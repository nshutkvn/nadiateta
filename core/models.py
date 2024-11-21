from django.db import models
from users.models import UserProfile  # Replace 'your_app' with the actual app name containing UserProfile

class Post(models.Model):
    """Model for user posts."""
    user = models.ForeignKey(
        UserProfile, on_delete=models.CASCADE, related_name="posts"
    )
    title = models.CharField(max_length=255, blank=True, null=True)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_video = models.BooleanField(default=False)  # Add the is_video field


    def __str__(self):
        return self.title

class PostMedia(models.Model):
    post = models.ForeignKey('Post', on_delete=models.CASCADE)
    media = models.FileField(upload_to='post_media/')

class Comment(models.Model):
    """Model for comments on posts."""
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="comments")
    user = models.ForeignKey(
        UserProfile, on_delete=models.CASCADE, related_name="comments"
    )
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Comment by {self.user} on {self.post.title}"


class Saved(models.Model):
    """Model for saving posts."""
    user = models.ForeignKey(
        UserProfile, on_delete=models.CASCADE, related_name="saved_posts"
    )
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="saved_by")
    saved_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user} saved {self.post.title}"
