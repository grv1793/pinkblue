# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.utils.translation import ugettext_lazy as _
from django.db import models


class Vendor(models.Model):
    name = models.CharField(
        _('Name of Vendor'), unique=True, max_length=255, db_index=True)
    skus = models.ManyToManyField('product.SKU', related_name='skus')

    class Meta:
        verbose_name = _("Vendor")
        verbose_name_plural = _("Vendors")

    def __str__(self):
        return self.name
