from django.contrib import messages
from django.contrib.auth.models import User
from django.core.paginator import PageNotAnInteger, Paginator, EmptyPage
from django.shortcuts import render, redirect
#  dashboard
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import DeleteView

from dashboard.mixins import StaffAndLoginRequiredMixin
from items.models import Item
from orders.forms import CouponForm
from orders.models import Order, Coupon


# Create your views here.


class DashBoardView(StaffAndLoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        new_orders = Order.objects.filter(ordered=True, received=False)
        items = Item.objects.all()
        active_items = Item.objects.active_items()
        in_active_items = Item.objects.active_items()
        most_viewed_item_qs = Item.objects.all().order_by('-view_count')
        if most_viewed_item_qs.exists():
            most_viewed_item = most_viewed_item_qs.first()
        else:
            most_viewed_item = 0
        new_orders_total = 0
        new_orders_sub_total = 0
        for item in new_orders:
            new_orders_total += item.get_total
        for item in new_orders:
            new_orders_sub_total += item.get_sub_total
        user_count = User.objects.all().count()

        return render(request, 'dashboard/index.html',
                      {
                          'new_orders_count': new_orders.count(),
                          'new_orders_total': int(new_orders_total),
                          'new_orders_sub_total': int(new_orders_sub_total),
                          'user_count': user_count,
                          'products_count': items.count,
                          'active_products_count': active_items.count,
                          'inactive_products_count': in_active_items.count,
                          'most_viewed_product': most_viewed_item,
                          'new_orders': Order.objects.filter(ordered=True, received=False).order_by('-id')[:5]
                      })


class CouponCreateListView(StaffAndLoginRequiredMixin, View):

    def get(self, request, *args, **kwargs):
        form = CouponForm()
        page = self.request.GET.get('page')
        items = Coupon.objects.all()
        paginator = Paginator(items, 15)
        try:
            items = paginator.page(page)
        except PageNotAnInteger:
            items = paginator.page(1)
        except EmptyPage:
            items = paginator.page(paginator.num_pages)
        return render(request, 'dashboard/coupon/list_create.html',
                      {'form': form,
                       'items': items, })

    def post(self, request, *args, **kwargs):
        form = CouponForm(request.POST or None, request.FILES or None)
        if form.is_valid():
            form.save()
            messages.success(request, "Coupon created")
        else:
            messages.error(request, 'An error occurred')
        return redirect('dashboard:coupon_create_list')


class CouponDeleteView(StaffAndLoginRequiredMixin, DeleteView):
    model = Coupon
    success_url = reverse_lazy('dashboard:coupon_create_list')
    template_name = 'dashBoard/coupon/coupon_delete.html'
    context_object_name = 'item'
