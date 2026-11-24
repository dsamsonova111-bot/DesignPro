from django.contrib.auth.views import LogoutView
from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('login/', views.CustomLoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(next_page='index'), name='logout'),
    path('register/', views.register, name='register'),
    path('profile/', views.profile, name='profile'),
    path('request/create/', views.request_create, name='request_create'),
    path('request/<int:pk>/delete/', views.request_delete, name='request_delete'),
    path('admin-panel/', views.admin_panel, name='admin_panel'),
    path('panel/request/<int:pk>/in-progress/', views.status_in_progress, name='status_in_progress'),
    path('panel/request/<int:pk>/completed/', views.status_completed, name='status_completed'),
    path('panel/categories/', views.category_list, name='category_list'),
    path('panel/categories/<int:pk>/delete/', views.category_delete, name='category_delete'),
]