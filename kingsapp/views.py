from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout
from django.http import HttpResponseForbidden, JsonResponse, HttpResponseBadRequest
from django.views.decorators.http import require_http_methods, require_GET
from django.views.decorators.csrf import csrf_exempt
from .forms import SaleDataForm, KingsProfitDataForm
from django.db.models import Sum, Count, Avg, F
from django.utils import timezone
from .models import kingsSale, kingsArchvSummary, kingsProfit, kingsSalesArchv
from datetime import datetime, date, timedelta
from decimal import Decimal
from django.db.models.functions import TruncMonth
from dateutil.relativedelta import relativedelta
from django.contrib import messages
import json
import calendar

# Create your views here.

@login_required(login_url='login')
def welcome(request):
    """Displays a welcome page after successful login."""
    return render(request, 'kings/welcome.html')

@login_required(login_url='login')
def dashBoard(request):
	if request.method == 'POST':
		form = SaleDataForm(request.POST)
		if form.is_valid():
			sale_instance = form.save()
			return redirect('entrypage')
		else:
			print(form.errors)
	else:
		form = SaleDataForm()
	
	context = {'form': form}
	return render(request,'kings/inputdata.html',context)

def get_day_sales(target_date):
    """
    Helper function to get sales for a specific day
    """
    today = date.today()
    if target_date.year == today.year and target_date.month == today.month:
        # Query live sales for the current month
        model_to_query = kingsSale
    else:
        # Query archived sales for past months
        model_to_query = kingsSalesArchv

    day_sales = model_to_query.objects.filter(
        create_date=target_date
    ).aggregate(
        total_sale=Sum(F('FMP_sale') + F('foodpanda'))
    )['total_sale'] or Decimal('0.00')
    return {
        'date': target_date,
        'total_sale': day_sales
    }

def get_previous_month_day(current_date):
    """
    Get the same day in the previous month, handling edge cases
    """
    first_day_of_month = current_date.replace(day=1)
    prev_month_last_day = first_day_of_month - timedelta(days=1)
    
    # If current day > last day of previous month, use last day of previous month
    if current_date.day > prev_month_last_day.day:
        return prev_month_last_day
    return prev_month_last_day.replace(day=current_date.day)

def calculate_monthly_projection(average_sale, report_date):
    """
    Calculates the projected total sales for the month based on the daily average.
    """
    _, total_days = calendar.monthrange(report_date.year, report_date.month)
    projection = Decimal(average_sale) * Decimal(total_days)
    return projection.quantize(Decimal('0.01'))

@login_required(login_url='login')
def showData(request):
	today = datetime.today()
	# Get the most recent sale entry to determine the report date
	last_entry = kingsSale.objects.order_by('-create_date').first()

	# Use the create_date from the last entry, or today's date if there are no sales
	report_date = last_entry.create_date if last_entry else today
	# Filter for records in the current month and year
	monthly_sales = kingsSale.objects.filter(
		create_date__year=report_date.year,
		create_date__month=report_date.month
	)

	# Calculate totals using aggregation
	totals = monthly_sales.aggregate(
		total_fmp=Sum('FMP_sale'),
		total_foodpanda=Sum('foodpanda'),
		count=Count('id')
	)

	# Get gross totals, handling None if no sales exist
	total_fmp = totals['total_fmp'] or 0
	total_foodpanda_gross = totals['total_foodpanda'] or 0

	# Calculate Foodpanda commission and net sale
	commission_rate = Decimal('0.22')
	foodpanda_commission = total_foodpanda_gross * commission_rate
	total_foodpanda_net = total_foodpanda_gross - foodpanda_commission

	# Calculate grand total, handling None if no sales exist
	grand_total = total_fmp + total_foodpanda_gross
	net_total_sale = total_fmp + total_foodpanda_net

	# Calculate average sale, avoiding division by zero
	average_sale = 0
	sale_count = totals.get('count', 0)
	if sale_count > 0:
		average_sale = grand_total / sale_count

	# Calculate the monthly projection
	projected_grand_total = calculate_monthly_projection(average_sale, report_date)

	# Get the most recent sale entry to find the last updated date
	last_entry = kingsSale.objects.order_by('-create_date').first()
	last_updated_date = last_entry.create_date if last_entry else None

	# --- Prepare Chart Data (Merging Archive and Live Data) ---
	# Fetch archived summaries for the year of report_date
	archived_summaries = kingsArchvSummary.objects.filter(month__year=report_date.year)
	
	# Create lookups for archived data
	archived_avgs = {s.month.month: float(s.average_daily_sale) for s in archived_summaries}
	archived_totals = {
		s.month.month: {
			'grand_total': float(s.grand_total_sale),
			'foodpanda_total': float(s.total_foodpanda_sale)
		} for s in archived_summaries
	}

	chart_labels = []
	chart_data = []
	monthly_grand_total_data = []
	monthly_foodpanda_total_data = []

	# Iterate through months up to report_date.month
	for month_num in range(1, report_date.month + 1):
		month_name = date(report_date.year, month_num, 1).strftime('%b %Y')
		chart_labels.append(month_name)
		
		if month_num == report_date.month:
			# Current live month data (calculated above)
			chart_data.append(float(average_sale))
			monthly_grand_total_data.append(float(grand_total))
			monthly_foodpanda_total_data.append(float(total_foodpanda_gross))
		else:
			# Archived month data
			chart_data.append(archived_avgs.get(month_num, 0.0))
			m_data = archived_totals.get(month_num, {'grand_total': 0.0, 'foodpanda_total': 0.0})
			monthly_grand_total_data.append(m_data['grand_total'])
			monthly_foodpanda_total_data.append(m_data['foodpanda_total'])

	# Get current day sales
	current_day_sales = get_day_sales(report_date)
	
	# Get previous month's same day sales
	prev_month_day = get_previous_month_day(report_date)
	prev_month_sales = get_day_sales(prev_month_day)

	context = {
		'showSaleData': monthly_sales.order_by('create_date'),
		'report_date': report_date,
		'total_fmp_sale': total_fmp, # Gross FMP sale
		'total_foodpanda_sale': total_foodpanda_gross, # Gross Foodpanda sale
		'foodpanda_commission': foodpanda_commission, # The calculated commission amount
		'foodpanda_net_sale': total_foodpanda_net, # Net Foodpanda sale after commission
		'grand_total_sale': grand_total,
		'average_sale': average_sale,
		'net_total_sale': net_total_sale,
		'projected_grand_total': projected_grand_total,
		'last_updated_date': last_updated_date,
		'chart_labels': chart_labels,
		'chart_data': chart_data,
		'monthly_grand_total_data': monthly_grand_total_data,
		'monthly_foodpanda_total_data': monthly_foodpanda_total_data,
		'current_day_sales': current_day_sales,
        'prev_month_sales': prev_month_sales,
	}
	return render(request,'kings/showdata.html',context)

@login_required(login_url='login')
def showArchive(request):
    """Displays the archived monthly sales summaries."""
    # Order by month to ensure the chart is chronological
    archived_data = kingsArchvSummary.objects.order_by('month')

    # Prepare data for Chart.js
    chart_labels = [item.month.strftime('%b %Y') for item in archived_data]
    # Use grand_total_sale for the chart's data points
    chart_data = [float(item.grand_total_sale) for item in archived_data]

    context = {
        # Reverse the data for the table display to show newest first
        'archived_data': reversed(archived_data),
        'chart_labels': chart_labels,
        'chart_data': chart_data,
    }
    return render(request, 'kings/archive_data.html', context)

@login_required(login_url='login')
def profitDistribution(request):
    # Get all kings profit data, ordered by month in descending order
    kings_profit_data = kingsProfit.objects.order_by('-month')
    
    if request.method == 'POST':
        form = KingsProfitDataForm(request.POST)
        # print("POST DATA:", request.POST)
        # print("Form valid?", form.is_valid())
        # print("Form errors ->", form.errors)
        
        if form.is_valid():
            try:
                print(f'form data: {form.cleaned_data}')
                month = form.cleaned_data['month']
                print(f'show the month{month}')
                # print(f"Checking for existing entry for month: {month}")
                if kingsProfit.objects.filter(month__year=month.year, month__month=month.month).exists():
                    messages.error(request, f'An entry for {month.strftime("%B %Y")} already exists.')
                else:
                    form.save()
                    messages.success(request, 'Profit data added successfully!')
                    return redirect('psd')
            except Exception as e:
                messages.error(request, f'Error saving data: {str(e)}')
        else:
            # Add form errors to messages
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{field}: {error}')
    else:
        form = KingsProfitDataForm()
    
    context = {
        'kingsProfitDataList': kings_profit_data,
        'form': form,
    }
    return render(request, 'kings/profit_distribution.html', context)

# ====== Month view report
@login_required(login_url='login')
def month_view_sale(request, pk):
    arcv_month = get_object_or_404(kingsArchvSummary, pk=pk)
    daily_sales = kingsSalesArchv.objects.filter(
        create_date__year=arcv_month.month.year,
        create_date__month=arcv_month.month.month
    ).order_by('create_date')
    
    return render(request, 'kings/month_view_sale.html', {'archive': arcv_month, 'daily_sales': daily_sales})
