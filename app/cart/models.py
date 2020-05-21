import random
from django.db import models, transaction
from django.conf import settings
from products.models import Product, Category
from django.contrib.auth import get_user_model, signals
from django.contrib.sessions.models import Session
from djmoney.models.fields import MoneyField
from accounts.validators import ZipCodeValidator
from accounts.models import Voivodeship, Country
from django.utils import timezone
from .signals import shipment_pre_save
from django.db.models import signals


User = get_user_model()
MAX_ITEMS_IN_CART = 30


class OrderItem(models.Model):
    product = models.ForeignKey(Product, on_delete=models.PROTECT, null=True)
    date_added = models.DateTimeField(auto_now=True)
    date_ordered = models.DateTimeField(null=True)
    amount = models.IntegerField(default=1)
    price = MoneyField(max_digits=14, decimal_places=2, default_currency='USD', null=True)
    booked = models.BooleanField(default=False, null=False)

    def __str__(self):
        return self.product.name

    def is_discounted(self):
        return True if self.product.discounted_price else False

    def get_item_total_no_discount(self):
        return self.product.price * self.amount

    def get_item_total(self):
        return (self.product.discounted_price if self.product.discounted_price else self.product.price) * self.amount


class Order(models.Model):
    IN_CART = 1
    BOOKED = 2
    CONFIRMED = 3
    PAID = 4
    COMPLETED = 5
    STATUS = (
        (IN_CART, 'Products in cart - not booked yet'),
        (BOOKED, 'Stock booked'),
        (CONFIRMED, 'Confirmed by client'),
        (PAID, 'Paid - waiting for delivery'),
        (COMPLETED, 'Completed - Delivered to client'),
    )
    owner = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    ref_code = models.CharField(max_length=20, editable=False)
    is_ordered = models.BooleanField(default=False)
    items = models.ManyToManyField(OrderItem)
    # payment_details = models.ForeignKey(Payment, null=True)
    date_ordered = models.DateTimeField(auto_now=True)
    session_key = models.ForeignKey(Session, on_delete=models.CASCADE, null=True, editable=False)
    access_code = models.SmallIntegerField(null=True, blank=False, editable=False)
    confirmed = models.BooleanField(default=False, editable=False)
    booked = models.BooleanField(default=False, null=False, editable=False)
    status = models.PositiveSmallIntegerField(
        choices=STATUS,
        default=IN_CART,
    )

    # save email for client without account which don't want to create one
    email = models.EmailField(null=True)

    def delete_order(self, delete_booked=False):
        items = self.items.all()
        for item in items:
            if delete_booked:
                if item.booked:
                    item.product.undo_book()
            item.delete()
        self.delete()

    def get_cart_items(self):
        return self.items.all().order_by('id')

    def get_cart_total(self):
        return sum([(item.product.discounted_price if item.product.discounted_price else item.product.price)
                    * item.amount for item in self.items.all()])

    def get_cart_total_str(self):
        return str(self.get_cart_total().amount)

    def get_cart_currency(self):
        return self.get_cart_total().currency if self.get_cart_total().currency else 'USD'

    def get_cart_qty(self):
        return sum(item.amount for item in self.items.all())

    def book(self):
        items = self.items.all()
        for item in items:
            item.product.book(amount=item.amount)
        self.update_status(self.BOOKED)

    def __str__(self):
        return '{}'.format(self.ref_code)

    def confirm(self):
        self.confirmed = True
        self.status = self.CONFIRMED
        self.save(update_fields=['confirmed', 'status', ])

    def update_status(self, status):
        self.status = status
        self.save(update_fields=['status', ])

    def create_access_code(self):
        self.access_code = random.randint(1000, 9999)
        self.save(update_fields=['access_code'])

    def delete_access_code(self):
        self.access_code = None
        self.save(update_fields=['access_code'])


class ShipmentType(models.Model):
    name = models.CharField(max_length=50, blank=False, null=False)
    cost = MoneyField(max_digits=14, decimal_places=2, default_currency='USD', null=False)

    def __str__(self):
        return '{}'.format(self.name)


class Shipment(models.Model):
    NEW = 1
    IN_PREPARATION = 2
    SENT = 3
    DELIVERED = 4
    STATUS = (
        (NEW, 'New and before payment'),
        (IN_PREPARATION, 'Paid and during preparation'),
        (SENT, 'Sent to client'),
        (DELIVERED, 'Delivered to client'),
    )
    order = models.OneToOneField(Order, on_delete=models.CASCADE, null=True, editable=False)
    type = models.ForeignKey(ShipmentType, on_delete=models.CASCADE, null=True)
    cost = MoneyField(null=True, max_digits=14, decimal_places=2, default_currency='USD')
    email = models.EmailField(null=True, blank=True)
    first_name = models.CharField(max_length=50, blank=False, null=False)
    last_name = models.CharField(max_length=150, blank=False, null=False)
    city = models.CharField(max_length=50, blank=False, null=False)
    voivodeship = models.ForeignKey(Voivodeship, on_delete=models.SET_NULL, blank=False, null=True)
    country = models.ForeignKey(Country, on_delete=models.SET_NULL, blank=False, null=True)
    zip_code = models.CharField(max_length=6, validators=[ZipCodeValidator], blank=False, null=False)
    address_1 = models.CharField(max_length=100, blank=False, null=False)
    address_2 = models.CharField(max_length=100, blank=True, null=True)
    status = models.PositiveSmallIntegerField(
        choices=STATUS,
        default=NEW,
    )
    creationdate = models.DateTimeField(auto_now_add=True, editable=False)
    preparationdate = models.DateTimeField(null=True, blank=True, editable=False)
    sentdate = models.DateTimeField(null=True, blank=True, editable=False)
    delivereddate = models.DateTimeField(null=True, blank=True, editable=False)

    def save(self, *args, **kwargs):
        if self.type is None:
            try:
                self.type = ShipmentType.objects.get(name='DHL')
            except ShipmentType.DoesNotExist:
                self.type = ShipmentType.objects.first()  # not sure if acceptable such approach

        if self.cost is None:
            self.cost = self.type.cost

        if self.email is None:
            self.email = kwargs['email'] if 'email' in kwargs else None

        if self.order is None:
            self.order = kwargs['order'] if 'order' in kwargs else None

        if self.order is None:
            return False  # todo add exception

        now = timezone.now()
        if self.status == self.IN_PREPARATION:
            self.preparationdate = now
        elif self.status == self.SENT:
            self.sentdate == now
        elif self.status == self.DELIVERED:
            self.delivereddate == now

        super().save(*args, **kwargs)

    def __str__(self):
        return '{} - {}'.format(self.order.ref_code, self.get_status_display())


signals.pre_save.connect(shipment_pre_save, sender=Shipment)


class OrderAccess(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, null=True)
    session_key = models.ForeignKey(Session, on_delete=models.CASCADE, null=True, editable=False)


class Payment(models.Model):
    id = models.CharField(max_length=17, blank=False, null=False, editable=False, primary_key=True)
    order = models.ForeignKey(Order, on_delete=models.SET_NULL, null=True, editable=False)
    createdate = models.DateTimeField(null=True, blank=True, editable=False)
    updatedate = models.DateTimeField(null=True, blank=True, editable=False)
    status = models.CharField(max_length=10, blank=False, null=False, editable=False)
    value = MoneyField(null=True, max_digits=14, decimal_places=2, default_currency='USD')
    payer_id = models.CharField(max_length=15, blank=False, null=False, editable=False)
    email = models.EmailField(null=False, editable=False)
    given_name = models.CharField(max_length=30, blank=False, null=False, editable=False)
    surname = models.CharField(max_length=30, blank=False, null=False, editable=False)
