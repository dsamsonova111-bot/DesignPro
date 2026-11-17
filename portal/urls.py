from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('register/', views.register_view, name='register'),
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('profile/', views.profile_view, name='profile'),
    path('requests/create/', views.create_request_view, name='request-create'),
    path('requests/<int:pk>/delete/', views.delete_request_view, name='request-delete'),
    path('admin-panel/', views.admin_panel_view, name='admin-panel'),
    path('admin-panel/requests/<int:pk>/in-progress/', views.change_status_in_progress_view, name='request-in-progress'),
    path('admin-panel/requests/<int:pk>/completed/', views.change_status_completed_view, name='request-completed'),
    path('admin-panel/categories/', views.category_list_view, name='category-list'),
    path('admin-panel/categories/<int:pk>/delete/', views.category_delete_view, name='category-delete'),
]