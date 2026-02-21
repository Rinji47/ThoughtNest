
from django.urls import path


from . import views

urlpatterns = [
	path('tag/<int:pk>/posts/', views.tag_posts, name='tag_posts'),
	path('category/<int:pk>/posts/', views.category_posts, name='category_posts'),
	path('categories/', views.categories, name='categories'),
	path('posts/new/', views.post_create, name='post_create'),
	path('posts/manage/', views.user_manage_posts, name='user_manage_posts'),
	path('profile/comments/', views.user_my_comments, name='user_my_comments'),
	path('profile/likes/', views.user_my_likes, name='user_my_likes'),
	path('profile/comments/<int:pk>/delete/', views.user_delete_comment, name='user_delete_comment'),
	path('posts/<int:pk>/edit/', views.post_edit, name='edit_post'),
	path('posts/<int:pk>/delete/', views.delete_post, name='post_delete'),
	path('posts/<int:pk>/comment/', views.post_add_comment, name='post_add_comment'),
	path('posts/<int:pk>/like/', views.post_toggle_like, name='post_toggle_like'),
	path('posts/<int:pk>/', views.post_detail, name='post_detail'),
	path('admin/posts/', views.admin_posts, name='admin_posts'),
	path('admin/comments/', views.admin_comments, name='admin_comments'),
	path('admin/likes/', views.admin_likes, name='admin_likes'),
		# admin_subscribers URL removed
	path('admin/settings/', views.admin_settings, name='admin_settings'),
	path('admin/categories/', views.admin_categories, name='admin_categories'),
	path('admin/category/create/', views.create_category_page, name='create_category_page'),
	path('admin/category/<int:pk>/delete/', views.admin_delete_category, name='admin_delete_category'),
    path('admin/tags/', views.admin_tags, name='admin_tags'),
    path('admin/tag/delete/<int:pk>/', views.admin_delete_tag, name='admin_delete_tag'),
    path('admin/delete_comment/<int:pk>/', views.admin_delete_comment, name='admin_delete_comment'),
]
