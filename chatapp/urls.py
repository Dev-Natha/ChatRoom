from django.urls import path
from .views import *

urlpatterns = [
    path("", homePage, name="home"),
    path("room/<int:pk>/", roomPage, name="room"),
    path("create/", createRoom, name="create"),
    path("edit/<int:pk>/", editRoom, name="edit"),
    path("delete/<int:pk>/", deleteObj, name="delete"),
    path("delete-message/<int:pk>/", deleteMessage, name="delete-message"),
    path("login/", loginPage, name="login"),
    path("logout/", logoutPage, name="logout"),
    path("register/", registerPage, name="register"),
    path("profile/<int:pk>", viewProfile, name="view-profile"),
    path("edit-profile/<int:pk>", profilePage, name="profile"),
]