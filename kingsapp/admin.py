from django.contrib import admin
from .models import saleData, ArchivedSaleSummary,kingsProfitData

# Customizing the SaleData admin view
class SaleDataAdmin(admin.ModelAdmin):
    list_display = ('entity', 'FMP_sale', 'foodpanda', 'total_sale', 'create_date')
    list_filter = ('create_date',)
    search_fields = ('entity',)
    date_hierarchy = 'create_date'
    ordering = ('-create_date',)
    list_per_page = 10

# Customizing the ArchivedSaleSummary admin view
class ArchivedSaleSummaryAdmin(admin.ModelAdmin):
    list_display = ('month', 'grand_total_sale', 'net_total_sale', 'average_daily_sale')
    ordering = ('-month',)


# Register your models here.
admin.site.register(saleData, SaleDataAdmin)
admin.site.register(ArchivedSaleSummary, ArchivedSaleSummaryAdmin)

@admin.register(kingsProfitData)
class KingsProfitDataAdmin(admin.ModelAdmin):
    list_display = ('month', 'remarks', 'totalProfitAmount', 'distributionAmount', 'disburseDate', 'status')
    list_filter = ('status', 'month')
    date_hierarchy = 'month'