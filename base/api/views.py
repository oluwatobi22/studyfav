from django.http import Http404
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import  Response 
from base.models import Room
from .serializers import RoomSerializer

@api_view(['GET'])
def getRoutes(request, *args, **kwargs):
  routes = [
    'GET /api',
    'GET /api/rooms',
    'GET /api/rooms/:id'
  ]

  return Response(routes)

@api_view(['GET'])
def getRooms(request):
  rooms = Room.objects.all()
  serializer = RoomSerializer(rooms, many=True)
  return Response(serializer.data)

@api_view(['GET'])
def getRoom(request, pk):
  try:
    room = Room.objects.get(id=pk)
    serializer = RoomSerializer(room, many=False)
    return Response(serializer.data)
  except Room.DoesNotExist:
    return Response(status=status.HTTP_404_NOT_FOUND)