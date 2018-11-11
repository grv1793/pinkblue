# -*- coding: utf-8 -*-
# Generated by Django 1.11.16 on 2018-11-11 18:50
from __future__ import unicode_literals

from django.conf import settings
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import django_fsm


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Batch',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Creation Date')),
                ('description', models.CharField(blank=True, max_length=100, null=True, verbose_name='Description')),
                ('number_of_entries', models.IntegerField(verbose_name='Num of entries')),
            ],
            options={
                'verbose_name': 'Batch',
                'verbose_name_plural': 'Batches',
            },
        ),
        migrations.CreateModel(
            name='Inventory',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('total_price', models.IntegerField(blank=True, null=True, verbose_name='MRP')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Creation Date')),
                ('modified_at', models.DateTimeField(blank=True, null=True, verbose_name='Modified Date')),
                ('quantity', models.PositiveIntegerField(blank=True, null=True, verbose_name='Quantity')),
                ('status', django_fsm.FSMField(db_index=True, default=b'pending', max_length=50)),
                ('batch', models.ForeignKey(blank=True, on_delete=django.db.models.deletion.PROTECT, to='product.Batch')),
                ('created_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='inventory_created_by', to=settings.AUTH_USER_MODEL)),
                ('modified_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='inventory_modified_by', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Inventory',
                'verbose_name_plural': 'Inventories',
            },
        ),
        migrations.CreateModel(
            name='SKU',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(db_index=True, max_length=64, unique=True, validators=[django.core.validators.RegexValidator(message='Only AlphaNumerics and , - _ are allowed', regex='^[-,_\\w]*$')], verbose_name='SKU')),
                ('total_quantity', models.PositiveIntegerField(default=0, verbose_name='Quantity available')),
                ('unit', models.CharField(choices=[('gm', 'in grams'), ('kg', 'in kilograms'), ('l', 'in litres'), ('ml', 'in mililitres')], max_length=50, verbose_name='SKU unit of measurement')),
                ('quantity', models.DecimalField(decimal_places=2, max_digits=20, verbose_name='SKU Quantity of measurement')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Creation Date Date')),
                ('created_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='sku_created_by', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'SKU',
                'verbose_name_plural': 'SKUs',
            },
        ),
        migrations.AddField(
            model_name='inventory',
            name='sku',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='product.SKU'),
        ),
    ]
