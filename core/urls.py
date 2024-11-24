from django.urls import path

from . import views

urlpatterns = [path("", views.index, name="index"),
               path("coubs", views.coubs, name="coubs"),
               path("explore", views.explore, name="explore"),
               path("notification", views.notification, name="notification"),
               path("create_post", views.create_post, name="create_post"),
               path("get-post-details/<int:postId>/", views.postDetails, name="postDetails"),
               path('all-posts', views.all_posts, name="all_posts"),
               path('comment/<int:postId>/', views.add_comment, name="add_comment"),
               path("delete-comment/<int:commentId>/", views.deleteComment, name="deleteComment"),
               path("delete-post/<int:postId>/", views.deletePost, name="deletePost"),
               path('toggle-like/', views.toggle_like, name='toggle_like'),
               path("notifications/", views.get_notifications, name="get_notifications"),
               path('fetch-rooms/', views.fetch_rooms, name='fetch_rooms'),
               path('post/<int:postId>/', views.post, name="post" )


               ]