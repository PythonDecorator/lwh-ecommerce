from django import forms

from users.models import Customer


class PaymentForm(forms.Form):
    stripeToken = forms.CharField(required=False)
    save = forms.BooleanField(required=False)
    use_default = forms.BooleanField(required=False)


class CustomerCheckoutForm(forms.ModelForm):
    first_name = forms.CharField(max_length=200)
    last_name = forms.CharField(max_length=200)
    phone_number = forms.CharField(max_length=20)

    class Meta:
        model = Customer
        fields = [
            'first_name',
            'last_name',
            'phone_number', ]


class CustomerForm(forms.ModelForm):
    first_name = forms.CharField(max_length=200)
    last_name = forms.CharField(max_length=200)
    phone_number = forms.CharField(max_length=20)

    class Meta:
        model = Customer
        fields = [
            'first_name',
            'last_name',
            'image',
            'phone_number', ]
