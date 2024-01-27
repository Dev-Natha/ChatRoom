from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.db.models import Q
from .models import Room, Message, Topic, User
from .forms import RoomForm, MyUserForm, ProfileForm
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages

# Create your views here.


def homePage(request):
    q = request.GET.get('q')
    if q == None:
        q = ""
    rooms = Room.objects.filter(Q(topic__name__icontains=q) 
                                | Q(name__icontains=q)
                                | Q(host__username__icontains=q)
                                ).order_by("-updated", "-created")
    topics = Topic.objects.all()
    room_count = rooms.count()
    room_messages = Message.objects.all().order_by("-updated", "-created")[0:4]
    context = {"rooms":rooms, "topics":topics, "room_count":room_count, "room_messages":room_messages}
    return render(request, "index.html", context)

def roomPage(request, pk):
    room_user = Room.objects.get(id=pk)
    room_people = room_user.participants.all()
    room_messages = room_user.message_set.all().order_by("-updated", "-created")

    if request.method == "POST":
        Message.objects.create(
            owner = request.user,
            room = room_user,
            body = request.POST.get("comment")
        )
        room_user.participants.add(request.user)
        return redirect("room", pk=room_user.id)
    context = {"room":room_user, "room_messages":room_messages, "room_people":room_people}
    return render(request, "room.html", context)

@login_required(login_url="login")
def createRoom(request):
    form = RoomForm()
    topics = Topic.objects.all()
    if request.method == "POST":
        form = RoomForm(request.POST)
        topic_name = request.POST.get("topic")
        topic, created = Topic.objects.get_or_create(name=topic_name)
        Room.objects.create(
            host = request.user,
            topic = topic,
            name = request.POST.get("name"),
            description = request.POST.get("description")
        )
       
        # if form.is_valid():
        #     user = form.save(commit=False)
        #     user.host = request.user
        #     user.save()
        return redirect("home")
    context = {"form":form, "topics":topics}
    return render(request, "create_edit.html", context)

@login_required(login_url="login")
def editRoom(request, pk):
    room = Room.objects.get(id=pk)
    topics = Topic.objects.all()
    if request.user != room.host:
        return HttpResponse("You are not allowed here")
    form = RoomForm(instance=room)
    user_topic = room.topic
    if request.method == "POST":
        topic_name = request.POST.get("topic")
        topic, created = Topic.objects.get_or_create(name=topic_name)
        room.topic = topic
        room.name = request.POST.get("name")
        room.description = request.POST.get("description")
        room.save()
        # form = RoomForm(request.POST, instance=room)
        # if form.is_valid():
        #     form.save()
        return redirect("home")
    context = {"form":form, "user_topic":user_topic, "topics":topics}
    return render(request, "create_edit.html", context)

@login_required(login_url="login")
def deleteObj(request, pk):
    obj = Room.objects.get(id=pk)
    if request.user != obj.host:
        return HttpResponse("You are not allowed here")
    context = {"obj":obj}
    if request.method == "POST":
        obj.delete()
        return redirect("home")
    return render(request, "delete.html", context)


def loginPage(request):
    if request.user.is_authenticated:
        return redirect("home")
    if request.method == "POST":
        usernam = request.POST.get("email")
        pwd = request.POST.get("password")
        user = authenticate(request, email=usernam, password=pwd)
        if user is not None:
            login(request, user)
            return redirect("home")
        else:
            messages.error(request, "Invalid Login details")
            return redirect("login")
    return render(request, "login.html")


def logoutPage(request):
    logout(request)
    return redirect("home")


def registerPage(request):
    form = MyUserForm()
    context = {"form":form}
    if request.method == "POST":
        form = MyUserForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.username = user.username.lower()
            user.save()
            login(request, user)
            return redirect("home")
    return render(request, "register.html", context)


def deleteMessage(request, pk):
    obj = Message.objects.get(id=pk)
    if request.user != obj.owner:
        return HttpResponse("You are not allowed here")
    context = {"obj":obj}
    if request.method == "POST":
        obj.delete()
        return redirect("home")
    return render(request, "delete.html", context)

@login_required(login_url="login")
def profilePage(request, pk):
    profile = User.objects.get(id = pk)
    form = ProfileForm(instance=profile)
    context = {"form":form}
    if request.user != profile:
        return redirect("home")
    if request.method == "POST":
        form = ProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            return redirect("view-profile", pk=profile.id)
    return render(request, "edit-profile.html", context)

def viewProfile(request, pk):
    profile = User.objects.get(id = pk)
    context = {"profile":profile}
    return render(request, "profile.html", context)