from requests import Response
from rest_framework import viewsets, status
from .models import Vendor, PurchaseOrder
from .serializers import VendorSerializer, PurchaseOrderSerializer


class VendorViewSet(viewsets.ModelViewSet):
    queryset = Vendor.objects.all()
    serializer_class = VendorSerializer

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.update_performance_metrics()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)


class PurchaseOrderViewSet(viewsets.ModelViewSet):
    queryset = PurchaseOrder.objects.all()
    serializer_class = PurchaseOrderSerializer

    def perform_create(self, serializer):
        instance = serializer.save()
        instance.vendor.update_performance_metrics()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def perform_update(self, serializer):
        instance = serializer.save()
        instance.vendor.update_performance_metrics()
        return Response(serializer.data)

    def perform_destroy(self, instance):
        vendor = instance.vendor
        instance.delete()
        vendor.update_performance_metrics()
        return Response(status=status.HTTP_204_NO_CONTENT)
