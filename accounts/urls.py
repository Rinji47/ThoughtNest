from django.urls import path

from . import views

urlpatterns = [
	path('', views.home, name='home'),
	path('register/', views.user_register, name='register'),
	path('login/', views.user_login, name='login'),
	path('logout/', views.user_logout, name='logout'),
	path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
	path('admin-page/', views.admin_page, name='admin_page'),
	path('profile/', views.profile, name='profile'),
	path('profile-settings/', views.profile_settings, name='profile_settings'),
    path('admin/users-manage/', views.user_management, name='admin_users_manage'),
    path('admin/users/<int:pk>/delete/', views.admin_delete_user, name='admin_delete_user'),
]