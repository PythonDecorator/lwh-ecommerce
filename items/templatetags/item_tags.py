from django import template

register = template.Library()
from orders.models import Wishlist, Order


@register.filter(name='wishlist_item_count')
def wishlist_item_count(customer__device):
    """Removes all values of arg from the given string"""
    try:
        print("value passed", customer__device)
        wishlist = Wishlist.objects.filter(customer__device=customer__device).first()
        count = 0
        if wishlist:
            count = wishlist.items.all().count()
        return str(count)
    except:
        count = 0
    return str(count)


@register.filter(name='user_order_items')
def user_order_items(customer__device):
    """Removes all values of arg from the given string"""
    try:
        order = Order.objects.filter(customer__device=customer__device, ordered=False).first()
        if order:
            return order.items.all()
        return None
    except:
        return None


@register.filter(name='user_order')
def user_order(customer__device):
    """Removes all values of arg from the given string"""
    try:
        order = Order.objects.filter(customer__device=customer__device, ordered=False).first()
        if order:
            return order
        return None
    except:
        return None


@register.filter(name='user_order_total_amount')
def user_order_total_amount(customer__device):
    """Removes all values of arg from the given string"""
    try:
        order = Order.objects.filter(customer__device=customer__device, ordered=False).first()
        if order:
            return order.get_total
        return '0'
    except:
        return '0'


@register.filter(name='user_order_total_item_count')
def user_order_total_item_count(customer__device):
    """Removes all values of arg from the given string"""
    try:
        order = Order.objects.filter(customer__device=customer__device, ordered=False).first()
        if order:
            return order.get_total_item_count
        return 0
    except:
        return 0


@register.filter(name='user_order_has_coupon')
def user_order_has_coupon(customer__device):
    """Removes all values of arg from the given string"""
    try:
        order = Order.objects.filter(customer__device=customer__device, ordered=False).first()
        if not order:
            return None
        if order.coupon:
            return True
    except:
        return None


@register.simple_tag
def item_quantity(customer__device, item_id):
    """Removes all values of arg from the given string"""
    try:
        order = Order.objects.filter(customer__device=customer__device, ordered=False).first()
        order_item = order.items.filter(item_id=item_id).first()
        if order_item:
            return order_item.quantity
        else:
            return 0
    except:
        return 0


@register.simple_tag
def add_or_delete_tag(customer__device=None, item_id=None):
    """It returns add or delete just like an action for the wishlist to perform"""
    try:
        wishlist = Wishlist.objects.filter(customer__device=customer__device).first()
        wishlist_item = wishlist.items.filter(id=item_id).first()
        if wishlist_item:
            return 'delete'
        else:
            return 'add'
    except:
        return 'add'


@register.simple_tag
def wish_list_active(customer__device=None, item_id=None):
    """Removes all values of arg from the given string"""
    try:
        wishlist = Wishlist.objects.filter(customer__device=customer__device).first()
        wishlist_item = wishlist.items.filter(id=item_id).first()
        if wishlist_item:
            return 'active'
        else:
            return 'nt'
    except:
        return 'nt'


@register.simple_tag
def paginate_url(value, field_name, urlencode=None):
    url = "?{}={}".format(field_name,value )
    if urlencode:
        querystring = urlencode.split("&")
        filter_querystring = filter(lambda p: p.split("=")[0] != field_name, querystring)
        encoded_querystring = "&".join(filter_querystring)
        url = "{}&{}".format(url, encoded_querystring)
        print(url)
    return url
