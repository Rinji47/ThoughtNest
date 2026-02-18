from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Prefetch
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from .models import Category, Comment, Like, Post, Tag


def categories(request):
	categories_list = Category.objects.annotate(post_count=Count('posts')).order_by('-post_count', 'name')
	for cat in categories_list:
		cat.recent_posts = cat.posts.filter(status=Post.STATUS_PUBLISHED).select_related('author').order_by('-created_at')[:2]
	tags = Tag.objects.annotate(post_count=Count('posts')).order_by('-post_count', 'name')
	

	context = {'categories': categories_list, 'tags': tags}
	return render(request, 'pages/categories.html', context)


def post_detail(request, pk):
	post = get_object_or_404(Post.objects.prefetch_related('tags'), pk=pk)
	comments = post.comments.filter(approved=True).select_related('author')
	user_has_liked = False
	if request.user.is_authenticated:
		user_has_liked = Like.objects.filter(post=post, user=request.user).exists()
	return render(
		request,
		'posts/post_detail.html',
		{'post': post, 'comments': comments, 'user_has_liked': user_has_liked},
	)


@login_required
def post_create(request):
	if request.method == 'POST':
		title = request.POST.get('title', '').strip()
		category_id = request.POST.get('category')
		tags_input = request.POST.get('tags', '').strip()
		content = request.POST.get('content', '').strip()
		status = request.POST.get('status', Post.STATUS_PUBLISHED)
		featured_image = request.FILES.get('featured_image')

		if not title:
			messages.error(request, 'Title is required.')
			return redirect('post_create')
		
		if not content:
			messages.error(request, 'Content is required.')
			return redirect('post_create')

		post = Post.objects.create(
			author=request.user,
			title=title,
			content=content,
			status=status,
			category_id=category_id if category_id else None,
			featured_image=featured_image,
		)

		# Handle tags
		if tags_input:
			tag_names = [tag.strip() for tag in tags_input.split(',')]
			tag_names = [tag.lstrip("#") for tag in tag_names]
			for tag_name in tag_names:
				if tag_name:
					tag, _ = Tag.objects.get_or_create(name=tag_name)
					post.tags.add(tag)

		messages.success(request, 'Post created successfully!')
		return redirect('post_detail', pk=post.pk)

	context = {
		'mode': 'create',
		'categories': Category.objects.all(),
		'tags': Tag.objects.all(),
		'popular_tags': Tag.objects.annotate(post_count=Count('posts')).order_by('-post_count', 'name')[:10],
		'all_tag_names': list(Tag.objects.order_by('name').values_list('name', flat=True)),
	}
	return render(request, 'posts/post_form.html', context)


@login_required
def post_edit(request, pk):
	post = get_object_or_404(Post, pk=pk)
	if not (request.user.is_staff or request.user == post.author):
		messages.error(request, 'You do not have permission to edit this post.')
		return redirect('post_detail', pk=post.pk)
	if request.method == 'POST':
		post.title = request.POST.get('title', post.title).strip()
		post.content = request.POST.get('content', post.content).strip()
		post.status = request.POST.get('status', post.status)
		category_id = request.POST.get('category')
		post.category_id = category_id if category_id else None
		
		if 'featured_image' in request.FILES:
			post.featured_image = request.FILES['featured_image']

		# Handle tags
		tags_input = request.POST.get('tags', '').strip()
		post.tags.clear()
		if tags_input:
			tag_names = [tag.strip() for tag in tags_input.split(',')]
			for tag_name in tag_names:
				if tag_name:
					tag, _ = Tag.objects.get_or_create(name=tag_name)
					post.tags.add(tag)

		post.save()
		messages.success(request, 'Post updated successfully!')
		return redirect('post_detail', pk=post.pk)

	context = {
		'mode': 'edit',
		'post': post,
		'categories': Category.objects.all(),
		'tags': Tag.objects.all(),
		'popular_tags': Tag.objects.annotate(post_count=Count('posts')).order_by('-post_count', 'name')[:10],
		'all_tag_names': list(Tag.objects.order_by('name').values_list('name', flat=True)),
	}
	return render(request, 'posts/post_form.html', context)


@login_required
@require_POST
def post_add_comment(request, pk):
	post = get_object_or_404(Post, pk=pk)
	content = (request.POST.get('content') or '').strip()
	if not content:
		messages.error(request, 'Comment cannot be empty.')
		return redirect('post_detail', pk=post.pk)

	Comment.objects.create(post=post, author=request.user, content=content)
	messages.success(request, 'Comment added.')
	return redirect('post_detail', pk=post.pk)


@login_required
@require_POST
def post_toggle_like(request, pk):
	post = get_object_or_404(Post, pk=pk)
	like = Like.objects.filter(post=post, user=request.user).first()
	if like:
		like.delete()
		messages.info(request, 'Like removed.')
	else:
		Like.objects.create(post=post, user=request.user)
		messages.success(request, 'You liked the post.')

	next_url = request.POST.get('next') or request.META.get('HTTP_REFERER')
	if next_url:
		return redirect(next_url)
	return redirect('post_detail', pk=post.pk)

@login_required
def user_manage_posts(request):
	posts = Post.objects.filter(author=request.user).select_related('category').prefetch_related('comments', 'likes', 'tags').order_by('-created_at')
	context = {'posts': posts}
	return render(request, 'posts/user_posts.html', context)

@login_required
@require_POST
def delete_post(request, pk):
	post = get_object_or_404(Post, pk=pk)
	if not (request.user.is_staff or request.user == post.author):
		messages.error(request, 'You do not have permission to delete this post.')
		return redirect('post_detail', pk=post.pk)
	
	post.delete()
	messages.success(request, 'Post deleted successfully!')
	return redirect('admin_posts' if request.user.is_staff else 'profile')


# ADMIN VIEWS

@login_required
def admin_posts(request):
	if not request.user.is_staff:
		messages.error(request, 'You do not have permission.')
		return redirect('home')
	
	posts = Post.objects.select_related('author', 'category').prefetch_related('comments', 'likes').order_by('-created_at')
	context = {'posts': posts}
	return render(request, 'admin/posts.html', context)


@login_required
def admin_comments(request):
	if not request.user.is_staff:
		messages.error(request, 'You do not have permission.')
		return redirect('home')
	
	comments = Comment.objects.select_related('author', 'post').order_by('-created_at')
	context = {'comments': comments}
	return render(request, 'admin/comments.html', context)


@login_required
def admin_subscribers(request):
	if not request.user.is_staff:
		messages.error(request, 'You do not have permission.')
		return redirect('home')
	
	context = {}
	return render(request, 'admin/subscribers.html', context)


@login_required
def admin_settings(request):
	if not request.user.is_staff:
		messages.error(request, 'You do not have permission.')
		return redirect('home')
	
	context = {}
	return render(request, 'admin/settings.html', context)


@login_required
def admin_categories(request):
	if not request.user.is_staff:
		messages.error(request, 'You do not have permission.')
		return redirect('home')
	
	categories = Category.objects.annotate(post_count=Count('posts')).order_by('-created_at')
	context = {'categories': categories}
	return render(request, 'admin/categories.html', context)


@login_required
def create_category_page(request):
	if not request.user.is_staff:
		messages.error(request, 'You do not have permission.')
		return redirect('home')
	
	if request.method == 'POST':
		name = request.POST.get('name', '').strip()
		if not name:
			messages.error(request, 'Category name is required.')
			return redirect('create_category_page')
		
		if Category.objects.filter(name=name).exists():
			messages.error(request, 'Category with this name already exists.')
			return redirect('create_category_page')
		
		Category.objects.create(name=name)
		messages.success(request, 'Category created successfully!')
		return redirect('admin_categories')
	
	return render(request, 'admin/create_category.html', {})


@login_required
@require_POST
def admin_delete_category(request, pk):
	if not request.user.is_staff:
		messages.error(request, 'You do not have permission.')
		return redirect('home')
	
	category = get_object_or_404(Category, pk=pk)
	category.delete()
	messages.success(request, 'Category deleted successfully!')
	return redirect('admin_categories')