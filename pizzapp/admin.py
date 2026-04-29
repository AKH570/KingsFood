from django.contrib import admin
from .models import PizzaSale, PizzaProfitData

@admin.register(PizzaSale)
class PizzaSaleAdmin(admin.ModelAdmin):
    list_display = ('entity', 'create_date', 'pizza_sale', 'fp_sale')
    list_filter = ('create_date', 'entity')

@admin.register(PizzaProfitData)
class PizzaProfitAdmin(admin.ModelAdmin):
    list_display = ('month', 'distributionAmount', 'status', 'disburseDate')
    list_editable = ('status',)