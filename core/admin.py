from django.contrib import admin
from .models import Post, PostMedia, Comment, Saved

# Register your models here.
admin.site.register(Post)
admin.site.register(PostMedia)
admin.site.register(Comment)
admin.site.register(Saved)