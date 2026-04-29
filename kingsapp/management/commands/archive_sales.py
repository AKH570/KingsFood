from django.core.management.base import BaseCommand
from django.db.models import Sum, Count
from django.db import transaction
from datetime import date, datetime
from dateutil.relativedelta import relativedelta
from decimal import Decimal
from kingsapp.models import kingsSale, kingsArchvSummary, kingsSalesArchv

# run this command in terminal: python manage.py archive_sales --year 2025 --month 1
class Command(BaseCommand):
    """
    A Django management command to archive the sales summary for the previous month.
    This command is intended to be run automatically on the first day of each month
    via a cron job or a task scheduler.
    
    Example usage:
    - For previous month: python manage.py archive_sales
    - For a specific month: python manage.py archive_sales --year 2023 --month 9
    """
    help = 'Calculates and archives the sales summary for the previous month.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--year',
            type=int,
            help='The year to archive (e.g., 2023).'
        )
        parser.add_argument(
            '--month',
            type=int,
            help='The month to archive (1-12).'
        )

    def handle(self, *args, **kwargs):
        year = kwargs.get('year')
        month = kwargs.get('month')

        if year and month:
            try:
                target_date = date(year, month, 1)
            except ValueError:
                self.stderr.write(self.style.ERROR('Invalid year or month provided.'))
                return
        else:
            # Default to the previous month if no arguments are given
            target_date = date.today() - relativedelta(months=1)
        
        year, month = target_date.year, target_date.month

        self.stdout.write(f'Starting archival process for {target_date.strftime("%B %Y")}...')

        monthly_sales = kingsSale.objects.filter(create_date__year=year, create_date__month=month)

        if not monthly_sales.exists():
            # If no sales exist, ensure no archive record exists for it.
            deleted_count, _ = kingsArchvSummary.objects.filter(month__year=year, month__month=month).delete()
            if deleted_count > 0:
                self.stdout.write(self.style.WARNING(f'No sales data found for {target_date.strftime("%B %Y")}. Removed existing archive record.'))
            else:
                self.stdout.write(self.style.SUCCESS(f'No sales data found for {target_date.strftime("%B %Y")}. No archival needed.'))
            return

        with transaction.atomic():
            totals = monthly_sales.aggregate(
                total_fmp=Sum('FMP_sale'),
                total_foodpanda=Sum('foodpanda'),
                count=Count('id')
            )

            total_fmp = totals['total_fmp'] or 0
            total_foodpanda_gross = totals['total_foodpanda'] or 0
            commission_rate = Decimal('0.2022')
            foodpanda_commission = total_foodpanda_gross * commission_rate
            total_foodpanda_net = total_foodpanda_gross - foodpanda_commission
            grand_total = total_fmp + total_foodpanda_gross
            net_total_sale = total_fmp + total_foodpanda_net

            # Calculate the number of unique days with sales to get a true daily average
            days_with_sales = monthly_sales.values('create_date').distinct().count()
            average_daily_sale = grand_total / days_with_sales if days_with_sales > 0 else 0

            # Use update_or_create to handle both new and existing archive entries
            obj, created = kingsArchvSummary.objects.update_or_create(
                month=date(year, month, 1),
                defaults={
                    'total_fmp_sale': total_fmp,
                    'total_foodpanda_sale': total_foodpanda_gross,
                    'grand_total_sale': grand_total,
                    'net_total_sale': net_total_sale,
                    'average_daily_sale': average_daily_sale
                }
            )

            # Replication process: Move detailed records to Archive model
            archived_records = [
                kingsSalesArchv(
                    entity=sale.entity,
                    FMP_sale=sale.FMP_sale,
                    foodpanda=sale.foodpanda,
                    create_date=sale.create_date,
                ) for sale in monthly_sales
            ]
            kingsSalesArchv.objects.bulk_create(archived_records)

            # Delete original records from the live table
            moved_count, _ = monthly_sales.delete()
            self.stdout.write(self.style.SUCCESS(f'Moved {moved_count} detailed records to {kingsSalesArchv._meta.verbose_name}.'))

        if created:
            self.stdout.write(self.style.SUCCESS(f'Successfully created archive for {target_date.strftime("%B %Y")}.'))
        else:
            self.stdout.write(self.style.SUCCESS(f'Successfully updated archive for {target_date.strftime("%B %Y")}.'))