"""aeronautica URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect
from users import views as user_views
from core import views as core_views

from django.contrib.auth.views import (PasswordResetView, PasswordResetDoneView,
                PasswordResetConfirmView, PasswordResetCompleteView, LogoutView)

admin.site.site_header = 'AeroNautica'
admin.site.index_title = 'Administration Area'
admin.site.site_title = 'AeroNautica'


web_user_urls = [
    path('register/', user_views.Register, name='web-register'),
    path('login/', user_views.user_web_login, name='web-login'),
    path('logout/', LogoutView.as_view(
        template_name='users/logout.html'), 
        name='web-logout'),
    path('password/change/', user_views.password_change, name='web-password-change'),
    path('user/profile/', user_views.profile_page, name='web-user-profile'),
    ###PASSWORD RESET VIEWS
    path(
        'password-reset/', 
        PasswordResetView.as_view(
            template_name='users/password_reset.html'),  
            name='password_reset'
        ),
    path(
        'password-reset/done/', 
        PasswordResetDoneView.as_view(
            template_name='users/password_reset_done.html'),  
            name='password_reset_done'
        ),
    path(
        'password-reset-confirm/<uidb64>/<token>', 
        PasswordResetConfirmView.as_view(
            template_name='users/password_reset_confirm.html'), 
            name='password_reset_confirm'
        ),
    path(
        'password-reset-complete/', 
        PasswordResetCompleteView.as_view(
            template_name='users/password_reset_complete.html'),  
            name='password_reset_complete'
        ),
]

urlpatterns = [
    path('', core_views.home_view, name='index'),
    path('admin/', admin.site.urls),
] + web_user_urls 
