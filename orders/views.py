import json
from uuid import uuid4

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
# Create your views here.
from django.urls import reverse_lazy
from django.utils import timezone
from django.views import View
from django.views.generic import ListView, DeleteView

from dashboard.mixins import StaffAndLoginRequiredMixin
from users.forms import CustomerCheckoutForm
from .forms import AddressForm, OrderForm, PaymentForm, PickupForm, ShippingRoutineForm
from .models import Pickup, ShippingRoutine, Payment
from .models import Wishlist, Item, Order, Address, Coupon, OrderItem
from .tasks import successful_order_message_for_pickup, successful_order_message_for_shipping
from .utils import generate_client_token, create_paypal_order, capture_paypal_order, get_or_create_customer, order_query


# this view create the order from PayPal
class CreatPaypalOrderView(View):
    def post(self, request):
        customer = get_or_create_customer(self.request)

        order = Order.objects.filter(customer=customer).first()
        if not order:
            return JsonResponse(data={"Message": "You have no order"}, status=400)
        order_response = create_paypal_order(order.get_total)
        return JsonResponse(data=order_response, status=200)


# Used to capture order like making payment after order was successful
class CapturePaypalOrderView(View):
    def post(self, request):
        order_id = request.POST.get("id")
        capture_response = capture_paypal_order(order_id)
        return JsonResponse(data=capture_response, status=200)


class WishListView(View):
    def get(self, request, *args, **kwargs):
        customer = get_or_create_customer(self.request)

        wishlist, created = Wishlist.objects.get_or_create(customer=customer)
        items = wishlist.items.all()
        page = request.GET.get('page', 1)
        paginator = Paginator(items, 15)
        try:
            items = paginator.page(page)
        except PageNotAnInteger:
            items = paginator.page(1)
        except EmptyPage:
            items = paginator.page(paginator.num_pages)
        return render(request, "order/wishlist.html", {'wishlist': wishlist, 'items': items})

    def post(self, request):
        customer = get_or_create_customer(self.request)
        data = {}
        if request.POST.get('id') and request.POST.get('action'):
            id = request.POST.get('id')
            action = request.POST.get('action')
            reload = True
        else:
            data = dict(json.loads(request.body.decode("utf-8")))
            id = data.get('id')
            action = data.get('action')
            reload = False
        wishlist, created = Wishlist.objects.get_or_create(customer=customer)
        item = Item.objects.filter(id=id).first()
        data['wishlist_item_count'] = wishlist.items.count()
        if not item:
            print('no item')
            messages.warning(
                self.request, "Product does not exist")
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
        if action == 'add':
            print('added')
            if item in wishlist.items.all():
                wishlist.items.remove(item)
            else:
                wishlist.items.add(item)
            wishlist.save()
            data['wishlist_item_count'] = wishlist.items.count()
        elif action == 'delete':
            print('deleted')
            if not item in wishlist.items.all():
                wishlist.items.add(item)
            else:
                wishlist.items.remove(item)
            wishlist.save()
            data['wishlist_item_count'] = wishlist.items.count()
        if reload:
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
        return JsonResponse(status=200, data=data)


class CheckoutView(View):
    def get(self, request, *args, **kwargs):
        customer = get_or_create_customer(self.request)
        address, created = Address.objects.get_or_create(customer=customer)
        order = Order.objects.filter(customer=customer, ordered=False).first()
        if not order:
            order = Order.objects.create(customer=customer, ordered=False, shipping_address=address)
        address_form = AddressForm(instance=address)
        customer_form = CustomerCheckoutForm(instance=customer)
        pickup = Pickup.objects.all()
        shipping_routine = ShippingRoutine.objects.all()
        return render(request, "order/checkout.html",
                      {
                          'order': order,
                          'customer_form': customer_form,
                          'items': order.items.all(),
                          'pickup': pickup,
                          'shipping_routine': shipping_routine,
                          'address_form': address_form})

    def post(self, request, *args, **kwargs):
        customer = get_or_create_customer(self.request)

        order = Order.objects.filter(customer=customer, ordered=False).first()
        if not order:
            order = Order.objects.create(customer=customer, ordered=False)
        address, created = Address.objects.get_or_create(customer=customer)
        address_form = AddressForm(request.POST, instance=address)
        customer_form = CustomerCheckoutForm(request.POST, request.FILES or None, instance=customer)
        if request.POST.get('delivery_method'):
            order_form = OrderForm(request.POST, instance=order)
            # only needed the shipping method
            if order_form.is_valid():
                order_form.save()
                print('address_form  saved')
        if address_form.is_valid():
            address_form.save()
            print('address_form  saved')
            print(address_form.cleaned_data)
        if customer_form.is_valid():
            print(customer_form.cleaned_data)
            customer_form.save()
            print('customer_form  saved')
        print('address_form form error ', address_form.errors)
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


class ApplyCouponView(View):

    def post(self, request):
        customer = get_or_create_customer(self.request)

        coupon_code = request.POST.get('coupon_code')
        order = Order.objects.filter(customer=customer, ordered=False).first()
        if not order:
            order = Order.objects.create(customer=customer, ordered=False)
        coupon = Coupon.objects.filter(code=coupon_code).first()
        if not coupon:
            messages.info(request, "Invalid Coupon code")
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
        if customer in coupon.customers.all():
            messages.info(request, "Coupon has already used by you.")
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
        if float(order.get_total) < coupon.order_price:
            messages.info(request, f"Please order item above {coupon.order_price} to use this coupon")
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
        order.coupon = coupon
        order.save()
        coupon.customers.add(customer)
        coupon.save()
        messages.success(request, "Coupon was Successfully Applied")
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


class MakePaymentView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        customer = get_or_create_customer(self.request)
        order = Order.objects.filter(customer=customer, ordered=False, id=kwargs.get('id')).first()
        if not order:
            messages.warning(request, 'You dont have an active order. ')
            return redirect('home:home_page')
        if order.get_total <= 0:
            messages.warning(request, 'You dont have item in your cart.')
            return redirect('home:home_page')

        if order.delivery_method == 'SHIPPING':
            if not order.shipping_address:
                if (order.shipping_address.street_address is None or
                        order.shipping_address.country is None or
                        order.shipping_address.state is None or
                        order.shipping_address.apartment_address is None or
                        order.shipping_address.shipping_routine is None or
                        order.shipping_address.zip_code is None):
                    messages.warning(request, 'Please update your shipping address.')
                return redirect('order:checkout')
        if order.delivery_method == 'PICKUP':
            if not order.pickup_address:
                messages.warning(request, 'Please update your pickup address.')
                return redirect('order:checkout')
        if order.customer.last_name is None or order.customer.last_name is None or order.customer.phone_number is None:
            messages.warning(request, "Please update your profile info")
            return redirect('order:checkout')
        return render(request, 'order/make_payment.html', {
            'order': order,
            'client_token': generate_client_token()
        })

    def post(self, request, *args, **kwargs):
        customer = get_or_create_customer(self.request)

        """Validation order before payment is being processed"""
        order = Order.objects.filter(customer=customer, ordered=False, id=kwargs.get('id')).first()
        if not order:
            print('you dont have an active order', order)
            messages.warning(request, 'You dont have an active order. ')
            return redirect('home:home_page')
        if order.get_total <= 0:
            messages.warning(request, 'You dont have item in your cart.')
            return redirect('home:home_page')

        if order.delivery_method == 'SHIPPING':
            if not order.shipping_address:
                messages.warning(request, 'Please update your shipping address.')
                return redirect('order:checkout')
        if order.delivery_method == 'PICKUP':
            if not order.pickup_address:
                messages.warning(request, 'Please update your pickup address.')
                return redirect('order:checkout')
        print(request.POST)
        form = PaymentForm(self.request.POST)
        if form.is_valid():
            payment_id = form.cleaned_data.get('payment_id')
            payment_info = form.cleaned_data.get('payment_info')
            try:
                # create the payment model for the order
                payment = Payment()
                payment.payment_id = payment_id
                payment.payment_info = payment_info
                payment.user = self.request.user
                payment.amount = order.get_total
                payment.save()
                print('payment was saved')
                # loop through order items and update them to ordered
                order_items = order.items.all()
                order_items.update(ordered=True)
                for item in order_items:
                    item.save()
                order.ordered = True
                order.payment = payment
                order.ordered_date = timezone.now()
                order.ref_code = str(uuid4()).replace("-", "")
                order.save()
                print('item ')
                try:
                    if order.delivery_method == 'PICKUP':
                        # sending email as task
                        successful_order_message_for_pickup(
                            order.customer.user.email,
                            order.customer.first_name,
                            order.customer.last_name,
                            order.ref_code,
                            order.get_total,
                            order.pickup_address.name,
                            order.pickup_address.location,
                        )
                    if order.delivery_method == 'SHIPPING':
                        # sending email as task to make the page fast using celery
                        successful_order_message_for_shipping(
                            email=order.customer.user.email,
                            first_name=order.customer.first_name,
                            last_name=order.customer.last_name,
                            phone_number=order.customer.phone_number,
                            ref_code=order.ref_code,
                            price=order.get_total,
                            country=order.shipping_address.country,
                            state=order.shipping_address.state,
                            apartment_address=order.shipping_address.apartment_address,
                            zip_code=order.shipping_address.zip_code,
                            routine=order.shipping_address.shipping_routine.routine,
                            routine_price=order.shipping_address.shipping_routine.price,
                        )
                except Exception as a:
                    print("Cant send mail", a)
                messages.success(self.request, "Your order was successful!")
                return HttpResponseRedirect(order.get_absolute_url())
            except Exception as e:
                # email ourselves
                print('the error', e)
                messages.warning(
                    self.request, "A serious error occurred. We have been notified.")
                return redirect("order:checkout")

        messages.warning(self.request, "Invalid data received")
        return redirect("order:checkout")


class OrderHistoryListView(LoginRequiredMixin, ListView):
    model = Order
    template_name = 'order/order_history.html'
    paginate_by = 15

    def get_queryset(self):
        customer = get_or_create_customer(self.request)
        return Order.objects.filter(customer=customer, ordered=True)


class OrderHistoryDetailView(LoginRequiredMixin, View):

    def get(self, request, *args, **kwargs):
        customer = get_or_create_customer(self.request)

        order = get_object_or_404(Order, id=kwargs['id'], customer=customer, ordered=True)
        return render(request, 'order/order_history_detail.html', {'order': order})


class AddToCartView(View):

    def post(self, request, *args, **kwargs):
        data = dict(json.loads(request.body.decode("utf-8")))
        item_count = int(data.get('item_count'))
        item_id = int(data.get('item_id'))
        customer = get_or_create_customer(self.request)

        if isinstance(item_id, int):
            item = Item.objects.filter(id=item_id).first()
            if not item:
                return JsonResponse(status=404, data={'message': 'item does not exist'})
            order_item = OrderItem.objects.filter(customer=customer, item=item, ordered=False).first()
            if not order_item:
                order_item = OrderItem.objects.create(customer=customer, ordered=False, item=item)
            order_qs = Order.objects.filter(customer=customer, ordered=False)
            if order_qs.exists():
                order = order_qs[0]
                data['total_item_count'] = order.get_total_item_count
                data['total_item_amount'] = order.get_total
                # check if the order item is in the order
                if order.items.filter(item__slug=item.slug).exists():
                    order_item.quantity = item_count
                    print('current quantity', order_item.quantity)
                    order_item.save()
                    order.save()
                    data['item_count'] = order_item.quantity
                    data['order_item_price'] = order_item.get_final_price
                    data['order_item_id'] = order_item.id
                    data['total_item_count'] = order.get_total_item_count
                    data['total_item_amount'] = order.get_total
                    print('total amount', order.get_total)
                    print('the data', data)
                    return JsonResponse(status=200, data=data)
                else:
                    order.items.add(order_item)
                    data['item_count'] = order_item.quantity
                    data['order_item_price'] = order_item.get_final_price
                    data['order_item_id'] = order_item.id
                    data['total_item_count'] = order.get_total_item_count
                    data['total_item_amount'] = order.get_total
                    print('added new item', data)
                    return JsonResponse(status=200, data=data)
            else:
                ordered_date = timezone.now()
                order = Order.objects.create(
                    customer=customer, ordered_date=ordered_date)
                order.items.add(order_item)
                order.save()
                data['item_count'] = order_item.quantity
                data['order_item_price'] = order_item.get_final_price
                data['order_item_id'] = order_item.id
                data['total_item_count'] = order.get_total_item_count
                data['total_item_amount'] = order.get_total
                print("Create new order item", data)
        return JsonResponse(status=200, data=data)


class RemoveSingleFromCart(View):
    def post(self, request, *args, **kwargs):
        customer = get_or_create_customer(self.request)

        data = dict(json.loads(request.body.decode("utf-8")))
        item = get_object_or_404(Item, id=data.get('item_id'))
        item_count = int(data.get('item_count'))

        order_qs = Order.objects.filter(
            customer=customer,
            ordered=False
        )
        if order_qs.exists():
            order = order_qs[0]
            # check if the order item is in the order
            data['total_item_count'] = order.get_total_item_count
            data['total_item_amount'] = order.get_total
            if order.items.filter(item__slug=item.slug).exists():
                order_item = OrderItem.objects.filter(
                    item=item,
                    customer=customer,
                    ordered=False
                ).first()
                if order_item.quantity > 1:
                    order_item.quantity = item_count
                    print('current quantity', order_item.quantity)
                    order_item.save()
                    order.save()
                    data['item_count'] = order_item.quantity
                    data['order_item_price'] = order_item.get_final_price
                    data['order_item_id'] = order_item.id
                    data['total_item_count'] = order.get_total_item_count
                    data['total_item_amount'] = order.get_total
                else:
                    order.items.remove(order_item)
                    order.save()
                    data['total_item_count'] = order.get_total_item_count
                    data['total_item_amount'] = order.get_total
                    order_item.delete()
                return JsonResponse(status=200, data=dict(data))
            else:
                return JsonResponse(status=400, data={'message': 'This item was not in your cart'})
        else:
            return JsonResponse(status=400, data={'message': 'This item was not in your cart'})


class RemoveFromCartView(View):
    def post(self, request, *args, **kwargs):
        customer = get_or_create_customer(self.request)

        item_id = request.POST.get('item_id')
        item = get_object_or_404(Item, id=item_id)
        order_qs = Order.objects.filter(
            customer=customer,
            ordered=False
        )
        if order_qs.exists():
            order = order_qs[0]
            # check if the order item is in the order
            if order.items.filter(item__slug=item.slug).exists():
                order_item = OrderItem.objects.filter(
                    item=item,
                    customer=customer,
                    ordered=False
                ).first()
                if order_item:
                    order.items.remove(order_item)
                    order_item.delete()
                    messages.info(request, "This item was removed from your cart.")
                return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
            else:
                messages.info(request, "This item was not in your cart")
                return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
        else:
            messages.info(request, "You do not have an active order")
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


class ChangePickUpLocationView(View):
    def post(self, request, *args, **kwargs):
        customer = get_or_create_customer(self.request)

        data = dict(json.loads(request.body.decode("utf-8")))
        item_id = data.get('item_id')
        if not item_id:
            return JsonResponse(status=400, data={'message': 'Please submit item id.'})
        order = Order.objects.get(customer=customer, ordered=False)
        if not order:
            return JsonResponse(status=400, data={'message': 'Order does not exist'})
        pickup = Pickup.objects.filter(id=item_id).first()
        if not pickup:
            return JsonResponse(status=400, data={'message': 'PickUp does not exist'})
        order.pickup_address = pickup
        order.save()
        return JsonResponse(status=200, data={})


class ChangeShippingRoutineView(View):
    def post(self, request, *args, **kwargs):
        customer = get_or_create_customer(self.request)

        data = dict(json.loads(request.body.decode("utf-8")))
        item_id = data.get('item_id')
        if not item_id:
            return JsonResponse(status=400, data={'message': 'Please submit item id.'})
        order = Order.objects.get(customer=customer, ordered=False)
        if not order:
            return JsonResponse(status=400, data={'message': 'Order does not exist'})
        shipping_routine = ShippingRoutine.objects.filter(id=item_id).first()
        if not shipping_routine:
            return JsonResponse(status=400, data={'message': 'shipping routine does not exist'})
        if not order.shipping_address:
            address, created = Address.objects.get_or_create(customer=customer)
            order.shipping_address = address
            order.save()
        order.shipping_address.shipping_routine = shipping_routine
        order.shipping_address.save()
        data = {
            'total_item_amount': order.get_total,
            'total_item_count': order.get_total_item_count,
        }
        return JsonResponse(status=200, data=data)


class UpdateShippingAddressView(View):
    def post(self, request, *args, **kwargs):
        customer = get_or_create_customer(self.request)

        data = dict(json.loads(request.body.decode("utf-8")))
        print('the posted data', data)
        shipping_address, created = Address.objects.get_or_create(customer=customer)
        try:
            shipping_address.__dict__.update(data)
            shipping_address.save()
            print('Was saved', shipping_address.get_full_address)
            return JsonResponse(status=200, data=data)
        except Exception as a:
            print('Shipping address error', a)
            return JsonResponse(status=400, data=data)


class OrderListView(StaffAndLoginRequiredMixin, ListView):
    model = Order
    paginate_by = 50
    context_object_name = "orders"
    template_name = "dashboard/orders/order_list.html"

    def get_queryset(self):
        query = self.request.GET.get('search')
        order = Order.objects.all()
        if query:
            object_list = order_query(query, order)
            return object_list
        else:
            object_list = Order.objects.all()
            return object_list


class OrderedOrderListView(StaffAndLoginRequiredMixin, ListView):
    model = Order
    paginate_by = 50
    context_object_name = "orders"
    template_name = "dashboard/orders/order_list.html"

    def get_queryset(self):
        query = self.request.GET.get('search')
        order = Order.objects.all()
        if query:
            object_list = order_query(query, order)
            return object_list
        else:
            object_list = Order.objects.filter(ordered=True)
            return object_list


class NotOrderedOrderListView(StaffAndLoginRequiredMixin, ListView):
    model = Order
    paginate_by = 50
    context_object_name = "orders"
    template_name = "dashboard/orders/order_list.html"

    def get_queryset(self):
        query = self.request.GET.get('search')
        order = Order.objects.all()
        if query:
            object_list = order_query(query, order)
            return object_list
        else:
            object_list = Order.objects.filter(ordered=False)
            return object_list


class OrderDetailUpdateView(StaffAndLoginRequiredMixin, View):

    def get(self, request, *args, **kwargs):
        id = kwargs['id']
        order = get_object_or_404(Order, id=id)
        form = OrderForm(instance=order)
        address_form = AddressForm(instance=order.shipping_address)
        return render(request, 'dashboard/orders/order_detail_update.html',
                      {'order': order, 'form': form, 'address_form': address_form})

    def post(self, request, *args, **kwargs):
        id = kwargs['id']
        order = get_object_or_404(Order, id=id)
        form = OrderForm(request.POST, instance=order)
        address_form = AddressForm(request.POST, instance=order.shipping_address)
        if form.is_valid():
            form.save()
        if order.delivery_method == "SHIPPING":
            if address_form.is_valid():
                address_form.save()
            print(address_form.errors)
        print(form.errors)
        messages.success(request, 'Order Address was successfully updated')
        return HttpResponseRedirect(order.get_dashboard_absolute_url())


class OrderDeleteView(StaffAndLoginRequiredMixin, DeleteView):
    model = Order
    success_url = reverse_lazy('order:dashboard_order_list')
    template_name = 'DashBoard/orders/order_delete.html'
    context_object_name = 'order'


class PickupCreateListView(StaffAndLoginRequiredMixin, View):

    def get(self, request, *args, **kwargs):
        form = PickupForm()
        page = self.request.GET.get('page')
        items = Pickup.objects.all()
        paginator = Paginator(items, 15)
        try:
            items = paginator.page(page)
        except PageNotAnInteger:
            items = paginator.page(1)
        except EmptyPage:
            items = paginator.page(paginator.num_pages)
        return render(request, 'dashboard/pickup/list_create.html',
                      {'form': form,
                       'items': items, })

    def post(self, request, *args, **kwargs):
        form = PickupForm(request.POST or None, request.FILES or None)
        if form.is_valid():
            form.save()
            messages.success(request, "Pickup created")
        else:
            messages.error(request, 'An error occurred')
        return redirect('order:dashboard_pickup_list_create')


class PickupDeleteView(StaffAndLoginRequiredMixin, DeleteView):
    model = Pickup
    success_url = reverse_lazy('order:dashboard_pickup_list_create')
    template_name = 'dashboard/pickup/pickup_delete.html'
    context_object_name = 'item'


class ShippingRoutineCreateListView(StaffAndLoginRequiredMixin, View):

    def get(self, request, *args, **kwargs):
        form = ShippingRoutineForm()
        page = self.request.GET.get('page')
        items = ShippingRoutine.objects.all()
        paginator = Paginator(items, 15)
        try:
            items = paginator.page(page)
        except PageNotAnInteger:
            items = paginator.page(1)
        except EmptyPage:
            items = paginator.page(paginator.num_pages)
        return render(request, 'dashboard/routine/list_create.html',
                      {'form': form,
                       'items': items, })

    def post(self, request, *args, **kwargs):
        form = ShippingRoutineForm(request.POST or None, request.FILES or None)
        if form.is_valid():
            form.save()
            messages.success(request, "ShippingRoutine created")
        else:
            messages.error(request, 'An error occurred')
        return redirect('order:dashboard_routine_list_create')


class ShippingRoutineDeleteView(StaffAndLoginRequiredMixin, DeleteView):
    model = ShippingRoutine
    success_url = reverse_lazy('order:dashboard_routine_list_create')
    template_name = 'dashboard/routine/routine_delete.html'
    context_object_name = 'item'
