from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.views import LoginView
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from .forms import (
    CategoryForm,
    DesignRequestForm,
    RegisterForm,
    StatusCompletedForm,
    StatusInProgressForm,
)
from .models import Category, DesignRequest


def is_admin(user):
    return user.is_authenticated and user.is_superuser


class CustomLoginView(LoginView):
    template_name = 'registration/login.html'
    redirect_authenticated_user = True

    def get_success_url(self):
        if self.request.user.is_superuser:
            return reverse_lazy('admin_panel')
        return reverse_lazy('profile')


def index(request):
    completed_requests = DesignRequest.objects.filter(
        status=DesignRequest.STATUS_COMPLETED
    ).order_by('-created_at')[:4]

    in_progress_count = DesignRequest.objects.filter(
        status=DesignRequest.STATUS_IN_PROGRESS
    ).count()

    return render(
        request,
        'portal/index.html',
        {
            'completed_requests': completed_requests,
            'in_progress_count': in_progress_count,
        },
    )


def register(request):
    if request.user.is_authenticated:
        return redirect('profile')

    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Регистрация прошла успешно.')
            return redirect('profile')
        messages.error(request, 'Проверьте правильность заполнения полей.')
    else:
        form = RegisterForm()

    return render(request, 'registration/register.html', {'form': form})


@login_required
def profile(request):
    if request.user.is_superuser:
        return redirect('admin_panel')

    current_status = request.GET.get('status', '')
    qs = DesignRequest.objects.filter(user=request.user).order_by('-created_at')

    valid_statuses = [choice[0] for choice in DesignRequest.STATUS_CHOICES]
    if current_status in valid_statuses:
        qs = qs.filter(status=current_status)
    else:
        current_status = ''

    return render(
        request,
        'portal/profile.html',
        {
            'requests': qs,
            'status_choices': DesignRequest.STATUS_CHOICES,
            'current_status': current_status,
        },
    )


@login_required
def request_create(request):
    if request.method == 'POST':
        form = DesignRequestForm(request.POST, request.FILES)
        if form.is_valid():
            design_request = form.save(commit=False)
            design_request.user = request.user
            design_request.status = DesignRequest.STATUS_NEW
            design_request.save()
            messages.success(request, 'Заявка создана со статусом «Новая».')
            return redirect('profile')
        messages.error(request, 'Ошибка при создании заявки. Проверьте поля и файл.')
    else:
        form = DesignRequestForm()

    return render(request, 'portal/request_create.html', {'form': form})


@login_required
def request_delete(request, pk):
    design_request = get_object_or_404(DesignRequest, pk=pk, user=request.user)

    if design_request.status != DesignRequest.STATUS_NEW:
        messages.error(
            request,
            'Удалить можно только заявку со статусом «Новая».',
        )
        return redirect('profile')

    if request.method == 'POST':
        design_request.delete()
        messages.success(request, 'Заявка удалена.')
        return redirect('profile')

    return render(
        request,
        'portal/request_confirm_delete.html',
        {'design_request': design_request},
    )


@user_passes_test(is_admin, login_url='login')
def admin_panel(request):
    all_requests = DesignRequest.objects.select_related('user', 'category').order_by('-created_at')
    return render(
        request,
        'portal/admin_panel.html',
        {'requests': all_requests},
    )


@user_passes_test(is_admin, login_url='login')
def status_in_progress(request, pk):
    design_request = get_object_or_404(DesignRequest, pk=pk)

    if design_request.status != DesignRequest.STATUS_NEW:
        messages.error(request, 'Статус можно изменить только у заявки со статусом «Новая».')
        return redirect('admin_panel')

    if request.method == 'POST':
        form = StatusInProgressForm(request.POST, instance=design_request)
        if form.is_valid():
            updated = form.save(commit=False)
            updated.status = DesignRequest.STATUS_IN_PROGRESS
            updated.save()
            messages.success(request, 'Статус изменен на «Принято в работу».')
            return redirect('admin_panel')
    else:
        form = StatusInProgressForm(instance=design_request)

    return render(
        request,
        'portal/status_in_progress.html',
        {'form': form, 'design_request': design_request},
    )


@user_passes_test(is_admin, login_url='login')
def status_completed(request, pk):
    design_request = get_object_or_404(DesignRequest, pk=pk)

    if design_request.status != DesignRequest.STATUS_NEW:
        messages.error(request, 'Статус можно изменить только у заявки со статусом «Новая».')
        return redirect('admin_panel')

    if request.method == 'POST':
        form = StatusCompletedForm(request.POST, request.FILES, instance=design_request)
        if form.is_valid():
            updated = form.save(commit=False)
            updated.status = DesignRequest.STATUS_COMPLETED
            updated.save()
            messages.success(request, 'Статус изменен на «Выполнено».')
            return redirect('admin_panel')
    else:
        form = StatusCompletedForm(instance=design_request)

    return render(
        request,
        'portal/status_completed.html',
        {'form': form, 'design_request': design_request},
    )


@user_passes_test(is_admin, login_url='login')
def category_list(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Категория добавлена.')
            return redirect('category_list')
    else:
        form = CategoryForm()

    categories = Category.objects.all()
    return render(
        request,
        'portal/category_list.html',
        {'form': form, 'categories': categories},
    )


@user_passes_test(is_admin, login_url='login')
def category_delete(request, pk):
    category = get_object_or_404(Category, pk=pk)

    if request.method == 'POST':
        category.delete()
        messages.success(request, 'Категория и связанные с ней заявки удалены.')
        return redirect('category_list')

    return render(
        request,
        'portal/category_confirm_delete.html',
        {'category': category},
    )