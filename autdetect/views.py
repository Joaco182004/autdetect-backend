from django.utils import timezone
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render
from rest_framework import viewsets
from .serializer import PsychologistSerializer
from .models import Psychologists,UserProfile
from .serializer import UserProfileSerializer
from .serializer import InfantPatientSerializer
from .models import InfantPatient
from .serializer import QuestionnaireSerializer
from .models import Questionnaire
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .serializer import UserSerializer
from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.decorators import authentication_classes,permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from django.db.models.functions import ExtractMonth, ExtractYear
from django.db.models import Count, Case, When, IntegerField
from django.core.mail import send_mail
from django.core.mail import EmailMessage
from django.http import HttpResponse
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import inch
import os
import random
from django.conf import settings
# Create your views here.
from django.shortcuts import render, redirect
from django.utils.crypto import get_random_string
from django.urls import reverse
from django.http import HttpResponse
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
from reportlab.platypus import Table, TableStyle


def enviar_correo(user):
    activation_key = get_random_string(40)
    user_profile = UserProfile.objects.create(user=user, activation_key=activation_key)
    
    activation_url = f"http://localhost:5173/activate/{activation_key}"
    
    subject = "¡Bienvenido/a a AutDetect 🙌 ! Completa tu Registro"
    html_message = f"""
    <html>
    <head></head>
    <body>
    <p>Hola,{user.email}</p>
    <p>Gracias por unirte a <strong>AutDetect</strong>, la plataforma dedicada a la detección temprana de autismo. Nos alegra que formes parte de nuestra comunidad de profesionales comprometidos con el bienestar de los niños y sus familias. 😊</p>
    <p>Para completar tu registro, por favor sigue estos pasos:</p>
    <ol>
        <li><strong>Verifica tu correo electrónico</strong><br>
        Haz clic en el siguiente enlace para confirmar tu dirección de correo electrónico:  <a href="{activation_url}">Verificar correo</a>🔗</li>
        <li><strong>Explora nuestra aplicación web</strong><br>
        Navega por la aplicación web y sus diferentes funcionalidades para comenzar a utilizar la plataforma en tus evaluaciones. 🛠️</li>
    </ol>
    <p>Gracias por unirte a <strong>AutDetect</strong>!<br>
    Estamos emocionados de contar contigo en nuestra misión de hacer la diferencia. 🌟</p>
    <p>Atentamente,<br>
    <strong>AutDetect</strong><br>
    [autdetect@gmail.com] ✉️</p>
    </body>
    </html>
    """
    from_email = settings.DEFAULT_FROM_EMAIL
    recipient_list = [user.email]

    try:
        email = EmailMessage(
            subject=subject,
            body=html_message,
            from_email=from_email,
            to=recipient_list,
        )
        email.content_subtype = 'html'  # Importante para enviar HTML
        email.send()
    except Exception as e:
        print(f"Error al enviar correo: {e}")

@api_view(['GET'])
def activate_account(request, activation_key):
    activation_key = activation_key.rstrip('/')
    try:
        profile = UserProfile.objects.get(activation_key=activation_key)
        print(activation_key)
        if profile.key_expires < timezone.now():
            print(profile.key_expires)
            print(timezone.now())
            return HttpResponse('El enlace ha expirado.', status=400)
        user = profile.user
        user.is_active = True
        user.save()
        return HttpResponse('Cuenta activada con éxito. Puedes iniciar sesión.')
    except UserProfile.DoesNotExist:
        return HttpResponse('Enlace inválido.', status=400)

@api_view(['POST'])
def login(request):
    user = get_object_or_404(User, username=request.data['username'])

    if not user.is_active:
        return Response({"error": "El usuario no esta activo."}, status=status.HTTP_403_FORBIDDEN)
    if not user.check_password(request.data['password']):
        return Response({"error": "La contraseña es inválida."}, status=status.HTTP_400_BAD_REQUEST)

    token, created = Token.objects.get_or_create(user=user)
    serializer = UserSerializer(instance=user)

    return Response({"token": token.key, "user": serializer.data}, status=status.HTTP_200_OK)

@api_view(['POST'])
def register(request):
    username = request.data.get('email', '')
    # Buscar el usuario existente
    existing_user = User.objects.filter(username=username).first()

    if existing_user:
        if existing_user.is_active == False:
        # Si el usuario existe, eli inar usuario y psicólogo asociados
            Token.objects.filter(user=existing_user).delete()  # Eliminar el token existente
            Psychologists.objects.filter(user=existing_user).delete()  # Eliminar el psicólogo existente
            existing_user.delete() # Eliminar el usuario existente

    # Crear un nuevo usuario
    user_serializer = UserSerializer(data=request.data)
    if user_serializer.is_valid():
        user = user_serializer.save()
        user.set_password(request.data.get('password', ''))
        user.is_active = False  # Desactivar la cuenta hasta la verificación
        user.save()
    else:
        return Response(user_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # Crear un nuevo token para el usuario
    token, created = Token.objects.get_or_create(user=user)

    # Datos del psicólogo
    psychologist_data = {
        'user': user.id,
        'full_name': request.data.get('full_name', ''),
        'dni': request.data.get('dni', ''),
        'tuition_number': request.data.get('tuition_number', ''),
        'email': request.data.get('email', ''),
    }
    # Crear un nuevo psicólogo
    psychologist_serializer = PsychologistSerializer(data=psychologist_data)

    if psychologist_serializer.is_valid():
        psychologist_serializer.save()
        print(psychologist_data)
        enviar_correo(user)  # Enviar correo con el enlace de verificación
        return Response({
            'token': token.key,
            'user': user_serializer.data,
            'psychologist': psychologist_serializer.data
        }, status=status.HTTP_201_CREATED)
    else:
        return Response(psychologist_serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PsychologistView(viewsets.ModelViewSet):
    serializer_class = PsychologistSerializer
    queryset = Psychologists.objects.all()

@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
class InfantPatientView(viewsets.ModelViewSet):
    serializer_class = InfantPatientSerializer
    queryset = InfantPatient.objects.all()
    
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
class QuestionnaireView(viewsets.ModelViewSet):
    serializer_class = QuestionnaireSerializer
    queryset = Questionnaire.objects.all()

@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
class UserProfileView(viewsets.ModelViewSet):
    serializer_class = UserProfileSerializer
    queryset = UserProfile.objects.all()

@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def patients_by_month(request):
    monthly_data = (
        Questionnaire.objects
        .annotate(
            year=ExtractYear('date_evaluation'),
            month=ExtractMonth('date_evaluation')
        )
        .values('year', 'month','patient__psychology')
        .annotate(total=Count('id'))
        .order_by('year', 'month','patient__psychology')
    )
    return Response(monthly_data)


@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def patients_by_month_autism(request):
    monthly_data = (
        Questionnaire.objects
        .annotate(
            year=ExtractYear('date_evaluation'),  
            month=ExtractMonth('date_evaluation')
        )
        .values('year', 'month','patient__psychology')
        .annotate(
            paciente_con_DT=Count(Case(When(result=0, then=1), output_field=IntegerField())),
            paciente_con_TEA=Count(Case(When(result=1, then=1), output_field=IntegerField())),
        )
        .order_by('year', 'month','patient__psychology')
    )
    return Response(monthly_data)
    
@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def patients_by_gender(request):
    gender_data = (
        InfantPatient.objects
        .values('gender','psychology')
        .annotate(total=Count('id'))
        .order_by('gender','psychology')
    )
    
    return Response(gender_data)

def change_email(user,email_change):
    user_profile = UserProfile.objects.filter(user=user).first()

    verification_code = random.randint(100000, 999999)

    if user_profile:
        user_profile.code_change = verification_code
        user_profile.save()
    
    subject = "AutDetect - Cambio de Correo Electrónico 📧"
    html_message = f"""
    <html>
    <head></head>
    <body>
    <p>Hola, {email_change}</p>
    <p>Hemos recibido una solicitud para cambiar la dirección de correo electrónico asociada a tu cuenta en <strong>AutDetect</strong>. Si has solicitado este cambio, por favor confirma tu nueva dirección de correo electrónico utilizando el código de verificación que se muestra a continuación.</p>
    <p><strong>Código de verificación: {verification_code}</strong></p>
    <p>Si no solicitaste este cambio, por favor ignora este correo o contacta a nuestro equipo de soporte.</p>
    <p>Gracias por formar parte de <strong>AutDetect</strong> y por tu dedicación en la detección temprana del autismo. Tu compromiso con esta causa es muy valioso para nosotros. 🌟</p>
    <p>Atentamente,<br>
    <strong>AutDetect</strong><br>
    [autdetect@gmail.com] ✉️</p>
    </body>
    </html>
    """
    from_email = settings.DEFAULT_FROM_EMAIL
    recipient_list = [email_change]

    try:
        email = EmailMessage(
            subject=subject,
            body=html_message,
            from_email=from_email,
            to=recipient_list,
        )
        email.content_subtype = 'html'  # Importante para enviar HTML
        email.send()
    except Exception as e:
        print(f"Error al enviar correo: {e}")

@api_view(['POST'])
def change_email_verification(request):
    username = request.data.get('email', '')
    existing_user = User.objects.filter(username=username).first()
    email_change = request.data.get('email_change', '')
    
    change_email(existing_user,email_change)

    return Response(status=status.HTTP_200_OK)

@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def change_username(request):
    username = request.data.get('email', '')
    existing_user = User.objects.filter(username=username).first()
    email_change = request.data.get('email_change', '')
    if existing_user:
        existing_user.username = email_change
        existing_user.email = email_change
        existing_user.save()
        psychology = Psychologists.objects.filter(email=username).first()
        if psychology:
            psychology.email = email_change
            psychology.save()
    return Response(status=status.HTTP_200_OK)

@api_view(['POST'])
def change_password(request):
    username = request.data.get('email', '')
    existing_user = User.objects.filter(username=username).first()
    password = request.data.get('password', '')
    if existing_user:
        existing_user.set_password(password)
        existing_user.save()
    return Response(status=status.HTTP_200_OK)

@api_view(['POST'])
def change_password_email(request):
    username = request.data.get('email', '')
    
    existing_user = User.objects.filter(username=username).first()
    
    user_profile = UserProfile.objects.filter(user=existing_user).first()

    verification_code = random.randint(100000, 999999)

    if user_profile:
        user_profile.code_change = verification_code
        user_profile.save()
    else:
        return Response("El correo ingresado no se encuentra registrado.", status=status.HTTP_400_BAD_REQUEST)
    
    subject = "AutDetect - Cambio de Contraseña 🔑"
    html_message = f"""
    <html>
    <head></head>
    <body>
    <p>Hola, {username}</p>
    <p>Hemos recibido una solicitud para cambiar la contraseña asociada a tu cuenta en <strong>AutDetect</strong>. Si has solicitado este cambio, por favor confirma tu nueva contraseña utilizando el código de verificación que se muestra a continuación.</p>
    <p><strong>Código de verificación: {verification_code}</strong></p>
    <p>Si no solicitaste este cambio, por favor ignora este correo o contacta a nuestro equipo de soporte.</p>
    <p>Gracias por formar parte de <strong>AutDetect</strong> y por tu dedicación en la detección temprana del autismo. Tu compromiso con esta causa es muy valioso para nosotros. 🌟</p>
    <p>Atentamente,<br>
    <strong>AutDetect</strong><br>
    [autdetect@gmail.com] ✉️</p>
    </body>
    </html>
    """
    from_email = settings.DEFAULT_FROM_EMAIL
    recipient_list = [username]

    try:
        email = EmailMessage(
            subject=subject,
            body=html_message,
            from_email=from_email,
            to=recipient_list,
        )
        email.content_subtype = 'html'  # Importante para enviar HTML
        email.send()
        return Response(status=status.HTTP_200_OK)
    except Exception as e:
        print(f"Error al enviar correo: {e}")


@api_view(['POST'])
def validate_code(request):
    username = request.data.get('email', '')
    code = request.data.get('code', '')
    
    existing_user = User.objects.filter(username=username).first()

    if existing_user:
        print(existing_user)
        user_profile = UserProfile.objects.filter(user=existing_user).first()
        print(user_profile)
        if(user_profile.code_change == code):
            return Response({"success": True}, status=status.HTTP_200_OK)
        else:
            return Response("El código no corresponde al código enviado.", status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
def generar_reporte_pdf(request):
    # Crear el objeto HttpResponse con el contenido del PDF
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="reporte.pdf"'

    # Crear un objeto canvas de ReportLab
    c = canvas.Canvas(response, pagesize=A4)
    width, height = A4

    # Ruta del logo (asegúrate de colocar la ruta correcta)
    logo_path = os.path.join('crudautdetect/static/imgs/logoautdetect.png')

    # Agregar el logo (en la esquina superior derecha)
    c.drawImage(logo_path, width - 2 * inch, height - inch - 20, width=1.5 * inch, height=1.5 * inch)


    c.setFont("Helvetica", 12)
    c.drawString(50, height - 40, "AutDetect")
    c.drawString(50, height - 60, "Contacto: autdetect@gmail.com")
    # Título del reporte

    # Añadir título
    c.setFont("Helvetica-Bold", 16)
    c.drawString(50, height - 100, "Reporte de detección temprana del Trastorno Espectro Autista")

    # Añadir información de contacto
    

    # Subtítulo 1
    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, height - 130, "1. Respuestas del cuestionario de comportamiento")

    # Preguntas
    questions = [
        "1. Si señalas algo en la habitación, como un juguete o un animal, ¿tu hijo(a) lo mira?",
        "2. ¿Alguna vez has pensado que tu hijo(a) podría ser sordo(a)?",
        "3. ¿Tu hijo(a) juega a hacer cosas como beber de una taza de juguete, hablar por teléfono, o darle de comer a una muñeca o peluche?",
        "4. ¿Hace tu hijo(a) movimientos extraños con los dedos cerca de sus ojos, o junta sus manos o pies de manera inusual?",
        "5. ¿Tu hijo(a) señala con el dedo o la mano cuando quiere algo o necesita ayuda, como un juguete o comida que no puede alcanzar?",
        "6. ¿Alguna vez tu hijo(a) señala algo solo para mostrarte, como un avión en el cielo o un animal?",
        "7. ¿Tu hijo(a) muestra interés en otros niños, como mirarlos, sonreírles o tratar de jugar con ellos?",
        "8. ¿Tu hijo(a) te muestra cosas para llamar tu atención, no porque necesite ayuda, sino solo para compartirlas contigo, como una flor o un juguete?",
        "9. ¿Responde tu hijo(a) cuando lo(a) llamas por su nombre, como volteándose, hablándote o dejando de hacer lo que estaba haciendo?",
        "10. ¿Cuando le sonríes a tu hijo(a), él o ella te sonríe de vuelta?",
        "11. ¿Tu hijo(a) es sensible a ciertos ruidos, como la aspiradora, música alta, o el sonido de una moto?",
        "12. ¿Te mira tu hijo(a) a los ojos cuando le hablas, juegas con él/ella, o lo(a) vistes?",
        "13. ¿Usa tu hijo(a) gestos como decir adiós con la mano, aplaudir, o imitar algún sonido gracioso que haces?",
        "14. Si te giras a ver algo, ¿tu hijo(a) trata de mirar hacia lo que estás mirando?",
        "15. ¿Tu hijo(a) intenta que le prestes atención, por ejemplo, diciendo “mira” o 'mírame'?",
        "16. ¿Entiende tu hijo(a) lo que le dices que haga, como “pon el libro en la silla” o “tráeme la manta” sin necesidad de gestos?",
        "17. ¿A tu hijo(a) le cuesta cambiar de rutina, como cambiar de horario en la escuela, salir de vacaciones, o tomar un camino diferente?",
        "18. ¿Tu hijo(a) tiene dificultades para aceptar diferentes texturas o colores de alimentos?",
        "19. ¿Tu hijo(a) tiene un interés exagerado por un tipo específico de dibujo, juego o tema?",
        "20. ¿Tu hijo(a) repite casi siempre la última palabra que escucha de una frase dicha por otra persona?",
        "21. ¿Tu hijo(a) te jala de la mano para que hagas cosas por él/ella, como abrir una puerta, coger un objeto, o jugar?",
        "22. Si personas desconocidas saludan a tu hijo(a), ¿él/ella las mira o responde al saludo?",
        "23. ¿Tu hijo(a) puede jugar con niños que no conoce cuando está en el parque?",
        "24. ¿Tu hijo(a) se integra al grupo de niños cuando va a una fiesta infantil?",
    ]

    y_position = height - 160
    c.setFont("Helvetica", 10)
    for question in questions:
        c.drawString(70, y_position, question)
        y_position -= 20

    # Subtítulo 2
    c.setFont("Helvetica-Bold", 14)
    c.drawString(100, y_position - 20, "2. Resultados de la evaluación")

    # Datos de la tabla
    table_data = [
        ["Nombre", "Apellido", "Fecha de nacimiento", "Fecha de evaluación", "Resultado", "Probabilidad"],
        ["Juan", "Pérez", "01/01/2010", "15/08/2024", "Positivo", "85%"],
        ["Ana", "García", "05/05/2012", "15/08/2024", "Negativo", "10%"],
    ]

    # Calcular las posiciones
    table_y_position = y_position - 60
    c.setFont("Helvetica-Bold", 12)
    for i, row in enumerate(table_data):
        for j, cell in enumerate(row):
            c.drawString(100 + j * 90, table_y_position, cell)
        table_y_position -= 20

    c.showPage()
    c.save()

    return response