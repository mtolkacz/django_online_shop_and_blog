from django.contrib import admin
from django.db.models import ForeignKey, ManyToOneRel, OneToOneField

from .models import (Order, OrderItem, Payment, PromoCode, PromoCodeUsage,
                     Shipment, ShipmentType)

MySpecialAdmin = lambda model: type('SubClass'+model.__name__, (admin.ModelAdmin,), {
    'list_display': [x.name for x in model._meta.fields],
    'list_select_related': [x.name for x in model._meta.fields if isinstance(x, (ManyToOneRel, ForeignKey, OneToOneField,))]
})

admin.site.register(PromoCode, MySpecialAdmin(PromoCode))
admin.site.register(PromoCodeUsage, MySpecialAdmin(PromoCodeUsage))
admin.site.register(Payment, MySpecialAdmin(Payment))
admin.site.register(Order, MySpecialAdmin(Order))
admin.site.register(OrderItem, MySpecialAdmin(OrderItem))
admin.site.register(Shipment, MySpecialAdmin(Shipment))
admin.site.register(ShipmentType, MySpecialAdmin(ShipmentType))
