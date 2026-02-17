from django.contrib import admin
from .models import Post, Category, Tag, Comment, Like

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
	list_display = ('title', 'author', 'category', 'status', 'created_at')
	list_filter = ('status', 'category', 'created_at')
	search_fields = ('title', 'content')
	fields = ('title', 'slug', 'author', 'category', 'tags', 'featured_image', 'content', 'status', 'created_at', 'updated_at')
	readonly_fields = ('slug', 'created_at', 'updated_at')

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
	list_display = ('name', 'slug', 'created_at')
	fields = ('name', 'slug', 'created_at')
	readonly_fields = ('slug', 'created_at')

@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
	list_display = ('name', 'slug', 'created_at')
	fields = ('name', 'slug', 'created_at')
	readonly_fields = ('slug', 'created_at')

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
	list_display = ('post', 'author', 'approved', 'created_at')
	list_filter = ('approved', 'created_at')
	search_fields = ('post__title', 'author__username', 'content')

@admin.register(Like)
class LikeAdmin(admin.ModelAdmin):
	list_display = ('post', 'user', 'created_at')
	search_fields = ('post__title', 'user__username')
