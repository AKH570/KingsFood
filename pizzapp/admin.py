from django.contrib import admin
from .models import PizzaSale, PizzaProfitData

@admin.register(PizzaSale)
class PizzaSaleAdmin(admin.ModelAdmin):
    list_display = ('entity', 'create_date', 'FMP_sale', 'foodpanda')
    list_filter = ('create_date', 'entity')

@admin.register(PizzaProfitData)
class PizzaProfitAdmin(admin.ModelAdmin):
    list_display = ('month', 'distributionAmount', 'status', 'disburseDate')
    list_editable = ('status',)