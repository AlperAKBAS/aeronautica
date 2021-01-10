from django.contrib.auth import get_user_model
from rest_framework import generics
from rest_framework.response import Response
from rest_framework.views import APIView
from users.api.serializers import (RegisterNewUserSerializer, 
            UserDisplaySerializer, ProfileSerializer, ProfileSerializerForAdmin)

from rest_framework.permissions import IsAuthenticated, IsAdminUser
from core.models import Profile
from rest_framework.viewsets import GenericViewSet
from rest_framework import mixins



class RegisterNewUserAPIView(generics.CreateAPIView):
    """Create a new user"""
    serializer_class = RegisterNewUserSerializer


class ProfileRetrieveUpdateAPIView(generics.RetrieveUpdateAPIView):
    """View user profile - only request user can see and update its own profile"""
    
    serializer_class = ProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user.profile
  

class ProfileModelViewSet( 
                    mixins.UpdateModelMixin,
                    mixins.ListModelMixin,
                    mixins.RetrieveModelMixin,
                    GenericViewSet
):
    """Admins can see all the profiles"""
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializerForAdmin
    permission_classes = [IsAuthenticated, IsAdminUser]


class CurrentUserDisplayAPIView(APIView):
    """Read only access the current user and user profile info"""
    permission_classes = [IsAuthenticated]
    def get(self, request):
        serializer = UserDisplaySerializer(request.user)
        return Response(serializer.data)