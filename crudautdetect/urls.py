"""
URL configuration for crudautdetect project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
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
from django.contrib import admin
from django.urls import path,include,re_path
from autdetect import views
urlpatterns = [
    path('admin/', admin.site.urls),
    path('autdetect/',include('autdetect.urls')),
    path('login/', views.login, name='login'),
    path('register/', views.register, name='register'),
    path('activate/<str:activation_key>/', views.activate_account, name='activate_account'),
    path('changeemail/', views.change_email_verification, name='change_email_verification'),
    path('changeusername/', views.change_username, name='changeusername'),
    path('changepassword/', views.change_password, name='changepassword'),
    path('changepasswordemail/',views.change_password_email,name='changepasswordemail'),
    path('validatecode/',views.validate_code,name='validatecode'),
    path('reporte/', views.send_email_report, name='reporte'),
    path('model/',views.prediccion_view,name='model'),
    path('export-infant-patients/', views.export_infant_patients_excel, name='export_infant_patients_excel'),
    path('export-questionnaires/', views.export_questionnaires_excel, name='export_questionnaires_excel'),
]
