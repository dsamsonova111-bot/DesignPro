import re
from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm
from .models import Category, DesignRequest

User = get_user_model()


class RegisterForm(UserCreationForm):
    full_name = forms.CharField(
        label='ФИО',
        max_length=255,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control'}),
    )
    username = forms.CharField(
        label='Логин',
        max_length=150,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control'}),
    )
    email = forms.EmailField(
        label='Email',
        required=True,
        widget=forms.EmailInput(attrs={'class': 'form-control'}),
    )
    password1 = forms.CharField(
        label='Пароль',
        required=True,
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
    )
    password2 = forms.CharField(
        label='Повтор пароля',
        required=True,
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
    )
    agreement = forms.BooleanField(
        label='Я даю согласие на обработку персональных данных',
        required=True,
        error_messages={
            'required': 'Необходимо отметить согласие на обработку персональных данных.',
        },
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
    )

    class Meta:
        model = User
        fields = ['full_name', 'username', 'email', 'password1', 'password2', 'agreement']

    def clean_full_name(self):
        full_name = self.cleaned_data.get('full_name', '').strip()
        if not re.fullmatch(r'[А-Яа-яЁё\s-]+', full_name):
            raise forms.ValidationError(
                'ФИО должно содержать только кириллические буквы, пробелы и дефис.'
            )
        return full_name

    def clean_username(self):
        username = self.cleaned_data.get('username', '').strip()
        if not re.fullmatch(r'[A-Za-z-]+', username):
            raise forms.ValidationError(
                'Логин может содержать только латинские буквы и дефис.'
            )
        if User.objects.filter(username__iexact=username).exists():
            raise forms.ValidationError('Пользователь с таким логином уже существует.')
        return username

    def clean_agreement(self):
        agreed = self.cleaned_data.get('agreement')
        if not agreed:
            raise forms.ValidationError(
                'Необходимо отметить согласие на обработку персональных данных.'
            )
        return agreed



class DesignRequestForm(forms.ModelForm):
    class Meta:
        model = DesignRequest
        fields = ['title', 'description', 'category', 'photo']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'photo': forms.FileInput(attrs={'class': 'form-control'}),
        }


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
        }


class StatusInProgressForm(forms.ModelForm):
    comment = forms.CharField(
        label='Комментарий',
        required=True,
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
    )

    class Meta:
        model = DesignRequest
        fields = ['comment']


class StatusCompletedForm(forms.ModelForm):
    design_image = forms.ImageField(
        label='Изображение дизайна',
        required=True,
        widget=forms.FileInput(attrs={'class': 'form-control'}),
    )

    class Meta:
        model = DesignRequest
        fields = ['design_image']