from django.urls import path,include
from rest_framework import routers
from autdetect import views
from rest_framework.documentation import include_docs_urls
router = routers.DefaultRouter()
router.register(r'psychologist',views.PsychologistView, 'psychologist')
router.register(r'infantpatient',views.InfantPatientView, 'infantpatient')
router.register(r'questionnaire',views.QuestionnaireView, 'questionnaire')
urlpatterns = [
    path('api/v1/',include(router.urls)),
    path('docs/',include_docs_urls(title = "Autdetect API")),
    path('api/v1/patients_by_month/', views.patients_by_month, name='patients_by_month'),
    path('api/v1/patients_by_month_autism/', views.patients_by_month_autism, name='patients_by_month_autism'),
    path('api/v1/patients_by_gender/', views.patients_by_gender, name='patients_by_gender'),
]