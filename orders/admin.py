from django.contrib import admin

from .models import Wishlist, OrderItem, Order, Address, Pickup, Coupon, Payment, ShippingRoutine


class OrderConfig(admin.ModelAdmin):
    list_display = ['customer', 'start_date', 'ordered', 'received', "ordered_date"]
    search_fields = ['customer__first_name', 'customer__last_name', 'customer__user__email', 'ref_code',
                     'shipping_address__street_address', 'pickup_address__name', ]
    filter = ['customer__first_name', 'customer__last_name', 'customer__user__email',
              'shipping_address__street_address',
              'pickup_address__name']


admin.site.register(Order, OrderConfig)
admin.site.register(Wishlist)
admin.site.register(OrderItem)
admin.site.register(Address)
admin.site.register(Pickup)
admin.site.register(Coupon)
admin.site.register(Payment)
admin.site.register(ShippingRoutine)
