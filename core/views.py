from django.shortcuts import render, get_object_or_404
from django.core.files.storage import default_storage
from django.shortcuts import render
import json
from authlib.integrations.django_client import OAuth
from django.conf import settings
from django.shortcuts import redirect, render
from django.urls import reverse
from users.models import UserProfile
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Post, PostMedia, Comment, Like, Notification
from django.utils.timesince import timesince
from chat.models import Room
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


from django.shortcuts import render, redirect, reverse
from .models import UserProfile

def index(request):
    user_id = request.session.get("user_id")
    if user_id:
        # Retrieve the user profile data
        user_profile = UserProfile.objects.filter(auth0_id=user_id).first()
        if user_profile:
            # Retrieve the top 3 latest mentors (same logic as before)
            latest_mentors = UserProfile.objects.filter(
                role="mentor",
                area_of_interest=user_profile.area_of_interest
            ).exclude(id=user_profile.id).order_by('-id')[:3]

            # Render the template with user profile and latest mentors
            return render(request, "index.html", {
                "user_profile": user_profile,
                "latest_mentors": latest_mentors,
            })
        else:
            # Handle case where the user_profile doesn't exist
            return redirect(reverse("login"))
    else:
        # Handle case where user_id doesn't exist in the session
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

from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.utils.timesince import timesince
from .models import Post, Comment

def postDetails(request, postId):
    try:
        post = get_object_or_404(Post, id=postId)
        user = request.user if request.user.is_authenticated else None

        # Prepare media
        media_urls = [media.media.url for media in post.postmedia_set.all()]

        # Prepare comments
        comments = [
            {
                "id": comment.id,
                "user_name": comment.user.name,
                "content": comment.content,
                "created_at": timesince(comment.created_at) + " ago",
                "can_delete": user == comment.user if user else False,  # Check if the logged-in user is the comment author
            }
            for comment in post.comments.all()
        ]

        # Prepare response data
        response_data = {
            "user": {
                "name": post.user.name,
                "profile_pic": post.user.profile_pic.url if post.user.profile_pic else None,
            },
            "content": post.content,
            "created_at": timesince(post.created_at) + " ago",
            "media": media_urls,
            "is_video": post.is_video,
            "comments": comments,
            "can_delete_post": user == post.user if user else False,  # Check if the logged-in user is the post author
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

# delete comment

from django.shortcuts import get_object_or_404
from django.http import JsonResponse

def deleteComment(request, commentId):
    # Check if the user is authenticated using session-based authentication
    user_id = request.session.get("user_id")
    if not user_id:
        return JsonResponse({"error": "You need to be logged in to delete comments."}, status=401)

    try:
        # Fetch the comment and the user profile
        comment = get_object_or_404(Comment, id=commentId)
        user_profile = UserProfile.objects.filter(auth0_id=user_id).first()

        if not user_profile:
            return JsonResponse({"error": "Invalid user profile."}, status=403)
        
        # Check if the user is the owner of the comment or has admin rights
        if comment.user == user_profile or user_profile.is_superuser:
            comment.delete()
            return JsonResponse({"message": "Comment deleted successfully."})
        else:
            return JsonResponse({"error": "You are not authorized to delete this comment."}, status=403)

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


#delete post

def deletePost(request, postId):
    # Check if the user is authenticated using session-based authentication
    user_id = request.session.get("user_id")
    if not user_id:
        return JsonResponse({"error": "You need to be logged in to delete posts."}, status=401)
    
    try:
        # Fetch the post and the user profile
        post = get_object_or_404(Post, id=postId)
        user_profile = UserProfile.objects.filter(auth0_id=user_id).first()

        if not user_profile:
            return JsonResponse({"error": "Invalid user profile."}, status=403)
        
        # Check if the user is the owner of the post or has admin rights
        if post.user == user_profile or user_profile.is_superuser:
            post.delete()
            return JsonResponse({"message": "Post deleted successfully."})
        else:
            return JsonResponse({"error": "You are not authorized to delete this post."}, status=403)

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)

# -------------like----------------
def toggle_like(request):
    if request.method == "POST":
        post_id = request.POST.get("post_id")
        user_id = request.session.get("user_id")

        if not user_id or not post_id:
            return JsonResponse({"error": "Invalid request"}, status=400)

        user_profile = UserProfile.objects.filter(auth0_id=user_id).first()
        post = get_object_or_404(Post, id=post_id)

        # Check if the user has already liked the post
        like, created = Like.objects.get_or_create(user=user_profile, post=post)

        if not created:  # If already liked, remove the like
            like.delete()
            return JsonResponse({"liked": False})
        return JsonResponse({"liked": True})

    return JsonResponse({"error": "Invalid request"}, status=400)

# notifications
def get_notifications(request):
    """
    Retrieve unread notifications for the authenticated user based on session.
    """
    user_id = request.session.get("user_id")  # Use your authentication method
    if user_id:
        user_profile = UserProfile.objects.filter(auth0_id=user_id).first()
        if user_profile:
            # Fetch unread notifications for the authenticated user
            notifications = Notification.objects.filter(recipient=user_profile, is_read=False).order_by('-created_at')

            # Mark notifications as read
            notifications.update(is_read=True)

            # Prepare data for response
            notification_data = [
                {
                    "sender_name": n.sender.username if n.sender else "System",
                    "sender_image": n.sender.profile_pic.url if n.sender else "/media/images/defaults/profile_img.jpg",
                    "content": n.content,
                    "time": n.created_at.strftime("%b %d, %H:%M"),
                }
                for n in notifications
            ]

            return JsonResponse({"notifications": notification_data}, safe=False)

    # Redirect to login if user is not authenticated
    return redirect(reverse("login"))


def fetch_rooms(request):
    user_id = request.session.get("user_id")
    if user_id:
        # Retrieve the user profile data
        user_profile = UserProfile.objects.filter(auth0_id=user_id).first()
        if user_profile:
            # Get rooms where the user is part of
            rooms = Room.objects.filter(users=user_profile)
            return render(request, "index.html", {"user_profile": user_profile, 'rooms': rooms})
    
    # Redirect to login if no user is found
    return redirect(reverse("login"))


from django.shortcuts import render, get_object_or_404
from django.utils.timesince import timesince

def post(request, postId):
    # Retrieve the user ID from the session
    user_id = request.session.get("user_id")
    user_profile = None
    user_rooms = []
    
    if user_id:
        # Retrieve the user profile data
        user_profile = UserProfile.objects.filter(auth0_id=user_id).first()
        if user_profile:
            # Retrieve the rooms the user is in
            user_rooms = user_profile.rooms.all()

    # Get the post or raise a 404 if not found
    post = get_object_or_404(Post, id=postId)

    # Prepare media
    media_urls = [media.media.url for media in post.postmedia_set.all()]

    # Prepare comments
    comments = [
        {
            "id": comment.id,
            "user_name": comment.user.name,
            "content": comment.content,
            "created_at": timesince(comment.created_at) + " ago",
            "can_delete": user_profile == comment.user if user_profile else False,  # Check if the logged-in user is the comment author
        }
        for comment in post.comments.all()
    ]

    # Prepare context data
    context = {
        "user_profile": user_profile,  # User profile data from session
        "user_rooms": user_rooms,  # Rooms the user is in
        "post": {
            "user": {
                "name": post.user.name,
                "profile_pic": post.user.profile_pic.url if post.user.profile_pic else None,
            },
            "content": post.content,
            "created_at": timesince(post.created_at) + " ago",
            "media": media_urls,
            "is_video": post.is_video,
            "comments": comments,
            "can_delete_post": user_profile == post.user if user_profile else False,  # Check if the logged-in user is the post author
        }
    }

    # Render the template with the prepared context
    return render(request, "post.html", context)