from django.conf import settings
from django.contrib.auth.models import User
from django.db import models
# Create your models here.
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.urls import reverse
from django.utils import timezone

from items.models import Item
from orders.utils import verify_paypal_payment
from users.models import Customer

DELIVERY_CHOICES = (
    ('PICKUP', 'PICKUP'),
    ('SHIPPING', 'SHIPPING'),
)

COUNTRY_CHOICES = (
    ('CANADA', 'CANADA'),
)


class ShippingRoutine(models.Model):
    routine = models.CharField(max_length=250)
    price = models.FloatField(default=10)

    class Meta:
        ordering = ['-id']


class Address(models.Model):
    customer = models.OneToOneField(Customer,
                                    on_delete=models.CASCADE)
    street_address = models.CharField(max_length=100)
    country = models.CharField(max_length=50, choices=COUNTRY_CHOICES)
    state = models.CharField(max_length=50)
    apartment_address = models.CharField(max_length=100)
    shipping_routine = models.ForeignKey(ShippingRoutine, on_delete=models.SET_NULL, null=True, blank=True)
    zip_code = models.CharField(max_length=100)

    class Meta:
        ordering = ['-id']

    def __str__(self):
        return str(f"{self.customer} --- {self.get_full_address}")

    @property
    def get_full_address(self):
        try:
            return str(
                f"Country: {self.country}, State: {self.state},  Street Address: {self.street_address},"
                f" Apartment Address: {self.apartment_address}")
        except:
            return str("")

    @property
    def get_routine(self):
        try:
            return str(f"Order at ${self.shipping_routine.price} Price within  ${self.shipping_routine.routine}")
        except:
            return str("")

    class Meta:
        verbose_name_plural = 'Addresses'


def user_address_receiver(sender, instance, created, *args, **kwargs):
    if created:
        user_address = Address.objects.create(customer=instance)


post_save.connect(user_address_receiver, sender=Customer)


class Pickup(models.Model):
    name = models.CharField(max_length=100)
    location = models.CharField(max_length=200)

    def __str__(self):
        return str(self.name)


class OrderItem(models.Model):
    customer = models.ForeignKey(Customer,
                                 on_delete=models.CASCADE)
    ordered = models.BooleanField(default=False)
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)

    class Meta:
        ordering = ['-id']

    def __str__(self):
        return f"{self.quantity} of {self.item.name}"

    def get_total_item_price(self):
        return round(self.quantity * self.item.price, 2)

    def get_total_discount_item_price(self):
        return round(self.quantity * self.item.discount_price, 2)

    def get_amount_saved(self):
        return round(self.get_total_item_price() - self.get_total_discount_item_price(), 2)

    @property
    def get_final_price(self):
        if self.item.discount_price:
            return self.get_total_discount_item_price()
        return round(self.get_total_item_price(), 2)


class Order(models.Model):
    customer = models.ForeignKey(Customer,
                                 on_delete=models.CASCADE)
    items = models.ManyToManyField(OrderItem)
    start_date = models.DateTimeField(auto_now_add=True)
    payment = models.ForeignKey(
        'Payment', on_delete=models.CASCADE, blank=True, null=True)
    coupon = models.ForeignKey(
        'Coupon', on_delete=models.SET_NULL, blank=True, null=True)
    ref_code = models.CharField(max_length=250, blank=True, null=True)
    shipping_address = models.ForeignKey('Address', on_delete=models.SET_NULL, null=True)
    pickup_address = models.ForeignKey('Pickup', on_delete=models.SET_NULL, null=True, blank=True)
    delivery_method = models.CharField(default='PICKUP', choices=DELIVERY_CHOICES, max_length=10, )
    ordered = models.BooleanField(default=False)
    received = models.BooleanField(default=False)
    ordered_date = models.DateTimeField(blank=True, null=True)
    timestamp = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['-ordered_date']

    '''
    1. Item added to cart
    2. Adding  address
    (Failed checkout)
    3. Payment
    (Preprocessing, processing, packaging etc.)
    4. Being delivered
    5. Received
    '''

    def __str__(self):
        return str(f"{self.customer} --- {self.ordered} -- {self.received} -- {self.ref_code}")

    def get_absolute_url(self):
        return reverse("order:order_history_detail", kwargs={
            'id': self.id
        })

    def get_dashboard_absolute_url(self):
        return reverse("order:dashboard_order_detail_update", kwargs={
            'id': self.id
        })

    def get_update_url(self):
        return reverse("order:dashboard_order_detail_update", kwargs={
            'id': self.id
        })

    def get_delete_url(self):
        return reverse("order:dashboard_order_delete", kwargs={
            'pk': self.id
        })

    @property
    def get_total(self):
        total = 0
        for order_item in self.items.all():
            total += order_item.get_final_price
        if self.coupon:
            if total > 0:
                percentage = (total * self.coupon.percent) / 100
                total -= percentage
        if self.delivery_method == 'SHIPPING':
            if self.shipping_address:
                if self.shipping_address.shipping_routine:
                    total += self.shipping_address.shipping_routine.price
        return round(total, 2)

    @property
    def get_sub_total(self):
        total = 0
        for order_item in self.items.all():
            total += order_item.get_final_price
        if self.coupon:
            if total > 0:
                percentage = (total * self.coupon.percent) / 100
                total -= percentage
        return round(total, 2)

    @property
    def get_total_item_count(self):
        total = 0
        for order_item in self.items.all():
            total += order_item.quantity
        return total


# deleting all order items on delete and also the payment made


@receiver(post_save, sender=Order, dispatch_uid="verify_payment")
def verify_payment(sender, instance, **kwargs):
    # verify payment by id and amount to prevent users from hacking
    if instance.ordered and instance.payment:
        if not instance.received:
            if not verify_paypal_payment(amount=instance.get_total, _id=instance.payment.payment_id):
                instance.ordered = False
                instance.save()


class Wishlist(models.Model):
    customer = models.OneToOneField(
        Customer,
        on_delete=models.CASCADE)
    items = models.ManyToManyField(Item)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-id']

    def __str__(self):
        return str(self.customer)


class Payment(models.Model):
    payment_id = models.CharField(max_length=50, unique=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.SET_NULL, blank=True, null=True)
    amount = models.FloatField()
    payment_info = models.JSONField(blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return str(self.user)


class Coupon(models.Model):
    customers = models.ManyToManyField(Customer, blank=True)
    code = models.CharField(max_length=15, unique=True)
    image = models.ImageField(blank=True, null=True, upload_to='coupon')
    order_price = models.FloatField(default=2000)
    percent = models.FloatField(max_length=2)

    class Meta:
        ordering = ['-id']

    @property
    def imageURL(self):
        try:
            if self.image:
                return self.image.url
        except:
            return None

    def __str__(self):
        return str(self.code)
