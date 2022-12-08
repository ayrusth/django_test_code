from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
# from django.contrib.auth.models import User
# from django.contrib.auth.forms import UserCreationForm
# Create your views here.
from .models import Room, Topic, Message, User
from .forms import RoomForm, UserForm, MyUserCreationFrom
from django.db.models import Q
from django.contrib.auth import authenticate, login, logout


# rooms =[
#     {'id':1, 'name':'Let\'s learn Python' },
#     {'id':2, 'name':'Javascript' },
#     {'id':3, 'name':'Let\'s learn CSS' },
# ]

def loginPage(request):

    page = 'login'
    if request.user.is_authenticated:
        return redirect('home')

    if request.method =='POST':
        username = request.POST.get('username').lower()
        password = request.POST.get('password')

        try:
            user = User.objects.get(username=username)
        
        except:
            messages.error(request, 'User doesn\'t exists')
        
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request,user)
            return redirect('home')
        else:
            messages.error(request, 'Email or Password doesn\'t exists')

    context= {'page' : page}
    return render(request, 'base/login_register.html', context)


def logoutUser(request):
    logout(request)
    return redirect('home')

def registerPage(request):
    form = MyUserCreationFrom()

    if request.method == 'POST':
        form = MyUserCreationFrom(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.username = user.username.lower()
            user.save()
            login(request, user)
            return redirect('home') 
        else:
            messages.error(request, 'An error has occurred during Registration')

    return render(request, 'base/login_register.html',{'form':form})



def home(request):
    q = request.GET.get('q') if request.GET.get('q')!= None else ''

    #for searching
    rooms = Room.objects.filter(
        Q( topic__name__icontains=q)|
        Q(name__icontains=q) |
        Q(description__icontains=q)
        )
    # rooms = Room.objects.all() #to extract all rooms

    topics = Topic.objects.all()[0:5]

    room_count = rooms.count() #to count the rooms

    room_messages = Message.objects.filter(Q(room__topic__name__icontains=q))
    
    context = {'rooms':rooms, 'topics': topics, 'room_count':room_count, 'room_messages': room_messages}
    return render(request, 'base/home.html',context) # or { 'rooms':rooms} instead of context directly
    # return render(request, 'home.html',context) incase of making templates outside of app folder



def room(request, pk):
    rooms= Room.objects.get(id=pk)
    room_messages = rooms.message_set.all() #.order_by('-created')
    participants = rooms.participants.all()
    if request.method == 'POST':
        message = Message.objects.create(
            user=request.user,
            room=rooms,
            body=request.POST.get('body')
        )
        rooms.participants.add(request.user) #user added to participants
        return redirect('rooms', pk=rooms.id)

    context = {'room': rooms, 'room_messages':room_messages,'participants':participants}        
    return render(request, 'base/room.html', context)


def userProfile(request,pk):
    user = User.objects.get(id=pk)
    rooms = user.room_set.all() #room is model name room._set.all() get all children of rooms
    room_messages = user.message_set.all()
    topics = Topic.objects.all()
    context = {'user': user, 'rooms': rooms, 'room_messages':room_messages, 'topics':topics}
    return render(request, 'base/profile.html', context)



@login_required(login_url='login')
def createRoom(request):
    form = RoomForm()
    topics = Topic.objects.all()
    if request.method == 'POST':
        # print(request.POST)
        topic_name = request.POST.get('topic')
        topic, created = Topic.objects.get_or_create(name=topic_name)

        Room.objects.create(
            host = request.user,
            topic= topic,
            name = request.POST.get('name'),
            description = request.POST.get('description')
        )
        return redirect('home')

        # This is used while using modelform method to create room
        # form = RoomForm(request.POST)
        # if form.is_valid():
        #     room = form.save(commit=False)
        #     room.host = request.user
        #     room.save()
            # return redirect('home')
        

    context= {'form':form, 'topics':topics}
    return render(request, 'base/room_form.html', context)


@login_required(login_url='login')
def updateRoom(request, pk):
    room = Room.objects.get(id=pk)
    form = RoomForm(instance=room)
    topics = Topic.objects.all()
    if request.user != room.host:
        return HttpResponse('Your are not allowed Here!!!')

    if request.method == 'POST':
        topic_name = request.POST.get('topic')
        topic, created = Topic.objects.get_or_create(name=topic_name)
        
        room.name = request.POST.get('name')
        room.topic = topic
        room.description = request.POST.get('description')
        room.save()
        return redirect('home')

        #for using Roomform method
        # form = RoomForm(request.POST, instance=room)
        # if form.is_valid():
        #     form.save()
        #     return redirect('home')

    context = {'form': form, 'topics':topics, 'room':room}
    return render(request, 'base/room_form.html', context)

@login_required(login_url='login')
def deleteRoom(request,pk):
    room = Room.objects.get(id=pk)

    if request.user != room.host:
        return HttpResponse('Your are not allowed Here!!!')

    if request.method == 'POST':
        room.delete()
        return redirect('home')

    return render(request, 'base/delete.html', {'obj':room})

@login_required(login_url='login')
def deleteMessage(request,pk):
    message = Message.objects.get(id=pk)

    if request.user != message.user:
        return HttpResponse('Your are not allowed Here!!!')

    if request.method == 'POST':
        message.delete()
        return redirect('home')

    return render(request, 'base/delete.html', {'obj':message})


@login_required(login_url='login')
def updateUser(request):
    user = request.user
    form = UserForm(instance=user)

    if request.method == 'POST':
        form = UserForm(request.POST, request.FILES, instance = user)  #request.Files used to link avatar image in backend
        if form.is_valid():
            form.save()
            return redirect('user-profile', pk= user.id)


    context = {'form':form  }
    return render(request, 'base/update-user.html', context)


def topicsPage(request):
    q = request.GET.get('q') if request.GET.get('q')!= None else ''
    topics = Topic.objects.filter(name__icontains=q)
    return render(request, 'base/topics.html',{'topics':topics})

def activityPage(request):
    room_message = Message.objects.all()
    return render(request, 'base/activity.html',{'room_message':room_message})    