from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

# Create your models here.

class UserProfile(models.Model):
    """
    Extended user profile for ThoughtNest users
    Extends Django's built-in User model with additional information
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    bio = models.TextField(max_length=500, blank=True, help_text="A short bio about yourself")
    # avatar field removed
    location = models.CharField(max_length=100, blank=True)
    website = models.URLField(max_length=200, blank=True)
    
    # Social media links
    twitter = models.CharField(max_length=100, blank=True)
    github = models.CharField(max_length=100, blank=True)
    linkedin = models.CharField(max_length=100, blank=True)
    
    # Preferences
    email_notifications = models.BooleanField(default=True, help_text="Receive email notifications")
    # newsletter_subscription field removed
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "User Profile"
        verbose_name_plural = "User Profiles"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.username}'s Profile"
    
    def get_full_name(self):
        """Return user's full name or username"""
        return self.user.get_full_name() or self.user.username
    
    def is_admin(self):
        """Check if user is an admin (staff or superuser)"""
        return self.user.is_staff or self.user.is_superuser
    
    def get_post_count(self):
        """Return number of posts by this user"""
        return self.user.posts.count()
    
    def get_total_likes(self):
        """Return total likes across all user's posts"""
        return sum(post.likes.count() for post in self.user.posts.all())
    
    def get_total_comments(self):
        """Return total comments across all user's posts"""
        return sum(post.comments.count() for post in self.user.posts.all())


# Signal to automatically create UserProfile when User is created
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """Create UserProfile when a new User is created"""
    if created:
        UserProfile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """Save UserProfile when User is saved"""
    if hasattr(instance, 'profile'):
        instance.profile.save()
