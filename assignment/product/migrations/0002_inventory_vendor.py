# -*- coding: utf-8 -*-
# Generated by Django 1.11.16 on 2018-11-11 18:50
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('product', '0001_initial'),
        ('vendor', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='inventory',
            name='vendor',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='vendor.Vendor'),
        ),
    ]
