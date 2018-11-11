# System and Django imports
from django import forms
from django.core.exceptions import ValidationError
from product.models import Inventory


class InventoryForm(forms.ModelForm):

    def clean(self, *args, **kwargs):
        if self.cleaned_data:
            vendor = self.cleaned_data.get('vendor')
            sku = self.cleaned_data.get('sku')

            if sku not in vendor.skus.all():
                raise ValidationError({
                    'sku': 'This SKU does not belong to the Vendor'
                })

    class Meta:
        model = Inventory
        fields = '__all__'
