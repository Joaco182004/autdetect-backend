from rest_framework import serializers
from .models import Psychologists
from .models import InfantPatient
from .models import Questionnaire
from django.contrib.auth.models import User

class PsychologistSerializer(serializers.ModelSerializer):
    class Meta:
        model = Psychologists
        fields = '__all__'

class InfantPatientSerializer(serializers.ModelSerializer):
    class Meta:
        model = InfantPatient
        fields = '__all__'

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password']
        extra_kwargs = {
            'password': {'write_only': True},
            'username': {'required': False, 'allow_blank': True}  # No requerido, permite estar en blanco
        }

    def validate_email(self, value):
        # Asegurar que el email sea único
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("This email is already in use.")
        return value

    def create(self, validated_data):
        validated_data['username'] = validated_data['email']  # Asigna email a username
        user = User(
            email=validated_data['email'],
            username=validated_data['email']
        )
        user.set_password(validated_data['password'])
        user.save()
        return user
    
class QuestionnaireSerializer(serializers.ModelSerializer):
    class Meta:
        model = Questionnaire
        fields = '__all__'