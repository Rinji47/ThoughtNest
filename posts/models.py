from django.conf import settings
from django.db import models
from django.utils.text import slugify


class Category(models.Model):
	name = models.CharField(max_length=120, unique=True)
	created_at = models.DateTimeField(auto_now_add=True)

	class Meta:
		ordering = ['name']
		verbose_name_plural = 'categories'

	# Removed slug logic

	def __str__(self):
		return self.name


class Tag(models.Model):
	name = models.CharField(max_length=80, unique=True)
	created_at = models.DateTimeField(auto_now_add=True)

	class Meta:
		ordering = ['name']

	# Removed slug logic

	def __str__(self):
		return self.name


class Post(models.Model):
	STATUS_DRAFT = 'draft'
	STATUS_PUBLISHED = 'published'
	STATUS_CHOICES = [
		(STATUS_DRAFT, 'Draft'),
		(STATUS_PUBLISHED, 'Published'),
	]

	author = models.ForeignKey(
		settings.AUTH_USER_MODEL,
		on_delete=models.CASCADE,
		related_name='posts',
	)
	category = models.ForeignKey(
		Category,
		on_delete=models.SET_NULL,
		null=True,
		blank=True,
		related_name='posts',
	)
	tags = models.ManyToManyField(Tag, blank=True, related_name='posts')
	title = models.CharField(max_length=200)
	content = models.TextField()
	status = models.CharField(
		max_length=20,
		choices=STATUS_CHOICES,
		default=STATUS_PUBLISHED,
	)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	class Meta:
		ordering = ['-created_at']

	# Removed slug logic

	def __str__(self):
		return self.title


class Comment(models.Model):
	post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
	author = models.ForeignKey(
		settings.AUTH_USER_MODEL,
		on_delete=models.SET_NULL,
		null=True,
		blank=True,
		related_name='comments',
	)
	content = models.TextField()
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)
	approved = models.BooleanField(default=True)

	class Meta:
		ordering = ['-created_at']

	def __str__(self):
		return f"Comment on {self.post_id}"


class Like(models.Model):
	post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='likes')
	user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='likes')
	created_at = models.DateTimeField(auto_now_add=True)

	class Meta:
		constraints = [
			models.UniqueConstraint(fields=['post', 'user'], name='unique_like_per_user'),
		]

	def __str__(self):
		return f"Like {self.post_id} by {self.user_id}"

class SiteSettings(models.Model):
	site_name = models.CharField(max_length=100, default='ThoughtNest')
	site_tagline = models.CharField(max_length=200, default='Gather ideas. Grow perspectives.')
	site_description = models.TextField(blank=True)
	contact_email = models.EmailField(blank=True)
	posts_per_page = models.PositiveIntegerField(default=12)
	excerpt_length = models.PositiveIntegerField(default=25)
	allow_comments = models.BooleanField(default=True)
	moderate_comments = models.BooleanField(default=False)
	allow_registration = models.BooleanField(default=True)
	show_author = models.BooleanField(default=True)

	def __str__(self):
		return "Site Settings"

	class Meta:
		verbose_name = "Site Settings"
		verbose_name_plural = "Site Settings"

	@classmethod
	def load(cls):
		obj, created = cls.objects.get_or_create(pk=1)
		return obj
