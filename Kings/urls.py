from django.urls import path,include
from django.contrib import admin
from django.conf.urls.static import static
from django.conf import settings
# from . import views
# from . import views

# app_name = 'pizzapp'

urlpatterns = [
	path('admin/', admin.site.urls),
	path('',include('accounts.urls')),
    path('kingsapp/',include('kingsapp.urls')),
	path('pizzapp/',include('pizzapp.urls')),

    
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)