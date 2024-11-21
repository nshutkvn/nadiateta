from django.shortcuts import render, get_object_or_404
from django.core.files.storage import default_storage
from django.shortcuts import render
import json
from authlib.integrations.django_client import OAuth
from django.conf import settings
from django.shortcuts import redirect, render
from django.urls import reverse
from urllib.parse import quote_plus, urlencode
from users.models import UserProfile
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from .models import Post, PostMedia, Comment
# Create your views here.

oauth = OAuth()

oauth.register(
    "auth0",
    client_id=settings.AUTH0_CLIENT_ID,
    client_secret=settings.AUTH0_CLIENT_SECRET,
    client_kwargs={
        "scope": "openid profile email",
    },
    server_metadata_url=f"https://{settings.AUTH0_DOMAIN}/.well-known/openid-configuration",
)


def index(request):
    user_id = request.session.get("user_id")
    if user_id:
        # Retrieve the user profile data
        user_profile = UserProfile.objects.filter(auth0_id=user_id).first()
        if user_profile:
            # Retrieve the top 3 latest mentors with the same area of interest as the logged-in user
            latest_mentors = UserProfile.objects.filter(
                role="mentor",
                area_of_interest=user_profile.area_of_interest
            ).exclude(id=user_profile.id).order_by('-id')[:3]

            # Render the template with user profile and latest mentors
            return render(request, "index.html", {
                "user_profile": user_profile,
                "latest_mentors": latest_mentors
            })
    
    # Redirect to login if no user is found
    return redirect(reverse("login"))


from django.shortcuts import render, redirect
from django.urls import reverse
from .models import Post, UserProfile  # Update imports to match your project

def coubs(request):
    # Check if user is authenticated
    user_id = request.session.get("user_id")
    if user_id:
        # Retrieve the user profile data
        user_profile = UserProfile.objects.filter(auth0_id=user_id).first()
        if user_profile:
            # Retrieve the latest 30 video posts ordered by creation date (descending)
            video_posts = Post.objects.filter(is_video=True).order_by("-created_at")[:30]

            # Prepare post data for template rendering
            posts_data = []
            for post in video_posts:
                # Prepare media URLs (assuming only video URLs are stored)
                media_urls = [media.media.url for media in post.postmedia_set.all() if media.media.url]

                # Skip posts without media
                if not media_urls:
                    continue

                # Prepare data for each post
                posts_data.append({
                    "id": post.id,
                    "content": post.content,
                    "created_at": post.created_at.strftime("%B %d, %Y, %I:%M %p"),
                    "media": media_urls[0],  # Use the first media URL as video
                    "user": {
                        "name": post.user.name,
                        "username": post.user.username,
                        "bio": post.user.bio,
                        "profile_pic": post.user.profile_pic.url if post.user.profile_pic else None,
                    },
                })

            # Render the "coubs.html" template with user profile and posts
            return render(request, "coubs.html", {"user_profile": user_profile, "posts": posts_data})

    # Redirect to login if no user is found
    return redirect(reverse("login"))




def explore(request):
    user_id = request.session.get("user_id")
    if user_id:
        # Retrieve the user profile data
        user_profile = UserProfile.objects.filter(auth0_id=user_id).first()
        if user_profile:
            return render(request, "explore.html", {"user_profile": user_profile})
    
    # Redirect to login if no user is found
    return redirect(reverse("login"))

def notification(request):
    user_id = request.session.get("user_id")
    if user_id:
        # Retrieve the user profile data
        user_profile = UserProfile.objects.filter(auth0_id=user_id).first()
        if user_profile:
            return render(request, "notification.html", {"user_profile": user_profile})
    
    # Redirect to login if no user is found
    return redirect(reverse("login"))


from django.shortcuts import render, redirect, reverse
from .models import Post, PostMedia, UserProfile # Import necessary models

def create_post(request):
    user_id = request.session.get("user_id")

    if user_id:
        user_profile = UserProfile.objects.filter(auth0_id=user_id).first()

        if user_profile:
            if request.method == 'POST':
                description = request.POST.get('description')
                is_video_str = request.POST.get('is_video')
                is_video = is_video_str.lower() == 'true'  # Convert to boolean
                uploaded_files = request.FILES.getlist('media')

                title = request.POST.get('title', 'Untitled') # Get title, default to 'Untitled'

                post = Post.objects.create(
                    user=user_profile,
                    title=title,
                    content=description,
                    is_video=is_video,  # Set is_video field
                )

                for file in uploaded_files:
                    PostMedia.objects.create(post=post, media=file)

                return redirect(reverse('index'))  # Redirect after successful post creation

    return redirect(reverse("login")) # Redirect to login if not logged in


from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from .models import Post, PostMedia, Comment

def postDetails(request, postId):
    try:
        # Fetch the post
        post = get_object_or_404(Post, id=postId)
        
        # Prepare media URLs for carousel
        media_urls = [media.media.url for media in post.postmedia_set.all()]
        
        # Prepare comments
        comments = [
            {
                "user_name": comment.user.name,
                "user_username": comment.user.username,
                "content": comment.content,
                "created_at": comment.created_at.strftime("%B %d, %Y, %I:%M %p"),
                "user_profile_pic": comment.user.profile_pic.url if comment.user.profile_pic else None,
            }
            for comment in post.comments.all()
        ]
        
        # Prepare user data for the post
        user = post.user
        user_data = {
            "name": user.name,
            "username": user.username,
            "bio": user.bio,
            "profile_pic": user.profile_pic.url if user.profile_pic else None
        }
        
        # Prepare the post data
        response_data = {
            "title": post.title,
            "content": post.content,
            "created_at": post.created_at.strftime("%B %d, %Y, %I:%M %p"),
            "user": user_data,
            "media": media_urls,
            "comments": comments,
        }

        return JsonResponse(response_data)
    
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)

def all_posts(request):
    try:
        # Retrieve the latest 30 posts ordered by creation date (descending)
        posts = Post.objects.all().order_by('-created_at')[:30]

        # Prepare the post data for response
        posts_data = []
        for post in posts:
            # Prepare comments data
            comments = [
                {
                    "user_name": comment.user.name,
                    "user_username": comment.user.username,
                    "content": comment.content,
                    "created_at": comment.created_at.strftime("%B %d, %Y, %I:%M %p"),
                    "user_profile_pic": comment.user.profile_pic.url if comment.user.profile_pic else None,
                }
                for comment in post.comments.all()
            ]

            # Prepare media URLs
            media_urls = [media.media.url for media in post.postmedia_set.all()]

            # Prepare user data
            user = post.user
            user_data = {
                "name": user.name,
                "username": user.username,
                "bio": user.bio,
                "profile_pic": user.profile_pic.url if user.profile_pic else None,
            }

            # Prepare the post data
            posts_data.append({
                "id": post.id,
                "title": post.title,
                "content": post.content,
                "is_video": post.is_video,
                "created_at": post.created_at.strftime("%B %d, %Y, %I:%M %p"),
                "user": user_data,
                "media": media_urls,
                "comments": comments,
            })

        print("Posts data being returned:", posts_data)
        return JsonResponse({"posts": posts_data})

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
    

@csrf_exempt
def add_comment(request, postId):
    user_id = request.session.get("user_id")  # Retrieve user ID from session
    if not user_id:
        return redirect(reverse("login"))

    # Get the authenticated user's profile
    user_profile = UserProfile.objects.filter(auth0_id=user_id).first()
    if not user_profile:
        return JsonResponse({"success": False, "error": "User profile not found."}, status=404)

    if request.method == "POST":
        try:
            import json
            data = json.loads(request.body)
            content = data.get("content", "").strip()

            if not content:
                return JsonResponse({"success": False, "error": "Comment content cannot be empty."}, status=400)

            # Get the post object
            post = get_object_or_404(Post, id=postId)

            # Create a new comment
            comment = Comment.objects.create(
                user=user_profile,
                post=post,
                content=content
            )

            # Prepare response data
            response_data = {
                "success": True,
                "comment": {
                    "id": comment.id,
                    "content": comment.content,
                    "created_at": comment.created_at.strftime("%B %d, %Y, %I:%M %p"),
                    "user_name": user_profile.name,
                    "user_username": user_profile.username,
                }
            }
            print(response_data)
            return JsonResponse(response_data, status=201)

        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)}, status=500)

    return JsonResponse({"success": False, "error": "Invalid request method."}, status=405)

