
from rest_framework import urlpatterns
from django.urls import path, include
from users.api import views 
from rest_framework.routers import DefaultRouter

app_name = 'users'

router = DefaultRouter()
 # IsAdmin - Privilages to update and list
router.register(r'profiles', views.ProfileModelViewSet)

urlpatterns = [
    path('register/', 
            views.RegisterNewUserAPIView.as_view(), 
            name='api-user-register'),
    path('profile/', 
            views.ProfileRetrieveUpdateAPIView.as_view(), 
            name='current-user-profile'),
    path('', include(router.urls)),
    # for rest auth, login logout
    path('rest-auth/user/', 
            views.CurrentUserDisplayAPIView.as_view(), 
            name='current-user'), # Overwrite rest_auth user view
    path('rest-auth/', include('rest_auth.urls')),

] 