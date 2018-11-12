# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin
from django.utils import timezone

from product.models import SKU, Inventory, Batch
from product.forms import InventoryForm
from fsm_admin.mixins import FSMTransitionMixin
from django.db import transaction
from django.db.models import F
from product.constants import APPROVED


@admin.register(SKU)
class SKUAdmin(admin.ModelAdmin):
    list_display = ('get_name', 'total_quantity')

    def get_fieldsets(self, request, obj=None):
        fieldsets = (
            ('General', {
                'fields':
                    ('name', 'quantity', 'unit')
            }),
            ('Audit Log', {
                'fields': ('created_at', 'created_by'),
            }),
        )
        if obj:
            fieldsets[0][1]['fields'] += ('total_quantity', )

        return fieldsets

    def get_name(self, obj):
        return str(obj)

    def get_readonly_fields(self, request, obj=None):
        fields = ['created_at', 'created_by', 'total_quantity']
        if obj:
            fields += ['name', 'quantity', 'unit', 'total_quantity']
        return fields

    def save_model(self, request, obj, form, change):
        if not change:
            obj.created_by = request.user
        super(SKUAdmin, self).save_model(request, obj, form, change)


@admin.register(Inventory)
class InventoryAdmin(FSMTransitionMixin, admin.ModelAdmin):

    list_display = ('sku', 'status', 'quantity', 'batch',
                    'vendor', 'total_price', 'created_at')
    fsm_field = ['status', ]
    form = InventoryForm

    def get_readonly_fields(self, request, obj=None):
        return ['status', 'batch', 'created_at',
                'created_by', 'modified_at', 'modified_by']

    def get_fieldsets(self, request, obj=None):
        fieldsets = (
            ('General', {
                'fields':
                    ('vendor', 'sku', 'batch', 'status',
                        'quantity', 'total_price')
            }),
            ('Audit Log', {
                'fields': ('created_at', 'created_by',
                           'modified_at', 'modified_by'),
            }),
        )

        return fieldsets

    def save_model(self, request, obj, form, change):
        with transaction.atomic():
            if form.is_valid() and form.cleaned_data:
                new_sku = form.cleaned_data.get('sku')
                new_quantity = form.cleaned_data.get('quantity')
                old_obj = None

                if change:
                    old_obj = Inventory.objects.get(pk=obj.id)
                    obj.modified_by = request.user
                    obj.modified_at = timezone.now()
                else:
                    batch = Batch.objects.create(
                        number_of_entries=new_quantity
                    )
                    obj.batch = batch
                    obj.created_by = request.user
                if old_obj and old_obj.status == APPROVED:
                    old_sku = old_obj.sku
                    old_quantity = old_obj.quantity
                    SKU.objects.filter(pk=old_sku.id).update(
                        total_quantity=F('total_quantity') - old_quantity)
                    SKU.objects.filter(pk=new_sku.id).update(
                        total_quantity=F('total_quantity') + new_quantity
                    )
            super(InventoryAdmin, self).save_model(
                request, obj, form, change)
