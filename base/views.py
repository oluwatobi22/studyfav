from django.shortcuts import redirect, render
from django.http import HttpResponse
from django.contrib import messages
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from .models import Room, Topic
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .forms import RoomForm

# Create your views here.

# rooms = [
#   {'id':1, 'name': 'Lets Learn Python'},
#   {'id':2, 'name': 'Lets Learn django'},
#   {'id':3, 'name': 'Backend Developers'}
# ]

def signinPage(request):

  page = 'signin'

  if request.user.is_authenticated:
    return redirect('home')

  if request.method == 'POST':
    username = request.POST.get('username')
    password = request.POST.get('password')

    user = authenticate(request, username=username, password=password)
    
    if user is not None:
      login(request, user)
      return redirect('home')
    else:
      messages.error(request, 'Username OR Password does not exist')
  
  context = {'page': page}
  return render(request, 'base/signin_signup.html', context)

def logoutUser(request):
  logout(request)
  return redirect('home') 

def signupPage(request):
    form = UserCreationForm()
    context = {'form': form}

    if request.method == 'POST':
      form = UserCreationForm(request.POST)
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
  
  topics = Topic.objects.all()
  room_count = rooms.count() 

  context = {'rooms': rooms, 'topics':topics, 'room_count': room_count}
  return render(request, 'base/home.html', context)


def room(request, pk): 
  room = Room.objects.get(id=pk)
  context = {'room': room}
  return render(request, 'base/room.html', context)


@login_required(login_url='signin')
def createRoom(request):
  form = RoomForm()
  if request.method == 'POST':
    form = RoomForm(request.POST)
    if form.is_valid():
      form.save()
      return redirect('home')


  context = {'form':form}
  return render(request, 'base/room_form.html', context)


@login_required(login_url='signin')
def updateRoom(request, pk):
  room = Room.objects.get(id=pk)
  form =RoomForm(instance=room)

  # if request.user != room.host:
  #   return HttpResponse('You are not allowed here')

  if request.method == 'POST':
    form = RoomForm(request.POST, instance=room) 
    if form.is_valid():
      form.save()
      return redirect('home')

  context = {'form':form}
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
