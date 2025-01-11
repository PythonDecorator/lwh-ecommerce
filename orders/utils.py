import uuid
import operator
from functools import reduce
import requests
from django.conf import settings
from django.db.models import Q

PAYPAL_CLIENT_ID = settings.PAYPAL_CLIENT_ID
PAYPAL_SECRET_KEY = settings.PAYPAL_SECRET_KEY
PAYPAL_URL = settings.PAYPAL_URL


# get paypal access token
def get_paypal_access_token():
    d = {"grant_type": "client_credentials"}
    h = {"Accept": "application/json", "Accept-Language": "en_US"}
    url = f"{PAYPAL_URL}v1/oauth2/token"
    r = requests.post(
        url,
        auth=(PAYPAL_CLIENT_ID,
              PAYPAL_SECRET_KEY),
        headers=h,
        data=d).json()
    return r.get('access_token')


def generate_client_token():
    access_token = get_paypal_access_token()
    headers = {"Content-Type": "application/json",
               "Authorization": f'Bearer {access_token}'}
    url = f"{PAYPAL_URL}v1/identity/generate-token"
    response = requests.request('POST', f"{url}", json={},
                                headers=headers)
    if response.status_code == 200:
        return response.json().get('client_token')
    return None


def create_paypal_order(amount):
    access_token = get_paypal_access_token()
    headers = {"Content-Type": "application/json",
               "Authorization": f'Bearer {access_token}'}
    url = f"{PAYPAL_URL}v2/checkout/orders"
    response = requests.request(
        'POST', f"{url}",
        json={
            "intent": "CAPTURE",
            "purchase_units": [
                {
                    "amount": {
                        "currency_code": "USD",
                        "value": float(amount)
                    },
                },
            ]
        },
        headers=headers)
    print(response.json())
    if response.json():
        return response.json()
    return None


def capture_paypal_order(orderId):
    access_token = get_paypal_access_token()
    headers = {"Content-Type": "application/json",
               "Authorization": f'Bearer {access_token}'}
    url = f"{PAYPAL_URL}v2/checkout/orders/{orderId}/capture"
    response = requests.request(
        'POST', f"{url}",
        json={},
        headers=headers)
    print(response.json())
    if response.json():
        return response.json()
    return None


def verify_paypal_payment(amount, _id):
    try:
        access_token = get_paypal_access_token()
        headers = {"Content-Type": "application/json",
                   "Authorization": f'Bearer {access_token}'}
        print('access token', access_token)
        response = requests.request('GET', f"{PAYPAL_URL}v2/checkout/orders/{_id}/", json={},
                                    headers=headers)
        print(response.json())
        if response.json().get('status') == 'COMPLETED' or response.json().get('status') == 'APPROVED':
            amount_details = response.json().get("purchase_units")[0].get('amount')
            print('the amount details', amount_details)
            # verify if the payment made is correct and check amount paid
            # minus one from our total because of some issues that might occur maybe .2 cent issue
            amount -= 1
            if float(amount_details.get('value')) >= amount and amount_details.get("currency_code") == "USD":
                return True
    except Exception as a:
        print(a)
        return False


def get_or_create_customer(request):
    """
    this merges the order once he logs in and when he hasn't added item to cart
    :return:  customer
    """
    from users.models import Customer
    from orders.models import OrderItem
    from orders.models import Wishlist

    device = request.COOKIES.get('gimsap_device')
    print("the device", device)

    if request.user.is_authenticated:
        customer = Customer.objects.filter(user=request.user).first()
        not_logged_in_customer = Customer.objects.filter(device=device).first()
        print("the customer device", customer)
        print("the not_logged_in_customer ", not_logged_in_customer)
        if customer:
            if customer.device:
                if customer.device == device:
                    print("the logged_in_customer is equals the not logged in customer")
                    return customer
                if not_logged_in_customer and not_logged_in_customer.device and not_logged_in_customer.user is None:
                    print("the not_logged_in_customer device", not_logged_in_customer.device)
                    #  the reason why I am adding this is if the user create an account somewhere else
                    print("customer.order_set", customer.order_set)
                    print("not_logged_in_customer.device", not_logged_in_customer.device)
                    logged_in_customer_order = customer.order_set.filter(ordered=False).first()
                    not_logged_in_customer_order = not_logged_in_customer.order_set.filter(ordered=False).first()
                    # check if both has orders
                    if logged_in_customer_order and not_logged_in_customer_order:
                        # setting all not logged in customer order items to logged in customer items
                        for order_item in not_logged_in_customer_order.items.all():
                            if not logged_in_customer_order.items.filter(item=order_item.item).exists():
                                new_order_item = OrderItem.objects.create(
                                    item=order_item.item, customer=customer,
                                    quantity=order_item.quantity)
                                # add the newly created order item  the current user
                                logged_in_customer_order.items.add(new_order_item)
                                logged_in_customer_order.save()
                                # delete the order item that was used to create
                            order_item.delete()
                        # delete the current user order
                        not_logged_in_customer_order.delete()
                        # delete the not logged in customer
                        # adding wishlist item
                        not_logged_in_customer_wishlist = Wishlist.objects.filter(
                            customer=not_logged_in_customer).first()
                        logged_in_customer_wishlist = Wishlist.objects.filter(
                            customer=customer).first()
                        if not logged_in_customer_wishlist:
                            logged_in_customer_wishlist = Wishlist.objects.create(customer=customer)

                        if not_logged_in_customer_wishlist:
                            # filter not logges in customer wishlist
                            for not_logged_in_customer_wishlist_item in not_logged_in_customer_wishlist.items.all():
                                if not not_logged_in_customer_wishlist_item in logged_in_customer_wishlist.items.all():
                                    logged_in_customer_wishlist.items.add(not_logged_in_customer_wishlist_item)
                                    logged_in_customer_wishlist.save()
                            not_logged_in_customer_wishlist.delete()
                        not_logged_in_customer.delete()
                        # setting cookie device to be use in the frontend
                        request.COOKIES["gimsap_device"] = customer.device
                        print("Just returns the customer after adding all not loged in customer items to order",
                              customer)
                        return customer
                if customer:
                    print("return for logged in user")
                    return customer
            if not customer.device:
                customer.device = device
                customer.save()
                print("added the device to the customer", customer)
                return customer
        elif not customer and not_logged_in_customer is not None:
            if not_logged_in_customer.user is None:
                not_logged_in_customer.user = request.user
                not_logged_in_customer.save()
                return not_logged_in_customer
        else:
            customer = Customer.objects.filter(device=device, user=request.user).first()
            if not customer:
                customer = Customer.objects.create(device=device, user=request.user)
            print("Create customer for logged in user", customer)
            return customer
    if not request.user.is_authenticated:
        # for the first time we might not have the device id in our browser so i need to set something new
        if not device:
            device = str(uuid.uuid4()).replace("-", "")
            request.COOKIES['gimsap_device'] = device
        customer = Customer.objects.filter(device=device).first()
        if not customer:
            print("create customer for not logged in user")
            customer = Customer.objects.create(device=device)
            return customer
        print("rerun customer for not logged in user", customer)
        return customer


def order_query(query, order):
    # user order query
    query_list = []
    query_list += query.split()
    query_list = sorted(query_list, key=lambda x: x[-1])
    print(query_list)
    second_received = True
    first_received = False
    if query == 'received':
        print(query)
        second_received = True
        first_received = True
    query = reduce(
        operator.or_,
        (
            Q(ordered__icontains=query) |
            Q(delivery_method__icontains=query) |
            Q(ref_code__icontains=query) |
            Q(ref_code__contains=query) |
            Q(received__icontains=query) |
            Q(customer__user__email=query) |
            Q(customer__user__email__in=[query]) |
            Q(customer__first_name__icontains=query) |
            Q(customer__last_name__icontains=query) |
            Q(customer__device__startswith=query) |
            Q(customer__last_name__startswith=query) |
            Q(customer__first_name__startswith=query) |
            Q(customer__user__email__startswith=query) |
            Q(customer__order__received__exact=second_received) |
            Q(customer__order__received__exact=first_received)
            for x in query_list)
    )
    object_list = order.filter(query).distinct()
    return object_list
