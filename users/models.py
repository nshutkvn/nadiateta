from django.db import models

class UserProfile(models.Model):
    auth0_id = models.CharField(max_length=255, unique=True)
    name = models.CharField(max_length=150, default="user")
    username = models.CharField(max_length=150, unique=True)
    bio = models.TextField(blank=True, null=True)
    # profile_pic = models.ImageField(upload_to="profile_pics/", blank=True, null=True)
    role = models.CharField(max_length=50, choices=[("user", "User"), ("mentor", "Mentor")])
    area_of_interest = models.CharField(max_length=255, blank=True, null=True)
    profile_pic = models.ImageField(upload_to='pfp', default="media/images/defaults/Default_pfp.svg.png")


    def __str__(self):
        return self.username

