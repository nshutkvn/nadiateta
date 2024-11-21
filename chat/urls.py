from django.urls import path
from . import views

urlpatterns = [
    # Chat Home (List of all rooms or user-specific rooms)
    path("", views.chat, name="chat"),

    # Room page (for viewing specific room and its messages)
    path('<slug:slug>/', views.room, name='room'),

    # Create new room (private or group chat)
    path('create_room', views.create_room, name='create_room'),

    # Join an existing room
    path('room/join/<slug:slug>/', views.join_room, name='join_room'),

    # Add user to room (admin functionality)
    path('room/add_user/<slug:slug>/', views.add_user_to_room, name='add_user_to_room'),

    # Send a message to a room
    path('room/<slug:slug>/send_message/', views.send_message, name='send_message'),

    # Start private chat with another user
    path('chat/private/<str:username>/', views.private_chat, name='private_chat'),

    # Leave room functionality
    path('room/leave/<slug:slug>/', views.leave_room, name='leave_room'),
    path('create-room/', views.create_room, name='create_room'),

]
