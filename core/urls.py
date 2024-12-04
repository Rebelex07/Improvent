"""
URL configuration for myproject project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.urls import path
from .views import home, products, exit, register, scan_page, storage_page, sales_page, csv_to_qr, generar_pdf

urlpatterns = [
    path('', home, name='home'),
    path('products/', products, name='products'),
    path('logout/', exit, name='exit'),
    path('register/', register, name='register'),
    path('scan_page/', scan_page, name='scan_page'),
    path('storage_page/', storage_page, name='storage_page'),
    path('sales_page/', sales_page, name='sales_page'),
    path('csv_to_qr/', csv_to_qr, name='csv_to_qr'),
    path('generar_pdf/<int:cod_producto>/', generar_pdf, name='generar_pdf'),
]