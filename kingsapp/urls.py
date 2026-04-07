from django.urls import path
from kingsapp import views


urlpatterns = [
    path('', views.showData, name='index'),
    path('dashboard/', views.dashBoard, name='dashboard'),
    path('sale/showdata/', views.showData, name='showdata'),
    path('archive/', views.showArchive, name='show_archive'),
    path('month_rpt/<int:pk>/', views.month_view_sale, name='month_rpt'),
    path('psd/', views.profitDistribution, name='psd'),
]