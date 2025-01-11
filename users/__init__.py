from allauth.account.signals import user_logged_in
from django.dispatch import receiver

from orders.utils import get_or_create_customer


@receiver(user_logged_in)
def on_login(sender, user, request, **kwargs):
    customer = get_or_create_customer(request)
    print('User just logged in....')
