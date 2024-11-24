from django.core.files.storage import default_storage
from django.shortcuts import render, get_object_or_404
import json
from authlib.integrations.django_client import OAuth
from django.conf import settings
from django.shortcuts import redirect, render
from django.urls import reverse
from urllib.parse import quote_plus, urlencode
from .models import UserProfile
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from core.models import Post, PostMedia



# 👆 We're continuing from the steps above. Append this to your webappexample/views.py file.

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

# 👆 We're continuing from the steps above. Append this to your webappexample/views.py file.

def login(request):
    return oauth.auth0.authorize_redirect(
        request, request.build_absolute_uri(reverse("callback"))
    )

# 👆 We're continuing from the steps above. Append this to your webappexample/views.py file.

def callback(request):
    # Fetch the access token and store the user info in the session
    token = oauth.auth0.authorize_access_token(request)
    user_info = token.get("userinfo")  # Extract user info from the token

    if user_info:
        # Extract the user ID from the `sub` claim
        user_id = user_info.get("sub")
        request.session["user_id"] = user_id  # Store it in the session

        # Check if the user exists in the UserProfile table
        user_profile = UserProfile.objects.filter(auth0_id=user_id).first()

        if user_profile:
            # User exists, redirect to their profile and pass user data
            return redirect(reverse('profile', kwargs={'username': user_profile.username}))
        else:
            # User is new, pass user_id and redirect to finalize registration (additionalinfo)
            return render(request, "additionalinfo.html", {"user_id": user_id})
    else:
        # Handle cases where authentication fails (e.g., missing user_info)
        return redirect(reverse("login"))




# 👆 We're continuing from the steps above. Append this to your webappexample/views.py file.

def logout(request):
    request.session.clear()

    return redirect(
        f"https://{settings.AUTH0_DOMAIN}/v2/logout?"
        + urlencode(
            {
                "returnTo": request.build_absolute_uri(reverse("index")),
                "client_id": settings.AUTH0_CLIENT_ID,
            },
            quote_via=quote_plus,
        ),
    )

# 👆 We're continuing from the steps above. Append this to your webappexample/views.py file.


def profile(request, username):
    # Check if the user is authenticated
    user_id = request.session.get("user_id")
    if not user_id:
        return redirect(reverse("login"))
    
    # Retrieve the authenticated user's profile
    user_profile = UserProfile.objects.filter(auth0_id=user_id).first()
    if not user_profile:
        return redirect(reverse("login"))
    
    # Retrieve the profile of the user specified by the 'username'
    profile_user = get_object_or_404(UserProfile, username=username)
    
    # Retrieve posts associated with the profile_user
    user_posts = Post.objects.filter(user=profile_user).order_by('-created_at')  # Latest posts first
    
    # Render the profile template with both profiles and posts
    return render(request, "profile.html", {
        "user_profile": user_profile,
        "profile_user": profile_user,
        "user_posts": user_posts,
    })


def additionalinfo(request):
    # Fetch the user ID from the session
    user_id = request.session.get("user_id")
    if not user_id:
        messages.error(request, "You must be authenticated to complete your registration.")
        return redirect("login")

    return render(request, "additionalinfo.html")

# check username 

def check_username(request):
    pass

from django.shortcuts import redirect

def save_additional_data(request):
    if request.method == 'POST':
        # Get the POST data
        user_id = request.POST.get('user_id')
        role = request.POST.get('role')
        name = request.POST.get('name')
        username = request.POST.get('username')
        bio = request.POST.get('bio')
        profile_pic = request.FILES.get('profile_pic')  # Get uploaded profile picture
        area_of_interest = request.POST.get('area_of_interest')

        # Check for unique username
        if UserProfile.objects.filter(username=username).exclude(auth0_id=user_id).exists():
            return JsonResponse(
                {"status": "error", "message": "The username is already taken. Please choose a different one."},
                status=400
            )

        # Find or create a new user profile using auth0_id (user_id)
        user_profile, created = UserProfile.objects.update_or_create(
            auth0_id=user_id,
            defaults={
                "role": role,
                "name": name,
                "username": username,
                "bio": bio,
                "area_of_interest": area_of_interest,
                "profile_pic": profile_pic or "media/images/defaults/Default_pfp.svg.png",
            }
        )

        # Redirect to profile endpoint
        return redirect(reverse('profile', args=[username]))    
    return JsonResponse({'status': 'error'}, status=400)

# fetch all users

def fetch_users(request):
    # Exclude the currently logged-in user from the list
    users = UserProfile.objects.exclude(auth0_id=request.session.get("user_id"))
    return render(request, "slider.html", {"users": users})

# search users

def search_users(request):
    query = request.GET.get('query', '')
    is_mentor = request.GET.get('is_mentor', 'false').lower() == 'true'

    if query:
        if is_mentor:
            users = UserProfile.objects.filter(username__icontains=query, role='mentor')[:10]  # Search in mentors only
        else:
            users = UserProfile.objects.filter(username__icontains=query)[:10]  # Search in both mentors and youth

        user_data = [
            {
                'username': user.username,
                'name': user.name,
                'profile_pic': user.profile_pic.url if user.profile_pic else None,
            }
            for user in users
        ]
        return JsonResponse({'users': user_data})
    return JsonResponse({'users': []})

@csrf_exempt
def updateUserProfile(request):
    user_id = request.session.get("user_id")
    if not user_id:
        return JsonResponse({"error": "You need to be logged in to update your profile."}, status=401)

    if request.method == "POST":
        user_profile = UserProfile.objects.filter(auth0_id=user_id).first()
        if not user_profile:
            return JsonResponse({"error": "User profile not found."}, status=404)

        try:
            # Update name
            name = request.POST.get("name")
            if name:
                user_profile.name = name
            
            # Update area of interest
            area_of_interest = request.POST.get("area_of_interest")
            if area_of_interest:
                user_profile.area_of_interest = area_of_interest
            
            # Update profile picture
            if "profile_pic" in request.FILES:
                profile_pic = request.FILES["profile_pic"]

                # Delete old profile pic if not default
                if user_profile.profile_pic and not user_profile.profile_pic.name.startswith("media/images/defaults/"):
                    default_storage.delete(user_profile.profile_pic.path)

                # Save new profile picture
                user_profile.profile_pic = profile_pic

            # Save changes
            user_profile.save()
            return JsonResponse({"message": "Profile updated successfully."})
        
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"error": "Invalid request method."}, status=405)
