from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Count, Q
from datetime import datetime, timedelta
from .forms import UserRegistrationForm, UserLoginForm
from posts.models import Comment, Like, Post, Category


def user_register(request):
	"""User registration view"""
	if request.user.is_authenticated:
		return redirect('home')
	
	if request.method == 'POST':
		form = UserRegistrationForm(request.POST)
		if form.is_valid():
			user = form.save()
			username = form.cleaned_data.get('username')
			messages.success(request, f'Account created successfully! Welcome, {username}!')
			login(request, user)
			return redirect('home')
		else:
			messages.error(request, 'Please correct the errors below.')
	else:
		form = UserRegistrationForm()
	
	return render(request, 'accounts/register.html', {'form': form})


def user_login(request):
	"""User login view"""
	if request.user.is_authenticated:
		return redirect('home')
	
	if request.method == 'POST':
		form = UserLoginForm(request, data=request.POST)
		if form.is_valid():
			username = form.cleaned_data.get('username')
			password = form.cleaned_data.get('password')
			user = authenticate(username=username, password=password)
			if user is not None:
				login(request, user)
				messages.success(request, f'Welcome back, {username}!')
				next_url = request.GET.get('next', 'home')
				return redirect(next_url)
		else:
			messages.error(request, 'Invalid username or password.')
	else:
		form = UserLoginForm()
	
	return render(request, 'accounts/login.html', {'form': form})


def user_logout(request):
	"""User logout view"""
	logout(request)
	messages.info(request, 'You have been logged out successfully.')
	return redirect('home')


def home(request):
	from posts.models import Post, Category, Like
	from django.db.models import Count
	
	# Get published posts with related data
	latest_posts = Post.objects.filter(status=Post.STATUS_PUBLISHED).select_related('author', 'category').prefetch_related('comments', 'likes').order_by('-created_at')[:12]
	
	# Get all categories with post counts
	categories = Category.objects.annotate(post_count=Count('posts')).order_by('-post_count')[:5]
	
	# Check which posts the user has liked
	user_liked_posts = set()
	if request.user.is_authenticated:
		user_liked_posts = set(Like.objects.filter(user=request.user, post__in=latest_posts).values_list('post_id', flat=True))
	
	# Add user_has_liked attribute to each post
	for post in latest_posts:
		post.user_has_liked = post.id in user_liked_posts
	
	context = {
		'latest_posts': latest_posts,
		'categories': categories,
		'total_posts': Post.objects.filter(status=Post.STATUS_PUBLISHED).count(),
	}
	return render(request, 'pages/home.html', context)


@login_required
def admin_dashboard(request):
	if not request.user.is_staff:
		messages.error(request, 'You do not have permission to access the admin dashboard.')
		return redirect('home')

	from posts.models import Comment, Like, Post
	posts = Post.objects.select_related('author', 'category').prefetch_related('comments', 'likes')
	context = {
		'total_posts': posts.count(),
		'total_comments': Comment.objects.count(),
		'total_likes': Like.objects.count(),
	}

	return render(request, 'admin/admin_dashboard.html', context)


@login_required
def admin_page(request):
	if not request.user.is_staff:
		messages.error(request, 'You do not have permission to access the admin dashboard.')
		return redirect('home')

	return redirect('admin_dashboard')




@login_required

def profile(request):
	"""Display user profile overview with recent comments and liked posts for sidebar"""
	user_post_count = Post.objects.filter(author=request.user).count()
	user_like_count = Like.objects.filter(user=request.user).count()
	user_comment_count = Comment.objects.filter(author=request.user).count()

	# Recent comments (limit 5)
	my_comments = Comment.objects.filter(author=request.user).select_related('post').order_by('-created_at')[:5]
	# Recent liked posts (limit 5, most recent likes)
	liked_post_ids = Like.objects.filter(user=request.user).order_by('-created_at').values_list('post_id', flat=True)[:5]
	liked_posts = Post.objects.filter(id__in=liked_post_ids)

	# User profile info
	profile = getattr(request.user, 'profile', None)
	bio = profile.bio if profile else ''
	location = profile.location if profile else ''
	website = profile.website if profile else ''

	context = {
		'user_post_count': user_post_count,
		'user_like_count': user_like_count,
		'user_comment_count': user_comment_count,
		'my_comments': my_comments,
		'liked_posts': liked_posts,
		'bio': bio,
		'location': location,
		'website': website,
		'profile': profile,
	}
	return render(request, 'users/profile_overview.html', context)


@login_required

def profile_settings(request):
	"""Display user profile settings with sidebar context"""
	# Sidebar context
	my_comments = Comment.objects.filter(author=request.user).select_related('post').order_by('-created_at')[:5]
	liked_post_ids = Like.objects.filter(user=request.user).order_by('-created_at').values_list('post_id', flat=True)[:5]
	liked_posts = Post.objects.filter(id__in=liked_post_ids)
	context = {
		'my_comments': my_comments,
		'liked_posts': liked_posts,
	}
	return render(request, 'users/profile_settings.html', context)