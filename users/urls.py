from django.urls import path

from . import views

urlpatterns = [
    # path("", views.index, name="index"),
    path("login/", views.login, name="login"),
    path("logout", views.logout, name="logout"),
    path("callback", views.callback, name="callback"),
    path("profile/<str:username>/", views.profile, name="profile"),
    path("additionalinfo", views.additionalinfo, name="additionalinfo"),
    path("check-username/", views.check_username, name="check_username"),
    path("save-additional-data/", views.save_additional_data, name="save_additional_data"),
    path("users-all/", views.fetch_users, name="fetch_users"),
    path('search/users/', views.search_users, name='search_users'),
    path("update-profile/", views.updateUserProfile, name="updateUserProfile"),




]