from django.shortcuts import render, redirect
from django.db.models import Sum, Avg
from .models import PizzaSale, PizzaProfitData
from .forms import pizzaSaleDataForm, pizzaProfitDataForm
from datetime import datetime, date
from django.contrib import messages
from django.contrib.auth.decorators import login_required

# Create your views here.

@login_required(login_url='login')
def dashBoard(request):
	if request.method == 'POST':
		form = pizzaSaleDataForm(request.POST)
		if form.is_valid():
			sale_instance = form.save()
			return redirect('pizzapp:pizzaentry')
		else:
			print(form.errors)
	else:
		form = pizzaSaleDataForm()
	
	context = {'form': form}
	return render(request,'pizza/pizza_input.html',context)

@login_required(login_url='login')
def showdata(request):
    today = date.today()
    queryset = PizzaSale.objects.filter(create_date__month=today.month, create_date__year=today.year).order_by('create_date')
    
    total_fmp = queryset.aggregate(Sum('pizza_sale'))['pizza_sale__sum'] or 0
    total_fp = queryset.aggregate(Sum('fp_sale'))['fp_sale__sum'] or 0
    fp_net = float(total_fp) * 0.7978  # Deducting 20.22%
    
    grand_total = float(total_fmp) + float(total_fp)
    net_total = float(total_fmp) + fp_net
    avg_sale = queryset.aggregate(Avg('pizza_sale'))['pizza_sale__avg'] or 0 # Example calc

    current_day = queryset.last()
    current_day_total = 0
    if current_day:
        # Calculate daily total if total_sale property isn't defined on the model
        current_day_total = float(current_day.pizza_sale or 0) + float(current_day.fp_sale or 0)
    
    prev_month_total = 0 # Placeholder value

    context = {
        'showSaleData': queryset,
        'total_fmp_sale': total_fmp,
        'total_foodpanda_sale': total_fp,
        'foodpanda_net_sale': fp_net,
        'grand_total_sale': grand_total,
        'net_total_sale': net_total,
        'average_sale': avg_sale,
        'report_date': today,
        'chart_labels': [d.create_date.strftime('%d') for d in queryset],
        'chart_data': [float(d.pizza_sale) for d in queryset],
        'monthly_grand_total_data': [float(total_fmp)],
        'monthly_foodpanda_total_data': [float(total_fp)],
        'current_day_sales': current_day,
        'prev_month_sales': {'total_sale': prev_month_total, 'date': None},
        'sales_diff': current_day_total - prev_month_total,
    }
    return render(request, 'pizza/pizza_showdata.html', context)

@login_required(login_url='login')
def show_archive(request):
    # This would typically use a separate Archive model or aggregation
    archives = [] 
    return render(request, 'pizza/pizza_archive.html', {'archived_data': archives})

def psd(request):
    if request.method == 'POST':
        # Profit distribution logic
        messages.success(request, "Data added successfully.")
        return redirect('pizzapp:psd')
    
    profit_list = PizzaProfitData.objects.all().order_by('-month')
    return render(request, 'pizza/pizza_profit.html', {'kingsProfitDataList': profit_list})

def month_rpt(request, archive_id):
    return render(request, 'pizza/pizza_month_view.html')