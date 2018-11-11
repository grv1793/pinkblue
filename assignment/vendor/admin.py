# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.contrib import admin
from vendor.models import Vendor


@admin.register(Vendor)
class VendorAdmin(admin.ModelAdmin):
    list_display = ('name', )
