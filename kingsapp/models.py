from django.db import models

# Create your models here.
class saleData(models.Model):
    entity = models.CharField(max_length=100)
    FMP_sale = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    foodpanda = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    create_date = models.DateField()
    update_date = models.DateTimeField(auto_now=True)

    @property
    def total_sale(self):
        return self.FMP_sale + self.foodpanda

    def __str__(self):
        return self.entity

    class Meta:
        verbose_name = 'Sale Data'
        verbose_name_plural = 'Sales Data'

class ArchivedSaleSummary(models.Model):
    month = models.DateField(unique=True)
    total_fmp_sale = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_foodpanda_sale = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    grand_total_sale = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    net_total_sale = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    average_daily_sale = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.month.strftime('%B %Y')

    class Meta:
        verbose_name = 'Archived Sale Summary'
        verbose_name_plural = 'Archived Sale Summaries'
class kingsProfitData(models.Model):
    month = models.DateField(unique=True)
    remarks = models.CharField(max_length=200, blank=True, null=True)
    totalProfitAmount   = models.DecimalField(max_digits=10, decimal_places=2, blank=True,null=True)
    distributionAmount = models.DecimalField(max_digits=10, decimal_places=2)
    disburseDate = models.DateField(blank=True, null=True)
    STATUS_CHOICES = [
        ('Given', 'Given'),
        ('Not Given', 'Not Given'),
    ]
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='Given',
        null=True,
        blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.month.strftime('%B %Y')

    class Meta:
        verbose_name = 'Kings Profit Data'
        verbose_name_plural = 'Kings Profit Data'


