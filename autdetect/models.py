from django.utils import timezone
from datetime import timedelta

from django.db import models
from django.contrib.auth.models import User
# Create your models here.
class UserProfile(models.Model):
    user = models.OneToOneField(User,on_delete=models.CASCADE)
    activation_key = models.CharField(max_length=40, blank=True)
    key_expires = models.DateTimeField(default=timezone.now() + timedelta(minutes=15))


    def __str__(self):
        return self.user.username

    class Meta:
        verbose_name_plural=u'Perfiles de Usuario'

class Psychologists(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    full_name = models.CharField(max_length=200)
    dni = models.CharField(max_length=8)
    tuition_number = models.CharField(max_length=20)
    email = models.EmailField()

    def __str__(self):
        return self.full_name if self.full_name else ""

class InfantPatient(models.Model):
    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
    ]
    infant_dni = models.CharField(max_length=8, verbose_name="Infant DNI")
    infant_name = models.CharField(max_length=100, verbose_name="Infant's Full Name")
    birth_date = models.DateField(verbose_name="Birth Date")
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, verbose_name="Gender")
    guardian_dni = models.CharField(max_length=8, verbose_name="Guardian DNI")
    guardian_name = models.CharField(max_length=100, verbose_name="Guardian's Full Name")
    guardian_email = models.EmailField(verbose_name="Guardian's Email", blank=True)
    contact_phone = models.CharField(max_length=15, verbose_name="Contact Phone")
    district = models.CharField(max_length=255, verbose_name="Address")
    psychology = models.ForeignKey(Psychologists, on_delete=models.CASCADE, related_name='patients')
    def __str__(self):
        return f"{self.infant_name} ({self.guardian_name})"

    class Meta:
        verbose_name = "Infant Patient"
        verbose_name_plural = "Infant Patients"

class Questionnaire(models.Model):
    patient = models.OneToOneField(InfantPatient, on_delete=models.CASCADE, verbose_name="Infant Patient")
    question_1 = models.BooleanField(verbose_name="Question 1")
    question_2 = models.BooleanField(verbose_name="Question 2")
    result = models.BooleanField(verbose_name="Autism Diagnosis")
    probability = models.FloatField(verbose_name="Autism Probability")
    date_evaluation = models.DateField(verbose_name="Date of Evaluation", blank=True)

    def __str__(self):
        return f"Questionnaire for {self.patient.infant_name}"

    class Meta:
        verbose_name = "Questionnaire"
        verbose_name_plural = "Questionnaire"