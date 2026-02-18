from django.urls import path

from . import views

urlpatterns = [
	path('categories/', views.categories, name='categories'),
	path('posts/new/', views.post_create, name='post_create'),
	path('posts/manage/', views.user_manage_posts, name='user_manage_posts'),
	path('posts/<int:pk>/edit/', views.post_edit, name='edit_post'),
	path('posts/<int:pk>/delete/', views.delete_post, name='post_delete'),
	path('posts/<int:pk>/comment/', views.post_add_comment, name='post_add_comment'),
	path('posts/<int:pk>/like/', views.post_toggle_like, name='post_toggle_like'),
	path('posts/<int:pk>/', views.post_detail, name='post_detail'),
	path('admin/posts/', views.admin_posts, name='admin_posts'),
	path('admin/comments/', views.admin_comments, name='admin_comments'),
	path('admin/subscribers/', views.admin_subscribers, name='admin_subscribers'),
	path('admin/settings/', views.admin_settings, name='admin_settings'),
	path('admin/categories/', views.admin_categories, name='admin_categories'),
	path('admin/category/create/', views.create_category_page, name='create_category_page'),
	path('admin/category/<int:pk>/delete/', views.admin_delete_category, name='admin_delete_category'),
]
