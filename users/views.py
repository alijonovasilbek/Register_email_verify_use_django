from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, get_user_model
from django.core.mail import send_mail
from django.conf import settings
import datetime
from random import randint
from .models import CustomUser, PasswordResets
from .forms import CustomUserCreationForm, CodeVerificationForm, PasswordResetForm, PasswordChangeForm
from django.utils import timezone

from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import logout



User=get_user_model()

def register_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            # Foydalanuvchini yaratish, lekin saqlamaslik
            user = form.save(commit=False)
            user.is_active = False  # Foydalanuvchi aktiv emas
            user.set_password(form.cleaned_data['password'])  # Parolni xeshlash
            user.save()  # Foydalanuvchini saqlash

            # Tasdiqlash kodi yaratish va yuborish
            verification_code = randint(100000, 999999)
            PasswordResets.objects.create(user=user, reset_code=verification_code)

            send_mail(
                'Email Verification',
                f'Your verification code is: {verification_code}',
                settings.EMAIL_HOST_USER,
                [user.email],
            )

            request.session['user_id'] = user.id
            return redirect('email_verification')
    else:
        form = CustomUserCreationForm()
    return render(request, 'register.html', {'form': form})


def email_verification_view(request):
    user_id = request.session.get('user_id')
    if not user_id:
        return redirect('register')

    user = CustomUser.objects.get(id=user_id)

    if request.method == 'POST':
        form = CodeVerificationForm(request.POST)
        if form.is_valid():
            entered_code = form.cleaned_data['code']
            try:
                reset_record = PasswordResets.objects.get(user=user, reset_code=entered_code, status=True)

                # UTC vaqtida joriy vaqtni olish
                now = timezone.now()

                # Tanaffus vaqtini hisoblash
                if (now - reset_record.created_at).total_seconds() > 600:
                    form.add_error('code', 'Verification code expired')
                else:
                    user.is_active = True
                    user.save()
                    reset_record.status = False
                    reset_record.save()
                    return redirect('login')
            except PasswordResets.DoesNotExist:
                form.add_error('code', 'Invalid verification code')
    else:
        form = CodeVerificationForm()

    return render(request, 'email_verification.html', {'form': form})


from django.contrib.auth import get_user_model, login
from django.contrib import messages
from django.shortcuts import render, redirect

def login_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        User = get_user_model()

        try:
            # Email orqali foydalanuvchini qidiramiz
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            # Foydalanuvchi topilmasa xatolik xabarini ko'rsatamiz
            messages.error(request, 'Invalid email or password.')
            return render(request, 'login.html')

        # Parolni tekshirish
        if user.check_password(password):
            # Parol to'g'ri bo'lsa foydalanuvchini tizimga kiritamiz
            login(request, user)
            return redirect('homepage')  # Tizimga kirganda `homepage`ga yo'naltirish
        else:
            # Parol noto'g'ri bo'lsa xatolik xabarini ko'rsatamiz
            messages.error(request, 'Invalid email or password.')
            return render(request, 'login.html')  # Noto'g'ri parol bo'lsa yana login sahifasini ko'rsatamiz

    # GET so'rovlar uchun login sahifasini qaytaramiz
    return render(request, 'login.html')



def password_reset_view(request):
    if request.method == 'POST':
        form = PasswordResetForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            user = CustomUser.objects.filter(email=email).first()
            if user:
                reset_code = randint(100000, 999999)
                PasswordResets.objects.create(user=user, reset_code=reset_code)
                send_mail(
                    'Password Reset Code',
                    f'Your password reset code is: {reset_code}',
                    settings.EMAIL_HOST_USER,
                    [email],
                )
                request.session['reset_user_id'] = user.id
                return redirect('password_reset_confirm')
            else:
                form.add_error('email', 'No user found with this email')
    else:
        form = PasswordResetForm()
    return render(request, 'password_reset.html', {'form': form})

from django.utils import timezone

def password_reset_confirm_view(request):
    user_id = request.session.get('reset_user_id')
    if not user_id:
        return redirect('password_reset')

    user = CustomUser.objects.get(id=user_id)

    if request.method == 'POST':
        form = CodeVerificationForm(request.POST)
        if form.is_valid():
            entered_code = form.cleaned_data['code']
            try:
                reset_record = PasswordResets.objects.get(user=user, reset_code=entered_code, status=True)

                # Offset-aware datetime olish
                now = timezone.now()

                if (now - reset_record.created_at).total_seconds() > 600:
                    form.add_error('code', 'Reset code expired')
                else:
                    reset_record.status = False
                    reset_record.save()
                    return redirect('password_change')
            except PasswordResets.DoesNotExist:
                form.add_error('code', 'Invalid reset code')
    else:
        form = CodeVerificationForm()

    return render(request, 'password_reset_confirm.html', {'form': form})


def password_change_view(request):
    user_id = request.session.get('reset_user_id')
    if not user_id:
        return redirect('password_reset')

    user = CustomUser.objects.get(id=user_id)

    if request.method == 'POST':
        form = PasswordChangeForm(request.POST)
        if form.is_valid():
            new_password = form.cleaned_data['new_password']
            user.set_password(new_password)
            user.save()
            return redirect('login')
    else:
        form = PasswordChangeForm()

    return render(request, 'password_change.html', {'form': form})






def logout_view(request):
    logout(request)
    return redirect('login')



def homepage(request):
   return   render(request,'homepage.html')