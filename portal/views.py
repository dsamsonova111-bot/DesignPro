from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .forms import RegisterForm


def index(request):
    """Временная заглушка главной страницы (доработаем на Коммите 5)."""
    return render(request, 'base.html')


def register_view(request):
    """Регистрация нового пользователя с серверной валидацией."""
    if request.user.is_authenticated:
        return redirect('profile')

    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()
            messages.success(request, 'Регистрация прошла успешно! Теперь вы можете войти в личный кабинет.')
            return redirect('login')
    else:
        form = RegisterForm()

    return render(request, 'registration/register.html', {'form': form})


@login_required
def profile_view(request):
    """Временная заглушка личного кабинета (доработаем на Коммите 4)."""
    return render(request, 'base.html')