
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Count, Q
from datetime import datetime, timedelta
from accounts.models import UserProfile
from posts.models import Comment, Like, Post, Category


def user_register(request):
	"""User registration view without forms.py"""
	if request.user.is_authenticated:
		return redirect('home')
	
	from posts.models import SiteSettings
	settings_obj = SiteSettings.load()
	
	if not settings_obj.allow_registration:
		messages.error(request, 'User registration is currently disabled by the administrator.')
		return redirect('home')
	
	if request.method == 'POST':
		username = request.POST.get('username')
		email = request.POST.get('email')
		first_name = request.POST.get('first_name', '')
		last_name = request.POST.get('last_name', '')
		password1 = request.POST.get('password1')
		password2 = request.POST.get('password2')

		if not username or not email or not password1 or not password2:
			messages.error(request, 'All required fields must be filled.')
			return render(request, 'accounts/register.html')

		if password1 != password2:
			messages.error(request, 'Passwords do not match.')
			return render(request, 'accounts/register.html')

		from django.contrib.auth.models import User
		if User.objects.filter(username=username).exists():
			messages.error(request, 'Username already taken.')
			return render(request, 'accounts/register.html')

		if User.objects.filter(email=email).exists():
			messages.error(request, 'Email already registered.')
			return render(request, 'accounts/register.html')

		user = User.objects.create_user(
			username=username,
			email=email,
			password=password1,
			first_name=first_name,
			last_name=last_name
		)
		messages.success(request, f'Account created successfully! Welcome, {username}!')
		login(request, user)
		return redirect('home')
	
	return render(request, 'accounts/register.html')


def user_login(request):
	"""User login view without forms.py"""
	if request.user.is_authenticated:
		return redirect('home')
	
	if request.method == 'POST':
		username = request.POST.get('username')
		password = request.POST.get('password')
		
		if not username or not password:
			messages.error(request, 'Both username and password are required.')
			return render(request, 'accounts/login.html')

		user = authenticate(username=username, password=password)
		if user is not None:
			login(request, user)
			messages.success(request, f'Welcome back, {username}!')
			next_url = request.GET.get('next', 'home')
			return redirect(next_url)
		else:
			messages.error(request, 'Invalid username or password.')
	
	return render(request, 'accounts/login.html')


def user_logout(request):
	"""User logout view"""
	logout(request)
	messages.info(request, 'You have been logged out successfully.')
	return redirect('home')


def home(request):
	from posts.models import Post, Category, Like, SiteSettings
	from django.db.models import Count
	
	settings_obj = SiteSettings.load()
	
	# Get published posts with related data
	latest_posts = Post.objects.filter(status=Post.STATUS_PUBLISHED).select_related('author', 'category').prefetch_related('comments', 'likes').order_by('-created_at')[:settings_obj.posts_per_page]
	
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
		'site_settings': settings_obj,
	}
	return render(request, 'pages/home.html', context)


@login_required
def admin_dashboard(request):
	if not request.user.is_staff:
		messages.error(request, 'You do not have permission to access the admin dashboard.')
		return redirect('home')

	from posts.models import Comment, Like, Post, Category, Tag
	from django.contrib.auth import get_user_model
	User = get_user_model()

	# Core stats
	total_posts = Post.objects.count()
	total_comments = Comment.objects.count()
	total_likes = Like.objects.count()
	total_users = User.objects.count()
	total_categories = Category.objects.count()
	total_tags = Tag.objects.count()
	published_posts = Post.objects.filter(status=Post.STATUS_PUBLISHED).count()
	draft_posts = Post.objects.filter(status='draft').count()

	# Recent activity (last 7 days)
	now = datetime.now()
	week_ago = now - timedelta(days=7)
	day_ago = now - timedelta(days=1)
	
	new_posts_week = Post.objects.filter(created_at__gte=week_ago).count()
	new_comments_week = Comment.objects.filter(created_at__gte=week_ago).count()
	new_users_week = User.objects.filter(date_joined__gte=week_ago).count()
	
	posts_last_24h = Post.objects.filter(created_at__gte=day_ago).count()
	comments_last_24h = Comment.objects.filter(created_at__gte=day_ago).count()

	# Top posts by likes
	top_posts = Post.objects.annotate(
		like_count=Count('likes'),
		comment_count=Count('comments')
	).order_by('-like_count')[:5]

	# Recent posts
	recent_posts = Post.objects.select_related('author', 'category').order_by('-created_at')[:5]

	# Recent comments
	recent_comments = Comment.objects.select_related('author', 'post').order_by('-created_at')[:5]

	# Most active users
	top_authors = User.objects.annotate(
		post_count=Count('posts')
	).filter(post_count__gt=0).order_by('-post_count')[:5]

	# Newest users
	newest_users = User.objects.order_by('-date_joined')[:5]

	# Interaction rate
	interaction_rate = 0.0
	if total_posts > 0:
		interaction_rate = (total_comments + total_likes) / total_posts

	context = {
		'total_posts': total_posts,
		'total_comments': total_comments,
		'total_likes': total_likes,
		'total_users': total_users,
		'total_categories': total_categories,
		'total_tags': total_tags,
		'published_posts': published_posts,
		'draft_posts': draft_posts,
		'new_posts_week': new_posts_week,
		'new_comments_week': new_comments_week,
		'new_users_week': new_users_week,
		'posts_last_24h': posts_last_24h,
		'comments_last_24h': comments_last_24h,
		'interaction_rate': interaction_rate,
		'top_posts': top_posts,
		'recent_posts': recent_posts,
		'recent_comments': recent_comments,
		'top_authors': top_authors,
		'newest_users': newest_users,
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
	"""Display user profile overview"""
	user_post_count = Post.objects.filter(author=request.user).count()
	user_like_count = Like.objects.filter(user=request.user).count()
	user_comment_count = Comment.objects.filter(author=request.user).count()

	my_comments = Comment.objects.filter(author=request.user).select_related('post').order_by('-created_at')[:5]
	liked_post_ids = Like.objects.filter(user=request.user).order_by('-created_at').values_list('post_id', flat=True)[:5]
	liked_posts = Post.objects.filter(id__in=liked_post_ids)

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
	"""Profile settings — edit info, change password"""
	profile = getattr(request.user, 'profile', None)
	my_comments = Comment.objects.filter(author=request.user).select_related('post').order_by('-created_at')[:5]
	liked_post_ids = Like.objects.filter(user=request.user).order_by('-created_at').values_list('post_id', flat=True)[:5]
	liked_posts = Post.objects.filter(id__in=liked_post_ids)

	if request.method == 'POST':
		action = request.POST.get('action')

		# ── Update profile info ──────────────────────────────────────
		if action == 'update_profile':
			first_name = request.POST.get('first_name', '').strip()
			last_name  = request.POST.get('last_name', '').strip()
			email      = request.POST.get('email', '').strip()
			bio        = request.POST.get('bio', '').strip()
			location   = request.POST.get('location', '').strip()
			website    = request.POST.get('website', '').strip()
			twitter    = request.POST.get('twitter', '').strip()
			github     = request.POST.get('github', '').strip()
			linkedin   = request.POST.get('linkedin', '').strip()
			email_notif = request.POST.get('email_notifications') == 'on'
			# newsletter_subscription removed

			# Update User fields
			request.user.first_name = first_name
			request.user.last_name  = last_name
			if email and email != request.user.email:
				from django.contrib.auth import get_user_model
				User = get_user_model()
				if User.objects.filter(email=email).exclude(pk=request.user.pk).exists():
					messages.error(request, 'An account with that email already exists.')
					return redirect('profile_settings')
			request.user.email = email
			request.user.save()

			# Update UserProfile fields
			if profile:
				profile.bio      = bio
				profile.location = location
				profile.website  = website
				profile.twitter  = twitter
				profile.github   = github
				profile.linkedin = linkedin
				profile.email_notifications      = email_notif
				# newsletter_subscription removed
				if 'avatar' in request.FILES:
					profile.avatar = request.FILES['avatar']
				profile.save()

			messages.success(request, 'Profile updated successfully!')
			return redirect('profile_settings')

		# ── Change password ──────────────────────────────────────────
		elif action == 'change_password':
			old_password = request.POST.get('old_password')
			new_password1 = request.POST.get('new_password1')
			new_password2 = request.POST.get('new_password2')

			if not old_password or not new_password1 or not new_password2:
				messages.error(request, 'All password fields are required.')
				return redirect('profile_settings')

			if not request.user.check_password(old_password):
				messages.error(request, 'Incorrect current password.')
				return redirect('profile_settings')

			if new_password1 != new_password2:
				messages.error(request, 'New passwords do not match.')
				return redirect('profile_settings')
			
			if len(new_password1) < 8:
				messages.error(request, 'Password must be at least 8 characters long.')
				return redirect('profile_settings')

			request.user.set_password(new_password1)
			request.user.save()
			update_session_auth_hash(request, request.user)  # Keep user logged in
			messages.success(request, 'Password changed successfully!')
			return redirect('profile_settings')

	context = {
		'profile': profile,
		'my_comments': my_comments,
		'liked_posts': liked_posts,
	}
	return render(request, 'users/profile_settings.html', context)


def user_management(request):
	if not request.user.is_staff:
		messages.error(request, 'You do not have permission to access user management.')
		return redirect('home')
	
	users = UserProfile.objects.annotate(
		post_count=Count('user__posts'),
		comment_count=Count('user__comments'),
		like_count=Count('user__likes')
	).select_related('user').order_by('-created_at')

	search_query = request.GET.get('q', '').strip()
	if search_query:
		users = users.filter(
			Q(user__username__icontains=search_query) |
			Q(user__email__icontains=search_query) |
			Q(user__first_name__icontains=search_query) |
			Q(user__last_name__icontains=search_query)
		)
	
	joined_date_from = request.GET.get('joined_date_from')
	joined_date_to = request.GET.get('joined_date_to')
	if joined_date_from:
		users = users.filter(user__date_joined__gte=joined_date_from)
		if joined_date_to:
			users = users.filter(user__date_joined__lte=joined_date_to)

	from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
	paginator = Paginator(users, 10)  # 10 users per page
	page = request.GET.get('page')
	try:
		users_page = paginator.page(page)
	except PageNotAnInteger:
		users_page = paginator.page(1)
	except EmptyPage:
		users_page = paginator.page(paginator.num_pages)

	context = {
		'users': users_page,
		'page_obj': users_page,
		'paginator': paginator,
	}
	return render(request, 'admin/user_management.html', context)

def admin_delete_user(request, user_id):
	"""Admin view to delete a user"""
	if not request.user.is_staff:
		messages.error(request, 'You do not have permission to perform this action.')
		return redirect('home')

	from django.contrib.auth import get_user_model
	User = get_user_model()
	user_to_delete = UserProfile.objects.filter(id=user_id).first()

	if not user_to_delete:
		messages.error(request, 'User not found.')
		return redirect('user_management')

	if user_to_delete == request.user:
		messages.error(request, 'You cannot delete your own account.')
		return redirect('user_management')

	user_to_delete.delete()
	messages.success(request, f'User {user_to_delete.username} has been deleted.')
	return redirect('user_management')