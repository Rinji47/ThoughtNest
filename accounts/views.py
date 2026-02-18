from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import UserRegistrationForm, UserLoginForm
from posts.models import Comment, Like, Post, Category
from django.db.models import Count


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
	return render(request, 'pages/home.html')


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
	user_posts = Post.objects.filter(author=request.user).order_by('-created_at')
	user_post_count = user_posts.count()
	user_like_count = Like.objects.filter(user=request.user).count()
	user_comment_count = Comment.objects.filter(author=request.user).count()
	
	context = {
		'user_posts': user_posts,
		'user_post_count': user_post_count,
		'user_like_count': user_like_count,
		'user_comment_count': user_comment_count,
	}
	return render(request, 'pages/profile.html', context)