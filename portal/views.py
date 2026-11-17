from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .forms import RegisterForm
from .models import DesignRequest


def index(request):
    """Главная страница портала Design.pro."""
    completed_requests = DesignRequest.objects.filter(status='completed').order_by('-created_at')[:4]
    in_progress_count = DesignRequest.objects.filter(status='in_progress').count()

    context = {
        'completed_requests': completed_requests,
        'in_progress_count': in_progress_count,
    }
    return render(request, 'portal/index.html', context)


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
    """Личный кабинет авторизованного пользователя."""
    user_requests = request.user.requests.all()
    return render(request, 'portal/profile.html', {'user_requests': user_requests})