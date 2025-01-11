from django.conf import settings

from home.models import Contact
from items.models import Category
from orders.models import Order

paypal_client_id = settings.PAYPAL_CLIENT_ID


def add_variable_to_context(try_content=None):
    return {
        'gimsap_facebook': 'https://www.facebook.com/Gimsap-Markt-105253258056163',
        'gimsap_twitter': '',
        'gimsap_linkedin': '',
        'gimsap_instagram': 'https://www.instagram.com/gimsap.markt',
        'gimsap_pinterest': '',
        'Categorys': Category.objects.all(),
        'new_orders_count': Order.objects.filter(ordered=True, received=False).count(),
        'new_orders': Order.objects.filter(ordered=True, received=False)[:5],
        'contacts': Contact.objects.all().order_by('-id')[:5],
        'gimsap_email': 'online@gimsap.com',
        'paypal_client_id': paypal_client_id,
        'paypal_client_url': f"https://www.paypal.com/sdk/js?client-id={paypal_client_id}&currency=USD",
        'gimsap_phone_number': '587-997-4986',
        'gimsap_address': '1829 54 Street Southeast, Unit 107, Calgary AB, Canada',
    }
