import os
import re
from django import forms
from django.core.exceptions import ValidationError
from .models import CustomUser, DesignRequest


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


class DesignRequestForm(forms.ModelForm):
    class Meta:
        model = DesignRequest
        fields = ['title', 'description', 'category', 'photo']
        labels = {
            'title': 'Название заявки',
            'description': 'Описание',
            'category': 'Категория',
            'photo': 'Фото помещения или его план (jpg, jpeg, png, bmp до 2 МБ)',
        }
        widgets = {
            'title': forms.TextInput(attrs={'placeholder': 'Например: Дизайн гостиной 24 кв.м.'}),
            'description': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Опишите ваши пожелания к интерьеру...'}),
        }

    def clean_photo(self):
        photo = self.cleaned_data.get('photo')
        if not photo:
            raise ValidationError('Необходимо прикрепить фото помещения или его план.')

        ext = os.path.splitext(photo.name)[1].lower()
        allowed_extensions = ['.jpg', '.jpeg', '.png', '.bmp']
        if ext not in allowed_extensions:
            raise ValidationError('Недопустимый формат файла. Разрешены только: jpg, jpeg, png, bmp.')

        max_size = 2 * 1024 * 1024  # 2 МБ в байтах
        if photo.size > max_size:
            raise ValidationError('Размер файла не должен превышать 2 МБ.')

        return photo