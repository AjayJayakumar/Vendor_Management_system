from datetime import timezone
from django.db import models

# Create your models here.


class Vendor(models.Model):
    name = models.CharField(max_length=100)
    contact_details = models.TextField()
    address = models.TextField()
    vendor_code = models.CharField(max_length=50, unique=True)
    on_time_delivery_rate = models.FloatField(default=0)
    quality_rating_avg = models.FloatField(default=0)
    average_response_time = models.FloatField(default=0)
    fulfillment_rate = models.FloatField(default=0)

    def __str__(self):
        return self.name

    def update_performance_metrics(self):
        # On-Time Delivery Rate
        completed_pos = self.purchaseorder_set.filter(status="completed")
        total_completed_pos = completed_pos.count()
        if total_completed_pos > 0:
            on_time_delivered_pos = completed_pos.filter(
                delivery_date__lte=timezone.now()
            ).count()
            self.on_time_delivery_rate = (
                on_time_delivered_pos / total_completed_pos
            ) * 100

        # Quality Rating Average
        completed_pos_with_rating = completed_pos.exclude(quality_rating__isnull=True)
        if completed_pos_with_rating.exists():
            self.quality_rating_avg = completed_pos_with_rating.aggregate(
                avg_rating=models.Avg("quality_rating")
            )["avg_rating"]

        # Average Response Time
        completed_pos_with_ack = completed_pos.exclude(acknowledgment_date__isnull=True)
        if completed_pos_with_ack.exists():
            response_times = [
                (po.acknowledgment_date - po.issue_date).total_seconds()
                for po in completed_pos_with_ack
            ]
            self.average_response_time = sum(response_times) / len(response_times)

        # Fulfillment Rate
        successful_pos = completed_pos.filter(quality_rating__isnull=False)
        total_pos = self.purchaseorder_set.count()
        if total_pos > 0:
            self.fulfillment_rate = (successful_pos.count() / total_pos) * 100

        self.save()


class PurchaseOrder(models.Model):
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE)
    po_number = models.CharField(max_length=50, unique=True)
    order_date = models.DateTimeField()
    delivery_date = models.DateTimeField()
    items = models.JSONField()
    quantity = models.IntegerField()
    status = models.CharField(max_length=50)
    quality_rating = models.FloatField(null=True, blank=True)
    issue_date = models.DateTimeField(auto_now_add=True)
    acknowledgment_date = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.po_number


class HistoricalPerformance(models.Model):
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE)
    date = models.DateTimeField()
    on_time_delivery_rate = models.FloatField()
    quality_rating_avg = models.FloatField()
    average_response_time = models.FloatField()
    fulfillment_rate = models.FloatField()

    def __str__(self):
        return f"{self.vendor} - {self.date}"
