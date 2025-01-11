from django import forms

from .models import Address, Order, DELIVERY_CHOICES, Coupon, Pickup, ShippingRoutine


class AddressForm(forms.ModelForm):
    class Meta:
        model = Address
        fields = [
            'country',
            'state',
            'street_address',
            'apartment_address',
            'zip_code', ]


class OrderForm(forms.ModelForm):
    delivery_method = forms.ChoiceField(choices=DELIVERY_CHOICES, required=False)

    class Meta:
        model = Order
        fields = [
            'delivery_method',
            'pickup_address',
            'ordered',
            'coupon',
            'received',
        ]


class StaffOrderForm(forms.ModelForm):
    delivery_method = forms.ChoiceField(choices=DELIVERY_CHOICES, required=False)

    class Meta:
        model = Order
        fields = [
            'ordered',
            'coupon',
            'received',
        ]


class PaymentForm(forms.Form):
    payment_id = forms.CharField()
    payment_info = forms.JSONField(required=False)


class CouponForm(forms.ModelForm):
    percent = forms.FloatField(max_value=100, min_value=1)

    class Meta:
        model = Coupon
        fields = ['code', 'percent','order_price', 'image']


class PickupForm(forms.ModelForm):
    class Meta:
        model = Pickup
        fields = ['name', 'location']


class ShippingRoutineForm(forms.ModelForm):
    class Meta:
        model = ShippingRoutine
        fields = ['routine', 'price']
