from django.contrib import admin
from .models import Psychologists
from .models import InfantPatient
from .models import UserProfile
from .models import Questionnaire
# Register your models here.
admin.site.register(Psychologists)
admin.site.register(InfantPatient)
admin.site.register(UserProfile)
admin.site.register(Questionnaire)