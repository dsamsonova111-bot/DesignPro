from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .forms import RegisterForm
from .models import DesignRequest
from .forms import RegisterForm, DesignRequestForm
from django.shortcuts import render, redirect, get_object_or_404

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
    """Личный кабинет авторизованного пользователя со списком и фильтрацией его заявок."""
    status_filter = request.GET.get('status', '')
    user_requests = request.user.requests.all()

    allowed_statuses = {'new', 'in_progress', 'completed'}
    if status_filter in allowed_statuses:
        user_requests = user_requests.filter(status=status_filter)
    else:
        status_filter = ''

    context = {
        'user_requests': user_requests,
        'current_status': status_filter,
    }
    return render(request, 'portal/profile.html', context)
@login_required
def create_request_view(request):
    """Создание новой заявки авторизованным пользователем."""
    if request.method == 'POST':
        form = DesignRequestForm(request.POST, request.FILES)
        if form.is_valid():
            design_req = form.save(commit=False)
            design_req.user = request.user
            design_req.status = 'new'
            design_req.save()
            messages.success(request, 'Заявка успешно создана!')
            return redirect('profile')
    else:
        form = DesignRequestForm()

    return render(request, 'portal/request_create.html', {'form': form})
@login_required
def delete_request_view(request, pk):
    """Удаление своей заявки в статусе «Новая» с обязательным подтверждением."""
    design_req = get_object_or_404(DesignRequest, pk=pk, user=request.user)

    if design_req.status != 'new':
        messages.error(
            request,
            'Удаление невозможно: заявка уже принята в работу или выполнена.'
        )
        return redirect('profile')

    if request.method == 'POST':
        design_req.delete()
        messages.success(request, 'Заявка успешно удалена.')
        return redirect('profile')

    return render(request, 'portal/request_confirm_delete.html', {'design_req': design_req})