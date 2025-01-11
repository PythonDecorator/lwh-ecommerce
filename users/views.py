import json

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.shortcuts import render, redirect
# Create your views here.
from django.views import View

from orders.forms import AddressForm
from orders.models import Address
from orders.utils import get_or_create_customer
from users.forms import CustomerForm


class ProfilePageView(LoginRequiredMixin, View):
    def get(self, request):
        customer = get_or_create_customer(self.request)
        customer_form = CustomerForm(instance=customer)
        shipping_address, created = Address.objects.get_or_create(customer=customer)
        shipping_address_form = AddressForm(instance=shipping_address)
        return render(request, "user/profile.html",
                      {'customer_form': customer_form, 'customer': customer,
                       'shipping_address': shipping_address,
                       'shipping_address_form': shipping_address_form})

    def post(self, request, *args, **kwargs):
        customer = get_or_create_customer(self.request)
        shipping_address, created = Address.objects.get_or_create(customer=customer)
        shipping_address_form = AddressForm(request.POST, instance=shipping_address)

        customer_form = CustomerForm(request.POST, request.FILES or None, instance=customer)
        if customer_form.is_valid():
            customer_form.save()
            messages.success(request, "Profile was successfully updated")
        if shipping_address_form.is_valid():
            shipping_address_form.save()
            messages.success(request, "Shipping address was successfully updated")
        print(shipping_address_form.errors)
        return redirect('user:profile_page')


class UpdateUserProfileAPIView(View):
    def post(self, request, *args, **kwargs):
        data = dict(json.loads(request.body.decode("utf-8")))
        customer = get_or_create_customer(self.request)
        try:
            print('the posted data', data)

            customer.__dict__.update(data)
            print('saved')
            customer.save()
            return JsonResponse(status=200, data=data)
        except Exception as a:
            print(a)
            return JsonResponse(status=400, data=data)
