from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Prefetch, Q
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST
from datetime import datetime, timedelta
from django.core.paginator import Paginator

from .models import Category, Comment, Like, Post, Tag, SiteSettings



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

    # Pagination: 10 comments per page
    page_number = request.GET.get('page', 1)
    paginator = Paginator(comments, 10)
    page_obj = paginator.get_page(page_number)

    context = {
        'comments': page_obj,
        'posts': posts,
        'search_query': search_query,
        'selected_post': post_id,
        'selected_date_range': date_range,
        'paginator': paginator,
        'page_obj': page_obj,
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

    # Pagination: 10 likes per page
    page_number = request.GET.get('page', 1)
    paginator = Paginator(likes, 10)
    page_obj = paginator.get_page(page_number)

    context = {
        'likes': page_obj,
        'search_query': search_query,
        'selected_date_range': date_range,
        'paginator': paginator,
        'page_obj': page_obj,
    }
    return render(request, 'users/profile_likes.html', context)


@login_required
def user_delete_comment(request, pk):
	comment = Comment.objects.filter(pk=pk, author=request.user).first()
	if not comment:
		messages.error(request, 'You do not have permission to delete this comment.')
		return redirect('user_my_comments')
	comment.delete()
	messages.success(request, 'Comment deleted successfully!')
	return redirect('user_my_comments')

@login_required
def admin_likes(request):
    if not request.user.is_staff:
        messages.error(request, 'You do not have permission.')
        return redirect('home')

    User = get_user_model()
    likes = Like.objects.select_related('user', 'post').order_by('-created_at')

    # Filters
    user_search = request.GET.get('user_search', '').strip()  # Filter by username / name
    post_id = request.GET.get('post', '')
    date_range = request.GET.get('date_range', '')

    if user_search:
        likes = likes.filter(
            Q(user__username__icontains=user_search) |
            Q(user__first_name__icontains=user_search) |
            Q(user__last_name__icontains=user_search)
        )

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

    posts = Post.objects.all().order_by('title')

    # Pagination: 15 likes per page
    page_number = request.GET.get('page', 1)
    paginator = Paginator(likes, 15)
    page_obj = paginator.get_page(page_number)

    context = {
        'likes': page_obj,
        'posts': posts,
        'selected_post': post_id,
        'selected_date_range': date_range,
        'user_search': user_search,  # pass it to template
        'paginator': paginator,
        'page_obj': page_obj,
    }

    return render(request, 'admin/likes.html', context)


def categories(request):
    # Categories with post counts
    categories_list = Category.objects.annotate(post_count=Count('posts')).order_by('-post_count', 'name')
    for cat in categories_list:
        cat.recent_posts = cat.posts.filter(status=Post.STATUS_PUBLISHED).select_related('author').order_by('-created_at')[:2]

    # Tags with post counts
    tags_qs = Tag.objects.annotate(post_count=Count('posts')).order_by('-post_count', 'name')

    # Convert QuerySet to list of dicts for JSON serialization
    tags_list = list(tags_qs.values('id', 'name'))

    # Site settings
    settings_obj = SiteSettings.load()

    context = {
        'categories': categories_list,
        'tags': tags_qs,           # for displaying tags in template
        'all_tags_json': tags_list, # for JS search
        'site_settings': settings_obj,
    }
    return render(request, 'pages/categories.html', context)


def post_detail(request, pk):
	from .models import SiteSettings
	settings_obj = SiteSettings.load()
	
	post = get_object_or_404(Post.objects.prefetch_related('tags'), pk=pk)
	comments = post.comments.filter(approved=True).select_related('author')
	user_has_liked = False
	if request.user.is_authenticated:
		user_has_liked = Like.objects.filter(post=post, user=request.user).exists()
	
	context = {
		'post': post, 
		'comments': comments, 
		'user_has_liked': user_has_liked,
		'site_settings': settings_obj,
	}
	return render(request, 'posts/post_detail.html', context)


@login_required
def post_create(request):
    if request.method == 'POST':
        title = request.POST.get('title', '').strip()
        category_id = request.POST.get('category')
        tags_input = request.POST.get('tags', '').strip()
        content = request.POST.get('content', '').strip()
        status = request.POST.get('status', Post.STATUS_PUBLISHED)
        # featured_image removed

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
            # featured_image removed
        )

        # Handle tags
        if tags_input:
            tag_names = [tag.strip().lstrip("#") for tag in tags_input.split(',')]
            for tag_name in tag_names:
                if tag_name:
                    tag, _ = Tag.objects.get_or_create(name=tag_name)
                    post.tags.add(tag)

        messages.success(request, 'Post created successfully!')
        return redirect('post_detail', pk=post.pk)

    # Context for GET request / rendering form
    context = {
        'mode': 'create',
        'categories': Category.objects.all(),
        'popular_tags': Tag.objects.annotate(post_count=Count('posts')).order_by('-post_count', 'name')[:10],  # top 10 popular
        'all_tags': Tag.objects.all().order_by('name'),  # fetch all for search/autocomplete later
        'all_tag_names': list(Tag.objects.order_by('name').values_list('name', flat=True)),  # for JS
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
		
		# featured_image removed

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
	from .models import SiteSettings
	settings_obj = SiteSettings.load()
	
	if not settings_obj.allow_comments:
		messages.error(request, 'Commenting is currently disabled site-wide.')
		return redirect('post_detail', pk=pk)
		
	post = get_object_or_404(Post, pk=pk)
	content = (request.POST.get('content') or '').strip()
	if not content:
		messages.error(request, 'Comment cannot be empty.')
		return redirect('post_detail', pk=post.pk)

	approved = not settings_obj.moderate_comments
	Comment.objects.create(post=post, author=request.user, content=content, approved=approved)
	
	if approved:
		messages.success(request, 'Comment added.')
	else:
		messages.success(request, 'Comment submitted and awaiting moderation.')
		
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
    
    # Pagination: 10 posts per page
    page_number = request.GET.get('page', 1)
    paginator = Paginator(posts, 10)
    page_obj = paginator.get_page(page_number)
    
    # Categories for filter dropdown
    categories = Category.objects.all().order_by('name')
    
    # Sidebar context
    my_comments = Comment.objects.filter(author=request.user).select_related('post').order_by('-created_at')[:5]
    liked_post_ids = Like.objects.filter(user=request.user).order_by('-created_at').values_list('post_id', flat=True)[:5]
    liked_posts = Post.objects.filter(id__in=liked_post_ids)
    
    context = {
        'posts': page_obj,  # paginated posts
        'paginator': paginator,
        'page_obj': page_obj,
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

@login_required
def admin_posts(request):
    if not request.user.is_staff:
        messages.error(request, 'You do not have permission.')
        return redirect('home')

    # Base queryset
    posts = Post.objects.select_related('author', 'category').prefetch_related('comments', 'likes').order_by('-created_at')

    # Filters
    search_query = request.GET.get('search', '').strip()
    category_id = request.GET.get('category', '').strip()
    status = request.GET.get('status', '').strip()

    if search_query:
        posts = posts.filter(
            Q(title__icontains=search_query) |
            Q(author__username__icontains=search_query) |
            Q(author__first_name__icontains=search_query) |
            Q(author__last_name__icontains=search_query)
        )

    if category_id:
        posts = posts.filter(category_id=category_id)
    if status:
        posts = posts.filter(status=status)

    categories = Category.objects.all().order_by('name')

    # Pagination: 15 posts per page
    page_number = request.GET.get('page', 1)
    paginator = Paginator(posts, 15)
    page_obj = paginator.get_page(page_number)

    context = {
        'posts': page_obj,
        'categories': categories,
        'search_query': search_query,
        'selected_category': category_id,
        'selected_status': status,
        'paginator': paginator,
        'page_obj': page_obj,
        'request': request  # for template GET access
    }
    return render(request, 'admin/posts.html', context)


@login_required
def admin_comments(request):
    if not request.user.is_staff:
        messages.error(request, 'You do not have permission.')
        return redirect('home')

    User = get_user_model()
    comments = Comment.objects.select_related('author', 'post').order_by('-created_at')

    # Filters
    user_search = request.GET.get('user_search', '').strip()
    post_id = request.GET.get('post', '')
    date_range = request.GET.get('date_range', '')

    # Filter by user search (username or first/last name)
    if user_search:
        comments = comments.filter(
            Q(author__username__icontains=user_search) |
            Q(author__first_name__icontains=user_search) |
            Q(author__last_name__icontains=user_search)
        )

    # Filter by post
    if post_id:
        comments = comments.filter(post_id=post_id)

    # Filter by date range
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

    posts = Post.objects.all().order_by('title')

    # Pagination: 15 comments per page
    page_number = request.GET.get('page', 1)
    paginator = Paginator(comments, 15)
    page_obj = paginator.get_page(page_number)

    context = {
        'comments': page_obj,
        'posts': posts,
        'user_search': user_search,
        'selected_post': post_id,
        'selected_date_range': date_range,
        'paginator': paginator,
        'page_obj': page_obj,
    }

    return render(request, 'admin/comments.html', context)


@login_required
def admin_settings(request):
	if not request.user.is_staff:
		messages.error(request, 'You do not have permission.')
		return redirect('home')
	
	from .models import SiteSettings
	settings_obj = SiteSettings.load()

	if request.method == 'POST':
		action = request.POST.get('action')
		
		if action == 'site_info':
			settings_obj.site_name = request.POST.get('site_name', 'ThoughtNest')
			settings_obj.site_tagline = request.POST.get('site_tagline', '')
			settings_obj.site_description = request.POST.get('site_description', '')
			settings_obj.contact_email = request.POST.get('contact_email', '')
			settings_obj.save()
			messages.success(request, 'Site information updated successfully!')
		
		elif action == 'content_settings':
			try:
				settings_obj.posts_per_page = int(request.POST.get('posts_per_page', 12))
				settings_obj.excerpt_length = int(request.POST.get('excerpt_length', 25))
			except ValueError:
				messages.error(request, 'Invalid numeric values for content settings.')
				return redirect('admin_settings')
				
			settings_obj.allow_comments = request.POST.get('allow_comments') == 'on'
			settings_obj.moderate_comments = request.POST.get('moderate_comments') == 'on'
			settings_obj.allow_registration = request.POST.get('allow_registration') == 'on'
			settings_obj.show_author = request.POST.get('show_author') == 'on'
			settings_obj.save()
			messages.success(request, 'Content settings updated successfully!')
		
		elif action == 'clear_comments':
			from .models import Comment
			Comment.objects.all().delete()
			messages.success(request, 'All comments have been cleared.')
		
		return redirect('admin_settings')
	
	context = {
		'site_settings': settings_obj
	}
	return render(request, 'admin/settings.html', context)


@login_required
def admin_categories(request):
    if not request.user.is_staff:
        messages.error(request, 'You do not have permission.')
        return redirect('home')

    # Get search query and page number
    category_search = request.GET.get('category_search', '').strip()
    page_number = request.GET.get('page', 1)

    # Base queryset with post count
    categories = Category.objects.annotate(post_count=Count('posts')).order_by('-created_at')

    # Apply search filter
    if category_search:
        categories = categories.filter(name__icontains=category_search)

    # Pagination: 15 categories per page
    paginator = Paginator(categories, 15)
    page_obj = paginator.get_page(page_number)

    context = {
        'categories': page_obj,
        'category_search': category_search,
        'paginator': paginator,
        'page_obj': page_obj,
    }
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

def tag_posts(request, pk):
    tag = get_object_or_404(Tag, pk=pk)
    
    posts = Post.objects.filter(
        tags=tag, 
        status=Post.STATUS_PUBLISHED
    ).select_related('author', 'category').order_by('-created_at')
    
    search_query = request.GET.get('q', '').strip()
    if search_query:
        posts = posts.filter(title__icontains=search_query)
    
    context = {
        'tag': tag,
        'posts': posts,
        'search_query': search_query,
    }
    
    return render(request, 'pages/tag_posts.html', context)

def category_posts(request, pk):
    category = get_object_or_404(Category, pk=pk)
    
    posts = Post.objects.filter(
        category=category,
        status=Post.STATUS_PUBLISHED
    ).select_related('author').order_by('-created_at')
    
    search_query = request.GET.get('q', '').strip() 
    if search_query:
        posts = posts.filter(title__icontains=search_query)
    
    context = {
        'category': category,
        'posts': posts,
        'search_query': search_query,
    }
    
    return render(request, 'pages/category_posts.html', context)

def admin_delete_comment(request, pk):
	if not request.user.is_staff:
		messages.error(request, 'You do not have permission.')
		return redirect('home')
	
	comment = get_object_or_404(Comment, pk=pk)
	comment.delete()
	messages.success(request, 'Comment deleted successfully!')
	return redirect('admin_comments')

def admin_delete_tag(request, pk):
	if not request.user.is_staff:
		messages.error(request, 'You do not have permission.')
		return redirect('home')
	
	tag = get_object_or_404(Tag, pk=pk)
	tag.delete()
	messages.success(request, 'Tag deleted successfully!')
	return redirect('admin_tags')

@login_required
def admin_tags(request):
    if not request.user.is_staff:
        messages.error(request, 'You do not have permission.')
        return redirect('home')

    tag_search = request.GET.get('tag_search', '').strip()
    date_from = request.GET.get('date_from', '')
    date_to = request.GET.get('date_to', '')
    page_number = request.GET.get('page', 1)

    tags = Tag.objects.all()

    if tag_search:
        tags = tags.filter(name__icontains=tag_search)

    if date_from:
        tags = tags.filter(created_at__date__gte=date_from)
    if date_to:
        tags = tags.filter(created_at__date__lte=date_to)

    tags = tags.annotate(post_count=Count('posts')).order_by('-created_at')

    # Pagination: 15 tags per page
    paginator = Paginator(tags, 15)
    page_obj = paginator.get_page(page_number)

    context = {
        'tags': page_obj,
        'tag_search': tag_search,
        'date_from': date_from,
        'date_to': date_to,
        'paginator': paginator,
        'page_obj': page_obj,
    }
    return render(request, 'admin/tags.html', context)