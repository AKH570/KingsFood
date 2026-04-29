from django.db import models

class PizzaSale(models.Model):
    entity = models.CharField(max_length=100)
    pizza_sale = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)
    fp_sale = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)
    create_date = models.DateField()

    @property
    def total_sale(self):
        return self.pizza_sale + self.fp_sale

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


class pizzaArchvSummary(models.Model):
    month = models.DateField(unique=True)
    pizza_total_sale = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_foodpanda_sale = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    grand_total_sale = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    net_total_sale = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    average_daily_sale = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.month.strftime('%B %Y')

    class Meta:
        verbose_name = 'Pizza Archived Summary'
        verbose_name_plural = 'Pizza Archived Summary'

class pizzaSalesArchv(models.Model):
    entity = models.CharField(max_length=100)
    pizza_sale = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    fp_sale = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    create_date = models.DateField()
    update_date = models.DateTimeField(auto_now=True)

    @property
    def total_sale(self):
        return self.pizza_sale + self.fp_sale
    def __str__(self):
        return str(self.create_date)
    class Meta:
        verbose_name = 'Pizza Sale Archive'
        verbose_name_plural = 'Pizza Sale Archive'