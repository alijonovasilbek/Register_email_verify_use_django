from django.urls import path
from .views import (register_view, email_verification_view, login_view, homepage,
                    password_reset_view, password_reset_confirm_view, password_change_view,logout_view)

urlpatterns = [
    path('', register_view, name='register'),
    path('verify-email/', email_verification_view, name='email_verification'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('password-reset/', password_reset_view, name='password_reset'),
    path('password-reset-confirm/', password_reset_confirm_view, name='password_reset_confirm'),
    path('password-change/', password_change_view, name='password_change'),
    path('homepage/', homepage, name='homepage'),
]
