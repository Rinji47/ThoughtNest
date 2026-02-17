from django.urls import path

from . import views

urlpatterns = [
	path('', views.home, name='home'),
	path('register/', views.user_register, name='register'),
	path('login/', views.user_login, name='login'),
	path('logout/', views.user_logout, name='logout'),
	path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
	path('admin-page/', views.admin_page, name='admin_page'),
	path('admin/category/create/', views.admin_create_category, name='admin_create_category'),
	path('admin/category/<int:pk>/delete/', views.admin_delete_category, name='admin_delete_category'),
	path('profile/', views.profile, name='profile'),
]
