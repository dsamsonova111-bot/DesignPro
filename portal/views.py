from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from .forms import (
    RegisterForm,
    DesignRequestForm,
    StatusInProgressForm,
    StatusCompletedForm,
    CategoryForm,
)
from .models import DesignRequest, Category


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


def is_admin_user(user):
    """Проверка, что пользователь авторизован и является администратором."""
    return user.is_authenticated and user.is_staff


@user_passes_test(is_admin_user, login_url='login')
def admin_panel_view(request):
    """Панель управления сайтом (личный кабинет администратора)."""
    all_requests = DesignRequest.objects.select_related('user', 'category').all()
    categories = Category.objects.all()
    context = {
        'all_requests': all_requests,
        'categories': categories,
    }
    return render(request, 'portal/admin_panel.html', context)


@user_passes_test(is_admin_user, login_url='login')
def change_status_in_progress_view(request, pk):
    """Смена статуса заявки с «Новая» на «Принято в работу» с обязательным комментарием."""
    design_req = get_object_or_404(DesignRequest, pk=pk)

    if design_req.status != 'new':
        messages.error(request, 'Смена статуса невозможна: заявка уже находится в работе или выполнена.')
        return redirect('admin-panel')

    if request.method == 'POST':
        form = StatusInProgressForm(request.POST, instance=design_req)
        if form.is_valid():
            req_obj = form.save(commit=False)
            req_obj.status = 'in_progress'
            req_obj.save()
            messages.success(request, f'Заявка «{req_obj.title}» переведена в статус «Принято в работу».')
            return redirect('admin-panel')
    else:
        form = StatusInProgressForm(instance=design_req)

    return render(request, 'portal/status_in_progress.html', {
        'design_req': design_req,
        'form': form,
    })


@user_passes_test(is_admin_user, login_url='login')
def change_status_completed_view(request, pk):
    """Смена статуса заявки с «Новая» на «Выполнено» с обязательным изображением дизайна."""
    design_req = get_object_or_404(DesignRequest, pk=pk)

    if design_req.status != 'new':
        messages.error(request, 'Смена статуса невозможна: заявка уже находится в работе или выполнена.')
        return redirect('admin-panel')

    if request.method == 'POST':
        form = StatusCompletedForm(request.POST, request.FILES, instance=design_req)
        if form.is_valid():
            req_obj = form.save(commit=False)
            req_obj.status = 'completed'
            req_obj.save()
            messages.success(request, f'Заявка «{req_obj.title}» переведена в статус «Выполнено».')
            return redirect('admin-panel')
    else:
        form = StatusCompletedForm(instance=design_req)

    return render(request, 'portal/status_completed.html', {
        'design_req': design_req,
        'form': form,
    })
@user_passes_test(is_admin_user, login_url='login')
def category_list_view(request):
    """Просмотр и добавление категорий заявок администратором."""
    categories = Category.objects.all().order_by('id')

    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            category = form.save()
            messages.success(request, f'Категория «{category.name}» успешно добавлена.')
            return redirect('category-list')
    else:
        form = CategoryForm()

    return render(request, 'portal/category_list.html', {
        'categories': categories,
        'form': form,
    })


@user_passes_test(is_admin_user, login_url='login')
def category_delete_view(request, pk):
    """Удаление категории с подтверждением и каскадным удалением всех её заявок."""
    category = get_object_or_404(Category, pk=pk)
    related_requests_count = category.requests.count()

    if request.method == 'POST':
        category_name = category.name
        category.delete()
        messages.success(
            request,
            f'Категория «{category_name}» и все связанные заявки ({related_requests_count} шт.) удалены.'
        )
        return redirect('category-list')

    return render(request, 'portal/category_confirm_delete.html', {
        'category': category,
        'related_requests_count': related_requests_count,
    })