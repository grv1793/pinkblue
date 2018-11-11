# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.utils.translation import ugettext_lazy as _
from django.db import models
from django.core.validators import RegexValidator
from django_fsm import FSMField, transition
from django.contrib.auth.models import User
from assignment.middleware import current_request
from django.utils import timezone
from product.transitions import can_approve_inventory
from django.db.models import F
from product.constants import PENDING, APPROVED


class Batch(models.Model):
    created_at = models.DateTimeField(_("Creation Date"), auto_now_add=True)
    description = models.CharField(_("Description"),
                                   max_length=100, null=True, blank=True)
    number_of_entries = models.IntegerField(_("Num of entries"))

    def __str__(self):
        return '%s' % self.pk

    class Meta:
        verbose_name = _("Batch")
        verbose_name_plural = _("Batches")


class SKU(models.Model):
    GRAMS = 'gm'
    KILOGRAMS = 'kg'
    LITRE = 'l'
    MILILITRE = 'ml'
    UNITS = (
        (GRAMS, _('in grams')),
        (KILOGRAMS, _('in kilograms')),
        (LITRE, _('in litres')),
        (MILILITRE, _('in mililitres')),
    )
    name = models.CharField(
        _("SKU"), max_length=64, unique=True, db_index=True,
        validators=[
            RegexValidator(
                regex=r'^[-,_\w]*$',
                message=_("Only AlphaNumerics and , - _ are allowed"))])
    total_quantity = models.PositiveIntegerField(
        _("Quantity available"), default=0)

    unit = models.CharField(
        _('SKU unit of measurement'), max_length=50, choices=UNITS
    )
    quantity = models.DecimalField(
        _('SKU Quantity of measurement'),
        max_digits=20, decimal_places=2)
    created_at = models.DateTimeField(_("Creation Date Date"), auto_now_add=True)
    created_by = models.ForeignKey(User, related_name='sku_created_by')

    class Meta:
        verbose_name = _("SKU")
        verbose_name_plural = _("SKUs")

    def __str__(self):
        return ('%s(%s %s) - [%s]') % (self.name, self.quantity,
                                       self.unit, self.total_quantity)


# Create your models here.
class Inventory(models.Model):

    sku = models.ForeignKey('SKU', on_delete=models.PROTECT)
    total_price = models.IntegerField(_("MRP"), null=True, blank=True)
    created_at = models.DateTimeField(_("Creation Date"), auto_now_add=True)
    created_by = models.ForeignKey(User, related_name='inventory_created_by')
    modified_at = models.DateTimeField(_("Modified Date"),
                                       blank=True, null=True)
    modified_by = models.ForeignKey(User, blank=True, null=True,
                                    related_name='inventory_modified_by')
    quantity = models.PositiveIntegerField(
        _("Quantity"), null=True, blank=True)
    status = FSMField(default=PENDING, protected=False, db_index=True)
    batch = models.ForeignKey(Batch, on_delete=models.PROTECT, blank=True)
    vendor = models.ForeignKey('vendor.Vendor', on_delete=models.PROTECT)

    @transition(
        field=status, source=PENDING,
        target=APPROVED,
        permission=can_approve_inventory,
    )
    def approve(self):
        self.modified_by = current_request().user
        self.modified_at = timezone.now()
        SKU.objects.filter(pk=self.sku_id).update(
            total_quantity=F('total_quantity') + self.quantity
        )

    class Meta:
        verbose_name = _('Inventory')
        verbose_name_plural = _('Inventories')
