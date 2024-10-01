from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser
from django.contrib.auth.forms import AuthenticationForm

class CustomUserCreationForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['first_name','last_name','email', 'password']
        widgets = {
            'password': forms.PasswordInput(),
        }

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if CustomUser.objects.filter(email=email).exists():
            raise forms.ValidationError('This email is already in use.')
        return email

class CodeVerificationForm(forms.Form):
    code = forms.CharField(max_length=6, label="Verification Code", widget=forms.TextInput(attrs={'placeholder': 'Enter your code'}))

class PasswordResetForm(forms.Form):
    email = forms.EmailField()

class PasswordChangeForm(forms.Form):
    new_password = forms.CharField(widget=forms.PasswordInput)



class LoginForm(AuthenticationForm):
    email = forms.EmailField(widget=forms.EmailInput(attrs={
        'placeholder': 'Email or Phone',
        'class': 'input',
    }))
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'placeholder': 'Password',
        'class': 'input pass-key',
    }))    
