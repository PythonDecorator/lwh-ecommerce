from django import forms

from home.models import Contact, Faq
from items.models import Review


class ContactForm(forms.ModelForm):
    class Meta:
        model = Contact
        fields = ['name', 'email', 'subject', 'message']


class DashboardContactForm(forms.Form):
    email = forms.EmailField(
        required=False,
        widget=forms.TextInput(
            attrs={'placeholder': 'Email not required if '
                                  'sending to all customers'}))
    subject = forms.CharField(max_length=50)
    all_customers = forms.BooleanField(required=False)
    message = forms.CharField()


class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['item', 'name', 'email', 'content']




class FaqForm(forms.ModelForm):
    class Meta:
        model = Faq
        fields = ['answer', 'question', ]
