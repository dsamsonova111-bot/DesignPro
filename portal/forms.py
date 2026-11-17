import re
from django import forms
from django.core.exceptions import ValidationError
from .models import CustomUser


class RegisterForm(forms.ModelForm):
    full_name = forms.CharField(
        label='ФИО',
        widget=forms.TextInput(attrs={'placeholder': 'Иванов Иван Иванович'})
    )
    username = forms.CharField(
        label='Логин',
        widget=forms.TextInput(attrs={'placeholder': 'ivan-ivanov'})
    )
    email = forms.EmailField(
        label='Email',
        widget=forms.EmailInput(attrs={'placeholder': 'ivan@example.ru'})
    )
    password = forms.CharField(
        label='Пароль',
        widget=forms.PasswordInput(attrs={'placeholder': 'Введите пароль'})
    )
    password_confirm = forms.CharField(
        label='Повтор пароля',
        widget=forms.PasswordInput(attrs={'placeholder': 'Повторите пароль'})
    )
    consent = forms.BooleanField(
        label='Я согласен на обработку персональных данных',
        required=True,
        error_messages={'required': 'Необходимо дать согласие на обработку персональных данных.'}
    )

    class Meta:
        model = CustomUser
        fields = ['full_name', 'username', 'email']

    def clean_full_name(self):
        full_name = self.cleaned_data.get('full_name', '').strip()
        if not re.match(r'^[А-Яа-яЁё\s-]+$', full_name):
            raise ValidationError('ФИО должно содержать только кириллические буквы, пробелы и дефис.')
        return full_name

    def clean_username(self):
        username = self.cleaned_data.get('username', '').strip()
        if not re.match(r'^[A-Za-z-]+$', username):
            raise ValidationError('Логин должен содержать только латинские буквы и дефис.')
        if CustomUser.objects.filter(username__iexact=username).exists():
            raise ValidationError('Пользователь с таким логином уже зарегистрирован.')
        return username

    def clean_email(self):
        email = self.cleaned_data.get('email', '').strip()
        if CustomUser.objects.filter(email__iexact=email).exists():
            raise ValidationError('Этот Email уже используется.')
        return email

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        password_confirm = cleaned_data.get('password_confirm')

        if password and password_confirm and password != password_confirm:
            self.add_error('password_confirm', 'Введённые пароли не совпадают.')

        return cleaned_data