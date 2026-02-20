from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Prefetch, Q
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST
from datetime import datetime, timedelta

from .models import Category, Comment, Like, Post, Tag

# Dedicated page for user's comments

@login_required
def user_my_comments(request):
	comments = Comment.objects.filter(author=request.user).select_related('post').order_by('-created_at')

	# Filters
	search_query = request.GET.get('q', '').strip()
	post_id = request.GET.get('post', '')
	date_range = request.GET.get('date_range', '')

	if search_query:
		comments = comments.filter(content__icontains=search_query)
	if post_id:
		comments = comments.filter(post_id=post_id)
	if date_range:
		today = datetime.now().date()
		if date_range == 'today':
			comments = comments.filter(created_at__date=today)
		elif date_range == 'week':
			start_date = today - timedelta(days=7)
			comments = comments.filter(created_at__date__gte=start_date)
		elif date_range == 'month':
			start_date = today - timedelta(days=30)
			comments = comments.filter(created_at__date__gte=start_date)
		elif date_range == 'year':
			start_date = today - timedelta(days=365)
			comments = comments.filter(created_at__date__gte=start_date)

	# For filter dropdowns
	posts = Post.objects.filter(comments__author=request.user).distinct().order_by('title')

	context = {
		'comments': comments,
		'posts': posts,
		'search_query': search_query,
		'selected_post': post_id,
		'selected_date_range': date_range,
	}
	return render(request, 'users/profile_comments.html', context)

# Dedicated page for user's liked posts

@login_required
def user_my_likes(request):
	likes = Like.objects.filter(user=request.user).select_related('post').order_by('-created_at')

	# Filters
	search_query = request.GET.get('q', '').strip()
	date_range = request.GET.get('date_range', '')

	if search_query:
		likes = likes.filter(post__title__icontains=search_query)
	if date_range:
		today = datetime.now().date()
		if date_range == 'today':
			likes = likes.filter(created_at__date=today)
		elif date_range == 'week':
			start_date = today - timedelta(days=7)
			likes = likes.filter(created_at__date__gte=start_date)
		elif date_range == 'month':
			start_date = today - timedelta(days=30)
			likes = likes.filter(created_at__date__gte=start_date)
		elif date_range == 'year':
			start_date = today - timedelta(days=365)
			likes = likes.filter(created_at__date__gte=start_date)

	context = {
		'likes': likes,
		'search_query': search_query,
		'selected_date_range': date_range,
	}
	return render(request, 'users/profile_likes.html', context)
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
# Delete user's own comment
@login_required
def user_delete_comment(request, pk):
	comment = Comment.objects.filter(pk=pk, author=request.user).first()
	if not comment:
		messages.error(request, 'You do not have permission to delete this comment.')
		return redirect('user_my_comments')
	comment.delete()
	messages.success(request, 'Comment deleted successfully!')
	return redirect('user_my_comments')
from django.contrib.auth.decorators import login_required

@login_required
def admin_likes(request):
	if not request.user.is_staff:
		messages.error(request, 'You do not have permission.')
		return redirect('home')

	User = get_user_model()
	likes = Like.objects.select_related('user', 'post').order_by('-created_at')

	# Filters
	user_id = request.GET.get('user', '')
	post_id = request.GET.get('post', '')
	date_range = request.GET.get('date_range', '')

	if user_id:
		likes = likes.filter(user_id=user_id)
	if post_id:
		likes = likes.filter(post_id=post_id)
	if date_range:
		today = datetime.now().date()
		if date_range == 'today':
			likes = likes.filter(created_at__date=today)
		elif date_range == 'week':
			start_date = today - timedelta(days=7)
			likes = likes.filter(created_at__date__gte=start_date)
		elif date_range == 'month':
			start_date = today - timedelta(days=30)
			likes = likes.filter(created_at__date__gte=start_date)
		elif date_range == 'year':
			start_date = today - timedelta(days=365)
			likes = likes.filter(created_at__date__gte=start_date)

	users = User.objects.all().order_by('username')
	posts = Post.objects.all().order_by('title')
	context = {
		'likes': likes,
		'users': users,
		'posts': posts,
		'selected_user': user_id,
		'selected_post': post_id,
		'selected_date_range': date_range,
	}
	return render(request, 'admin/likes.html', context)
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Prefetch, Q
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST
from datetime import datetime, timedelta

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
	posts = Post.objects.filter(author=request.user).select_related('category').prefetch_related('comments', 'likes', 'tags')
	
	# Search functionality
	search_query = request.GET.get('q', '').strip()
	if search_query:
		posts = posts.filter(
			Q(title__icontains=search_query) | 
			Q(content__icontains=search_query)
		)
	
	# Filter by category
	category_id = request.GET.get('category', '')
	if category_id:
		try:
			posts = posts.filter(category_id=int(category_id))
		except (ValueError, TypeError):
			pass
	
	# Filter by status
	status_filter = request.GET.get('status', '')
	if status_filter in ['draft', 'published']:
		posts = posts.filter(status=status_filter)
	
	# Filter by date range
	date_range = request.GET.get('date_range', '')
	if date_range:
		today = datetime.now().date()
		if date_range == 'today':
			posts = posts.filter(created_at__date=today)
		elif date_range == 'week':
			start_date = today - timedelta(days=7)
			posts = posts.filter(created_at__date__gte=start_date)
		elif date_range == 'month':
			start_date = today - timedelta(days=30)
			posts = posts.filter(created_at__date__gte=start_date)
		elif date_range == 'year':
			start_date = today - timedelta(days=365)
			posts = posts.filter(created_at__date__gte=start_date)
	
	# Ordering
	order_by = request.GET.get('order_by', '-created_at')
	if order_by in ['-created_at', 'created_at', '-updated_at', 'updated_at', 'title']:
		posts = posts.order_by(order_by)
	else:
		posts = posts.order_by('-created_at')
	
	categories = Category.objects.all().order_by('name')
	# Sidebar context
	from posts.models import Comment, Like, Post as PostModel
	my_comments = Comment.objects.filter(author=request.user).select_related('post').order_by('-created_at')[:5]
	liked_post_ids = Like.objects.filter(user=request.user).order_by('-created_at').values_list('post_id', flat=True)[:5]
	liked_posts = PostModel.objects.filter(id__in=liked_post_ids)
	context = {
		'posts': posts,
		'categories': categories,
		'search_query': search_query,
		'selected_category': category_id,
		'selected_status': status_filter,
		'selected_date_range': date_range,
		'selected_order': order_by,
		'my_comments': my_comments,
		'liked_posts': liked_posts,
	}
	return render(request, 'users/profile_posts.html', context)

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

	User = get_user_model()
	comments = Comment.objects.select_related('author', 'post').order_by('-created_at')

	# Filters
	user_id = request.GET.get('user', '')
	post_id = request.GET.get('post', '')
	date_range = request.GET.get('date_range', '')

	if user_id:
		comments = comments.filter(author_id=user_id)
	if post_id:
		comments = comments.filter(post_id=post_id)
	if date_range:
		today = datetime.now().date()
		if date_range == 'today':
			comments = comments.filter(created_at__date=today)
		elif date_range == 'week':
			start_date = today - timedelta(days=7)
			comments = comments.filter(created_at__date__gte=start_date)
		elif date_range == 'month':
			start_date = today - timedelta(days=30)
			comments = comments.filter(created_at__date__gte=start_date)
		elif date_range == 'year':
			start_date = today - timedelta(days=365)
			comments = comments.filter(created_at__date__gte=start_date)

	users = User.objects.all().order_by('username')
	posts = Post.objects.all().order_by('title')
	context = {
		'comments': comments,
		'users': users,
		'posts': posts,
		'selected_user': user_id,
		'selected_post': post_id,
		'selected_date_range': date_range,
	}
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