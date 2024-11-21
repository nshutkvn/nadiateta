from django.db import models
from django.contrib.auth.models import User
from users.models import UserProfile  # Import UserProfile from the correct app

class Room(models.Model):
    """
    Model representing a chat room, which can be private or public (group).
    """
    name = models.CharField(max_length=255, help_text="Name of the room.")
    slug = models.SlugField(unique=True, blank=True, help_text="Unique slug for the room, auto-generated from name.")
    private = models.BooleanField(default=False, help_text="True for private rooms, False for public/group rooms.")
    admin = models.ForeignKey(
        User, 
        on_delete=models.CASCADE,
        related_name="private_admin_rooms",
        null=True,
        blank=True,
        help_text="Admin for private rooms (Django User)."
    )
    group_admin = models.ForeignKey(
        UserProfile, 
        on_delete=models.CASCADE,
        related_name="group_admin_rooms",
        null=True,
        blank=True,
        help_text="Admin for group rooms (UserProfile)."
    )
    users = models.ManyToManyField(
        UserProfile, 
        related_name="rooms",
        help_text="Participants of the room."
    )
    profile_pic = models.ImageField(
        upload_to='pfp', 
        default="images/defaults/Default_pfp.svg.png",
        help_text="Room's profile picture."
    )
    area_of_interest = models.CharField(
        max_length=255, 
        null=True, 
        blank=True, 
        help_text="Topic of interest for public/group rooms."
    )

    def save(self, *args, **kwargs):
        """
        Custom save method to enforce validation and automatically generate a unique slug.
        """
        # Generate slug if it's not already set
        if not self.slug:
            from django.utils.text import slugify
            base_slug = slugify(self.name)
            slug = base_slug
            counter = 1
            while Room.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug

        # Validation for public rooms
        if not self.private and not self.area_of_interest:
            raise ValueError("Area of interest must be provided for public rooms.")

        # Ensure only one admin type is set
        if self.private and self.group_admin:
            raise ValueError("Private rooms cannot have a group admin.")
        if not self.private and self.admin:
            raise ValueError("Public/group rooms cannot have a private admin.")
        
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


    
class Message(models.Model):
    room = models.ForeignKey(Room, related_name='messages', on_delete=models.CASCADE)
    user = models.ForeignKey(UserProfile, related_name='messages', on_delete=models.CASCADE)
    content = models.TextField()
    date_added = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('date_added',)