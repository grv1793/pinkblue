# -*- coding: utf-8 -*-
import json
import operator
from datetime import timedelta
from functools import reduce
from django.db.models import Q, F
from django.db import transaction
from django.utils import timezone
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny

from product.serializers import InventorySerializer
from product.models import SKU, Inventory, Batch
from product.constants import APPROVED, PENDING

IST_OFFSET_HOURS = 5.5
DATE_FORMAT = "%d-%m-%Y"
# Create your views here.


class InventoryView(generics.ListCreateAPIView):
    # TODO
    permission_classes = (AllowAny, )
    serializer_class = InventorySerializer

    def get(self, request):
        response_data = ''
        status_code = status.HTTP_200_OK

        inventories = self.get_queryset()
        # using serializers
        # response_data = self.serializer_class(inventories, many=True).data
        response_data = self.get_inventory_data(inventories)

        return Response(status=status_code, data=response_data)

    def get_inventory_data(self, qs):
        response = []
        for obj in qs:
            obj_dict = {}
            obj_dict['sku'] = {
                'id': obj.sku_id,
                'name': str(obj.sku)
            }
            obj_dict['vendor'] = {
                'id': obj.vendor_id,
                'name': str(obj.vendor)
            }
            obj_dict['created_by'] = {
                'id': obj.created_by_id,
                'name': str(obj.created_by)
            }
            obj_dict['total_price'] = float(obj.total_price)
            obj_dict['created_at'] = (obj.created_at + timedelta(
                hours=IST_OFFSET_HOURS)).strftime(DATE_FORMAT)
            obj_dict['quantity'] = obj.quantity
            obj_dict['status'] = obj.status
            obj_dict['batch_id'] = obj.batch_id
            response.append(obj_dict)
        return response

    def get_queryset(self):
        query = self.get_query(self.request.query_params)
        print(query)
        return Inventory.objects.filter(query).select_related('sku', 'vendor')

    def get_query(self, params):
        _status = params.get('status', None)
        batch_id = params.get('batch_id', None)
        sku_id = params.get('sku_id', None)
        created_by_id = params.get('created_by_id', None)
        vendor_id = params.get('vendor_id', None)
        start = params.get('start', None)
        # ensures there is always something in query
        end = params.get('end', timezone.now().date())

        query = []
        if _status:
            statuses = _status.split(",")
            status_query = []
            if statuses:
                status_query.append(Q(status__in=statuses))
            query.append(reduce(operator.or_, status_query))
        if batch_id:
            query.append(Q(batch_id=batch_id))
        if sku_id:
            query.append(Q(sku_id=sku_id))
        if created_by_id:
            query.append(Q(created_by_id=created_by_id))
        if vendor_id:
            query.append(Q(vendor_id=vendor_id))
        if start:
            query.append(Q(created_at__date__gte=start))
        if end:
            query.append(Q(created_at__date__lte=end))
        return reduce(operator.and_, query)

    def post(self, request):
        try:
            records_data = json.loads(request.body)
        except:
            return Response(status=status.HTTP_400_BAD_REQUEST,
                            data='Data is tampered or invalid.')

        response_data = 'Creation Successful'
        status_code = status.HTTP_200_OK
        desc_batch = "Inventory Creation %s" % (
                     timezone.now().date().strftime(DATE_FORMAT))
        batch = Batch.objects.create(
            description=desc_batch, number_of_entries=0)
        records_list = []

        for record_data in records_data:
            sku_id = record_data.get('sku_id', None)
            vendor_id = record_data.get('vendor_id', None)
            batch_id = batch.id
            quantity = record_data.get('quantity', None)
            total_price = float(record_data.get('total_price', None))
            created_by_id = request.user.id
            created_at = timezone.now()
            _status = record_data.get('status', PENDING)

            records_list.append(
                Inventory(**{
                    'sku_id': sku_id,
                    'vendor_id': vendor_id,
                    'batch_id': batch_id,
                    'quantity': quantity,
                    'total_price': total_price,
                    'created_by_id': created_by_id,
                    'created_at': created_at,
                    'status': _status
                })
            )

        try:
            with transaction.atomic():
                self.create_records(records_list, batch)
        except:
            batch.delete()
            response_data = 'Creation Failed'
            status_code = status.HTTP_500_INTERNAL_SERVER_ERROR

        return Response(status=status_code, data=response_data)

    def create_records(self, records_list, batch):
        records = Inventory.objects.bulk_create(records_list)
        batch.number_of_entries = len(records)
        batch.save()


class ApproveInventory(generics.UpdateAPIView):
    # TODO
    # permission_classes = (IsStaff, )
    serializer_class = InventorySerializer

    def put(self, request, pk):
        data = request.data
        response_data = 'Updation Success'
        status_code = status.HTTP_200_OK

        inventory = Inventory.objects.filter(pk=pk).first()
        if not inventory:
            return Response(status=status.HTTP_400_BAD_REQUEST,
                            data='Updation Failed')

        new_sku_id = data.get('sku_id')
        new_quantity = data.get('quantity')
        action = data.get('action', PENDING)

        inventory.modified_by = request.user
        inventory.modified_at = timezone.now()

        with transaction.atomic():
            if inventory.status == APPROVED:
                old_sku_id = inventory.sku
                old_quantity = inventory.quantity
                SKU.objects.filter(pk=old_sku_id).update(
                    total_quantity=F('total_quantity') - old_quantity)
                SKU.objects.filter(pk=new_sku_id).update(
                    total_quantity=F('total_quantity') + new_quantity
                )
            if action == APPROVED:
                SKU.objects.filter(pk=inventory.sku_id).update(
                    total_quantity=F('total_quantity') + inventory.quantity
                )

        return Response(status=status_code, data=response_data)
