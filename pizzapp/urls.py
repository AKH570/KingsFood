from django.urls import path
from pizzapp import views

app_name = 'pizzapp'

urlpatterns = [
    path('pizzaentry/', views.dashBoard, name='pizzaentry'),
    path('pizzasales/', views.showdata, name='pizzasales'),
    path('archive/', views.show_archive, name='show_archive'),
    path('month_rpt/<int:archive_id>/', views.month_rpt, name='month_rpt'),
    path('psd/', views.psd, name='psd'),
]