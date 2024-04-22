from . import views
from django.urls import path 

urlpatterns = [
  path('signin/', views.signinPage, name='signin'),
  path('logout/', views.logoutUser, name='logout'),
  path('signup/', views.signupPage, name='signup'),
  path('', views.home, name='home'),
  path('room/<str:pk>/', views.room, name='room'),
  path('create-room/', views.createRoom, name='create-room'),
  path('update-room/<str:pk>/', views.updateRoom, name='update-room'),
  path('delete-room/<str:pk>/', views.deleteRoom, name='delete-room'),
  path('delete-message/<str:pk>/', views.deleteMessage, name='delete-message'),
]