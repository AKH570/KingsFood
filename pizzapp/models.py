from django.db import models

class PizzaSale(models.Model):
    entity = models.CharField(max_length=100)
    FMP_sale = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)
    foodpanda = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)
    create_date = models.DateField()

    @property
    def total_sale(self):
        return self.FMP_sale + self.foodpanda

    def __str__(self):
        return f"{self.entity} - {self.create_date}"

class PizzaProfitData(models.Model):
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Disbursed', 'Disburse'),
    ]
    month = models.DateField()
    totalProfitAmount = models.DecimalField(max_digits=15, decimal_places=2)
    distributionAmount = models.DecimalField(max_digits=15, decimal_places=2)
    disburseDate = models.DateField(null=True, blank=True)
    remarks = models.TextField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')

    def __str__(self):
        return f"Profit for {self.month.strftime('%B %Y')}"
    class Meta:
        verbose_name = 'Pizza Profit'
        verbose_name_plural = 'Pizza Profit'