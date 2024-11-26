from django.shortcuts import render
from .serializers import UserSerializer
from rest_framework import viewsets
from core.models import User
from rest_framework import permissions

# ViewSets define the view behavior.
# ModelViewSet maps HTTP methods to action (list(), retrieve(), create()...)
class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]
