from django.db import models
from users.models import UserProfile  # Replace 'your_app' with the actual app name containing UserProfile
from chat.models import Room, Message

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

class Like(models.Model):
    """Model for likes on posts."""
    user = models.ForeignKey(
        UserProfile, on_delete=models.CASCADE, related_name="likes"
    )
    post = models.ForeignKey(
        Post, on_delete=models.CASCADE, related_name="likes"
    )
    liked_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user} liked {self.post.title}"

    class Meta:
        unique_together = ('user', 'post')  # Ensures a user can like a post only once


class Notification(models.Model):
    """
    Model representing notifications for users.
    """
    NOTIFICATION_TYPES = [
        ("message", "Message"),
        ("room", "Room"),
        ("post", "Post"),
        ("custom", "Custom"),
    ]

    recipient = models.ForeignKey(
        UserProfile,
        on_delete=models.CASCADE,
        related_name="notifications",
        help_text="The user who receives the notification.",
    )
    sender = models.ForeignKey(
        UserProfile,
        on_delete=models.CASCADE,
        related_name="sent_notifications",
        null=True,
        blank=True,
        help_text="The user who triggered the notification (optional).",
    )
    notification_type = models.CharField(
        max_length=20, choices=NOTIFICATION_TYPES, help_text="Type of the notification."
    )
    room = models.ForeignKey(
        Room,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="notifications",
        help_text="Room associated with the notification (if applicable).",
    )
    message = models.ForeignKey(
        Message,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="notifications",
        help_text="Message associated with the notification (if applicable).",
    )
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="notifications",
        help_text="Post associated with the notification (if applicable).",
    )
    content = models.TextField(help_text="Custom notification message.")
    is_read = models.BooleanField(default=False, help_text="True if the notification has been read.")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Notification for {self.recipient} - {self.notification_type} - Read: {self.is_read}"

    class Meta:
        ordering = ("-created_at",)  # Show newest notifications first
