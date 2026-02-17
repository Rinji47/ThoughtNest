from django.urls import path

from . import views

urlpatterns = [
	path('categories/', views.categories, name='categories'),
	path('posts/new/', views.post_create, name='post_create'),
	path('posts/<int:pk>/edit/', views.post_edit, name='post_edit'),
	path('posts/<int:pk>/comment/', views.post_add_comment, name='post_add_comment'),
	path('posts/<int:pk>/like/', views.post_toggle_like, name='post_toggle_like'),
	path('posts/<int:pk>/', views.post_detail, name='post_detail'),
]
