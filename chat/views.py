from django.shortcuts import render, redirect
from django.urls import reverse
from django.conf import settings
from authlib.integrations.django_client import OAuth
from .models import Room, Message
from users.models import UserProfile
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.utils.text import slugify
from .models import Room, UserProfile
from django.core.exceptions import ValidationError
from django.views.decorators.csrf import csrf_exempt
import logging

# Initialize OAuth for authentication with Auth0
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

# Chat home view (lists all rooms or user-specific rooms)
def chat(request):
    user_id = request.session.get("user_id")
    if user_id:
        # Retrieve the user profile data
        user_profile = UserProfile.objects.filter(auth0_id=user_id).first()
        if user_profile:
            # Get rooms where the user is part of
            rooms = Room.objects.filter(users=user_profile)
            return render(request, "messages.html", {"user_profile": user_profile, 'rooms': rooms})
    
    # Redirect to login if no user is found
    return redirect(reverse("login"))


# View for a specific room (displays messages within the room)
def room(request, slug):
    user_id = request.session.get("user_id")
    if user_id:
        # Retrieve the user profile data
        user_profile = UserProfile.objects.filter(auth0_id=user_id).first()
        if user_profile:
            # Get the specific room by slug
            room = Room.objects.get(slug=slug)
            
            # Check if the user is part of the room
            if user_profile not in room.users.all():
                # If the user is not part of the room, redirect to the chat page
                return redirect(reverse("chat"))
            
            # Fetch the latest 25 messages for the room
            messages = Message.objects.filter(room=room)[0:25]
            # Get rooms where the user is part of
            rooms = Room.objects.filter(users=user_profile)
            return render(request, "messages.html", {"user_profile": user_profile, 'room': room, 'rooms': rooms, 'messages': messages})
    
    # Redirect to login if no user is found
    return redirect(reverse("login"))


# Create a new room (private or group chat)

from django.http import JsonResponse

def create_room(request):
    if request.method == "POST":
        name = request.POST.get("name")
        area_of_interest = request.POST.get("area_of_interest")
        profile_pic = request.FILES.get("profile_pic")
        private = request.POST.get("private") == "True"

        if not name or not profile_pic:
            return JsonResponse({"success": False, "errors": {"name": "Room name is required.", "profile_pic": "Profile picture is required."}})

        # Save the room (example logic)
        room = Room.objects.create(
            name=name,
            area_of_interest=area_of_interest,
            private=private,
            profile_picture=profile_pic,
        )

        return JsonResponse({"success": True, "redirect_url": f"/chat/room/{room.slug}/"})

    return JsonResponse({"success": False, "error": "Invalid request method."})

# Join an existing room
def join_room(request, slug):
    user_id = request.session.get("user_id")
    if user_id:
        user_profile = UserProfile.objects.filter(auth0_id=user_id).first()
        if user_profile:
            room = Room.objects.get(slug=slug)
            room.users.add(user_profile)
            return redirect(reverse('room', kwargs={'slug': room.slug}))
    return redirect(reverse('chat'))  # Return to chat list if no user is found

# Send a message to a room
def send_message(request, slug):
    user_id = request.session.get("user_id")
    if user_id:
        user_profile = UserProfile.objects.filter(auth0_id=user_id).first()
        if user_profile and request.method == 'POST':
            room = Room.objects.get(slug=slug)
            message_content = request.POST.get('message')
            message = Message.objects.create(
                user=user_profile,
                room=room,
                content=message_content
            )
            return redirect(reverse('room', kwargs={'slug': room.slug}))
    return redirect(reverse('chat'))  # Return to chat list if no user is found

# Private chat between two users (based on their auth0_id)
logger = logging.getLogger(__name__)

from django.urls import reverse

def private_chat(request, username):
    user_id = request.session.get("user_id")
    if user_id:
        user_profile = UserProfile.objects.filter(auth0_id=user_id).first()
        if user_profile:
            other_user = UserProfile.objects.filter(username=username).first()
            if other_user:
                # Generate consistent room name by sorting the usernames
                usernames = sorted([user_profile.username, other_user.username])
                room_name = f"Private Chat: {' & '.join(usernames)}"
                
                # Check if room already exists
                room = Room.objects.filter(name=room_name).first()
                if not room:
                    # Create a new room if it doesn't exist
                    room, created = Room.objects.get_or_create(
                        name=room_name,
                        private=True
                    )
                    if not room.slug:
                        room.slug = slugify(room_name)
                        room.save()

                room.users.add(user_profile, other_user)
                return redirect(reverse('room', kwargs={'slug': room.slug}))

    return redirect(reverse('chat'))



# Leave a room (for users to leave a room they are part of)
def leave_room(request, slug):
    user_id = request.session.get("user_id")
    if user_id:
        user_profile = UserProfile.objects.filter(auth0_id=user_id).first()
        if user_profile:
            room = Room.objects.get(slug=slug)
            room.users.remove(user_profile)
            return redirect(reverse('chat'))  # After leaving the room, redirect back to the chat list
    return redirect(reverse('chat'))  # Redirect if user is not found

def create_room(request):
    if request.method == 'POST' and request.is_ajax():
        name = request.POST.get('name')
        profile_pic = request.FILES.get('profile_pic')
        area_of_interest = request.POST.get('area_of_interest')
        private = bool(request.POST.get('private'))

        # Check if room name is already taken
        if Room.objects.filter(name=name).exists():
            return JsonResponse({'error': 'Room name is already taken, please choose another one.'}, status=400)

        # Create room and save
        try:
            room = Room(name=name, slug=slugify(name), private=private, profile_pic=profile_pic)
            if not private and not area_of_interest:
                return JsonResponse({'error': 'Please provide an area of interest for public rooms.'}, status=400)

            if not private:
                room.area_of_interest = area_of_interest

            room.save()
            return JsonResponse({'success': 'Room created successfully!', 'room_slug': room.slug})

        except ValidationError as e:
            return JsonResponse({'error': str(e)}, status=400)
    return JsonResponse({'error': 'Invalid request.'}, status=400)


def add_user_to_room():
    pass


# View to fetch rooms based on logged-in user



# View to handle sharing content
def share_content(request):
    """Handle sharing content with selected rooms."""
    if request.method == 'POST':
        content_type = request.POST.get('content_type')
        content_id = request.POST.get('content_id')
        selected_rooms = request.POST.getlist('share_with[]')  # List of selected room slugs
        
        # Implement logic for sharing the content with the selected rooms
        # Example: Save the shared content into the room or send notifications, etc.
        
        # Example: Just print the shared content (you can replace this with your logic)
        print(f"Content type: {content_type}, Content ID: {content_id}")
        print(f"Sharing with rooms: {selected_rooms}")
        
        # Redirect or return a response after processing
        return redirect('some_view')  # Replace with an actual redirect URL

    return redirect('some_view')  # Redirect if it's not a POST request
