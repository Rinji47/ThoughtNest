from django.conf import settings
from django.db import models
from django.utils.text import slugify
from django_quill.fields import QuillField


class Category(models.Model):
	name = models.CharField(max_length=120, unique=True)
	slug = models.SlugField(max_length=140, unique=True, blank=True)
	created_at = models.DateTimeField(auto_now_add=True)

	class Meta:
		ordering = ['name']
		verbose_name_plural = 'categories'

	def save(self, *args, **kwargs):
		if not self.slug:
			base_slug = slugify(self.name)[:130] or 'category'
			slug = base_slug
			counter = 1
			while Category.objects.filter(slug=slug).exclude(pk=self.pk).exists():
				slug = f"{base_slug}-{counter}"
				counter += 1
			self.slug = slug
		super().save(*args, **kwargs)

	def __str__(self):
		return self.name


class Tag(models.Model):
	name = models.CharField(max_length=80, unique=True)
	slug = models.SlugField(max_length=100, unique=True, blank=True)
	created_at = models.DateTimeField(auto_now_add=True)

	class Meta:
		ordering = ['name']

	def save(self, *args, **kwargs):
		if not self.slug:
			base_slug = slugify(self.name)[:90] or 'tag'
			slug = base_slug
			counter = 1
			while Tag.objects.filter(slug=slug).exclude(pk=self.pk).exists():
				slug = f"{base_slug}-{counter}"
				counter += 1
			self.slug = slug
		super().save(*args, **kwargs)

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
	slug = models.SlugField(max_length=220, unique=True, blank=True)
	featured_image = models.ImageField(upload_to='posts/', blank=True, null=True, help_text="Featured image for the post")
	content = QuillField()
	status = models.CharField(
		max_length=20,
		choices=STATUS_CHOICES,
		default=STATUS_PUBLISHED,
	)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	class Meta:
		ordering = ['-created_at']

	def save(self, *args, **kwargs):
		if not self.slug:
			base_slug = slugify(self.title)[:200] or 'post'
			slug = base_slug
			counter = 1
			while Post.objects.filter(slug=slug).exclude(pk=self.pk).exists():
				slug = f"{base_slug}-{counter}"
				counter += 1
			self.slug = slug
		super().save(*args, **kwargs)

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
