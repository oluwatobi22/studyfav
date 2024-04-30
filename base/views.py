from multiprocessing import context
from pydoc_data import topics
from django.shortcuts import redirect, render
from django.http import HttpResponse
from django.contrib import messages
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from .models import Room, Topic, Message, User
from django.contrib.auth import authenticate, login, logout
from .forms import RoomForm, UserForm, MyUserCreationForm

# Create your views here.

# rooms = [
#   {'id':1, 'name': 'Lets Learn Python'},
#   {'id':2, 'name': 'Lets Learn django'},
#   {'id':3, 'name': 'Backend Developers'}
# ]

# def signinPage(request):

#   page = 'signin'

#   if request.user.is_authenticated:
#     return redirect('home')

#   if request.method == 'POST':
#     email = request.POST.get('email')
#     password = request.POST.get('password')

#     try:
#       user = User.objects.get(email=email)
#     except:
#       messages.error(request, 'Email address not found for user')
    
#     user = authenticate(request, email=email, password=password)

#     if user is not None:
#       login(request, user)
#       return redirect('home')
#     else:
#       messages.error(request, 'Username OR Password does not exist')
  
#   context = {'page': page}
#   return render(request, 'base/signin_signup.html', context)

def signinPage(request):
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        
        user = authenticate(request, username=email, password=password)
        
        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'Email or Password does not exist')
  
    context = {'page': 'signin'}
    return render(request, 'base/signin_signup.html', context)


def logoutUser(request):
  logout(request)
  return redirect('home') 

def signupPage(request):
    form = MyUserCreationForm()
    context = {'form': form}

    if request.method == 'POST':
      form = MyUserCreationForm(request.POST)
      if form.is_valid():
        user = form.save(commit=False)
        user.username = form.cleaned_data.get('username')
        password = form.cleaned_data.get('password1')
        user.set_password(password)
        user.save()
        login(request, user) 
        return redirect('home')
    else:
        messages.error(request, 'Invalid signup attempt. Please check the fields below.')
        context['form'] = form  

    return render(request, 'base/signin_signup.html', context)


def home(request): 
  q =  request.GET.get('q') if request.GET.get('q') != None else ''
  
  rooms = Room.objects.filter(
    Q(topic__name__icontains=q) |
    Q(name__icontains=q) |
    Q(description__icontains=q)
    )
  
  topics = Topic.objects.all()[0:10]
  room_count = rooms.count()
  room_messages = Message.objects.filter(
    Q(room__topic__name__icontains=q))

  context = {'rooms': rooms, 'topics':topics, 'room_count': room_count, 'room_messages': room_messages}
  return render(request, 'base/home.html', context)


def room(request, pk): 
  room = Room.objects.get(id=pk)
  room_messages = room.message_set.all()
  participants = room.participants.all()

  if request.method == 'POST':
    message = Message.objects.create(
      user=request.user,
      room=room,
      body=request.POST.get('body')
    )
    room.participants.add(request.user)
    return redirect('room', pk=room.id)

  context = {'room': room, 'room_messages': room_messages, 'participants': participants}
  return render(request, 'base/room.html', context)

def userProfile(request, pk):
  user =User.objects.get(id=pk)
  rooms = user.room_set.all()
  room_messages = user.message_set.all()
  topics = Topic.objects.all()

  context = {'user': user, 'rooms': rooms, 'room_messages': room_messages, 'topics': topics}
  return render(request, 'base/profile.html', context)

@login_required(login_url='signin')
def createRoom(request):
  form = RoomForm()
  topics = Topic.objects.all()
  if request.method == 'POST':
    topic_name = request.POST.get('topic')
    topic, created = Topic.objects.get_or_create(name=topic_name)

    Room.objects.create(
      host = request.user,
      topic = topic,
      name = request.POST.get('name'),
      description = request.POST.get('description'),
    )
    return redirect('home')


  context = {'form':form, 'topics':topics}
  return render(request, 'base/room_form.html', context)


@login_required(login_url='signin')
def updateRoom(request, pk):
  room = Room.objects.get(id=pk)
  form =RoomForm(instance=room)
  topics = Topic.objects.all()

  # if request.user != room.host:
  #   return HttpResponse('You are not allowed here')

  if request.method == 'POST':
    topic_name = request.POST.get('topic')
    topic, created = Topic.objects.get_or_create(name=topic_name)
    room.name = request.POST.get('name')
    room.topic = topic
    room.description = request.POST.get('description')
    room.save()

    return redirect('home')

  context = {'form':form, 'topics':topics, 'room':room}
  return render(request, 'base/room_form.html', context)


@login_required(login_url='signin')
def deleteRoom(request, pk):
  room = Room.objects.get(id=pk)

  if request.user != room.host:
    return HttpResponse('You are not allowed here')

  if request.method == 'POST':
    room.delete()
    return redirect('home')

  context = {'obj':room}
  return render(request, 'base/delete.html', context)

@login_required(login_url='signin')
def deleteMessage(request, pk):
  message = Message.objects.get(id=pk)

  if request.user != message.user:
    return HttpResponse('You are not allowed here')

  if request.method == 'POST':
    room_id = message.room.id
    message.delete()
    return redirect('room', pk=room_id)

  context = {'obj':message}
  return render(request, 'base/delete.html', context)

@login_required(login_url='login')
def updateUser(request):
  user = request.user
  form = UserForm(instance=user)

  if request.method == 'POST':
    form = UserForm(request.POST, request.FILES, instance=user)
    if form.is_valid():
      form.save()
      return redirect('user-profile', pk=user.id)

  context = {'form': form}
  return render(request, 'base/update-user.html', context)

def topicsPage(request):
  q =  request.GET.get('q') if request.GET.get('q') != None else ''
  topics = Topic.objects.filter(name__icontains=q)

  context = {'topics': topics}
  return render(request, 'base/topics.html', context)

def activityPage(request):
  room_messages = Message.objects.all()
  return render(request, 'base/activity.html', {'room_messages': room_messages})