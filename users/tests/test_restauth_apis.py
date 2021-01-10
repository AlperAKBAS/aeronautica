from django.http.response import JsonResponse
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status

from django.conf import settings
from core.models import Profile
from users.api.serializers import (ProfileSerializer, UserDisplaySerializer)
from rest_framework.renderers import JSONRenderer
from rest_framework.authtoken.models import Token

def create_user(**params):
    return get_user_model().objects.create_user(**params)

def user_exists(email_val):
    return get_user_model().objects.filter(email=email_val).exists()

def profile_exists(user_instance):
    return Profile.objects.filter(user=user_instance).exists()

def get_profiles(user_instance):
    return Profile.objects.filter(user=user_instance)

User = get_user_model()

"""  
USER MANAGEMENT REST END POINTS
#/api-auth/login/	django.contrib.auth.views.LoginView	rest_framework:login
/api-auth/logout/	django.contrib.auth.views.LogoutView	rest_framework:logout
/api/user/	rest_framework.routers.APIRootView	users:api-root
/api/user/\.<format>/	rest_framework.routers.APIRootView	users:api-root
# /api/user/current/	users.api.views.CurrentUserDisplayAPIView	users:current-user
#/api/user/profile/	users.api.views.ProfileRetrieveUpdateAPIView	users:user-profile
# /api/user/profiles/	users.api.views.ProfileModelViewSet	users:profile-list
# /api/user/profiles/<pk>/	users.api.views.ProfileModelViewSet	users:profile-detail
/api/user/profiles/<pk>\.<format>/	users.api.views.ProfileModelViewSet	users:profile-detail
/api/user/profiles\.<format>/	users.api.views.ProfileModelViewSet	users:profile-list
# /api/user/register/	users.api.views.RegisterNewUserAPIView	users:api-user-create
# /api/user/rest-auth/login/	rest_auth.views.LoginView	users:rest_login
# /api/user/rest-auth/logout/	rest_auth.views.LogoutView	users:rest_logout
/api/user/rest-auth/password/change/	rest_auth.views.PasswordChangeView	users:rest_password_change
/api/user/rest-auth/password/reset/	rest_auth.views.PasswordResetView	users:rest_password_reset
/api/user/rest-auth/password/reset/confirm/	rest_auth.views.PasswordResetConfirmView	users:rest_password_reset_confirm
# /api/user/rest-auth/user/	rest_auth.views.UserDetailsView	users:rest_user_details
"""

URL_REGISTRATION = reverse('users:api-user-register')
URL_BROWSABLE_API_LOGIN = reverse('rest_framework:login')
URL_BROWSABLE_API_LOGOUT = reverse('rest_framework:logout')
URL_CURRENT_USR = reverse('users:current-user-profile') # request user
URL_CURRENT_USER_DISPLAY = reverse('users:current-user')
# REST_AUTH URLS
URL_REST_AUTH_LOGIN = reverse('users:rest_login')
URL_REST_AUTH_LOGOUT = reverse('users:rest_logout')
URL_REST_AUTH_PASSWORD_CHANGE = reverse('users:rest_password_change')
URL_REST_AUTH_PASSWORD_RESET = reverse('users:rest_password_reset')
URL_REST_AUTH_PASSWORD_RESET_CONFIRM = reverse('users:rest_password_reset_confirm')
# PROFILE MODEL VIEWSET URLS # ONLY ADMIN ACCESS
URL_USER_PROFILE_LIST = reverse('users:profile-list')
## URL_USER_PROFILE_DETAIL = Constucted in the test functions


class PublicUserRestAuthAPITests(TestCase):
    """Tests the users API (public)"""
    def setUp(self):
        self.client = APIClient()
        self.register_credentials = {
            'email': 'testunit@domain.com',
            'verify_email': 'testunit@domain.com',
            'first_name': 'UserFirstName',
            'last_name': 'Testsurname',
            'password': 'Testing321..',
            'verify_password': 'Testing321..',
            'title': 'mr.', 
            'company': 'TestCompany', 
            'position': 'Director', 
            'country': 'Kyrat', 
            'city': 'SomeCity',
        }

        self.credentials = {
            'email': 'testunit@domain.com',
            'password': 'Testing321..',
        }

    def test_register_user(self):
        """Tests /api/rest-auth/registration/ end point
            with valid data"""
        resp_get = self.client.get(URL_REGISTRATION)
        self.assertEqual(
            resp_get.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        resp = self.client.post(
            URL_REGISTRATION,
            self.register_credentials,
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        user = User.objects.get(**resp.data)
        self.assertTrue(user.check_password(self.register_credentials['password']))
        self.assertNotIn('password', resp.data)
        self.assertNotIn(self.register_credentials['password'], resp.data)
        self.assertTrue(profile_exists(user))
        profiles=get_profiles(user)
        self.assertEqual(profiles.count(),1)
        profile=profiles[0]
        self.assertEqual(profile.company, self.register_credentials['company'])
        self.assertEqual(profile.position, self.register_credentials['position'])


    def test_register_existing_user(self):
        """Test creating a duplicate user"""
        create_user(**{
            'email': 'testunit@domain.com',
            'first_name': 'UserFirstName',
            'last_name': 'Testsurname',
            'password': 'Testing321..',
        })

        register_resp = self.client.post(
                    URL_REGISTRATION,
                    self.register_credentials,
                )
        self.assertEqual(register_resp.status_code, status.HTTP_400_BAD_REQUEST)


    def test_register_password_too_short(self):
            """Test register if password in less than 6 characters"""
            credentials = self.register_credentials
            credentials['password'] = 'Test'
            credentials['verify_password'] = 'Test'
    
            resp = self.client.post(URL_REGISTRATION, credentials)
            self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
            self.assertFalse(user_exists(credentials['email']))

    def test_register_unmatching_passwords(self):
            """Test regsiter if passwords not matchig"""
            credentials = self.register_credentials
            credentials['verify_password'] = 'Testing321'
    
            resp = self.client.post(URL_REGISTRATION, credentials)
            self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
            self.assertFalse(user_exists(credentials['email']))

    def test_register_with_invalid_email(self):
        """Test register with invalid email"""
        credentials = self.register_credentials
        credentials['emeail'] = 'Test'
        credentials['verify_email'] = 'Test.com'

        resp = self.client.post(URL_REGISTRATION, credentials)
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        ## Check if user created
        self.assertFalse(user_exists(credentials['email']))

    def test_register_with_unmatching_emails(self):
        """Test register with different emails"""
        credentials = self.register_credentials

        credentials['verify_email'] = 'testunitdiff@domain.com'

        resp = self.client.post(URL_REGISTRATION, credentials)
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        ## Check if user created
        self.assertFalse(user_exists(credentials['email']))      
        self.assertFalse(user_exists(credentials['verify_email']))      

    def test_register_without_profile_info(self):
        """Test registering without profile info"""
        credentials = self.register_credentials
        credentials.pop('company')
        credentials.pop('title')
        credentials.pop('position')
        credentials.pop('city')
        credentials.pop('country')

        resp = self.client.post(URL_REGISTRATION, credentials)
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)  
        self.assertFalse(user_exists(credentials['email']))   
        self.assertFalse(
            Profile.objects.filter(user__email=credentials['email']).exists()
        )


class TestLoginUrls(TestCase):
    """Test API login endpoints    """
    def setUp(self):
        self.client = APIClient()
        self.email = 'testunit@domain.com'
        self.password = 'Testing321..'
        self.user = create_user(**{
            'email': self.email,
            'first_name': 'UserFirstName',
            'last_name': 'Testsurname',
            'password': self.password,
        })


    def test_login(self):
        """Test api login url and the key"""
        login_resp = self.client.post(
            URL_REST_AUTH_LOGIN,
            {
                'email': self.email,
                'password': self.password,
            }
        )
        self.assertEqual(login_resp.status_code, status.HTTP_200_OK)
        self.assertIn('key', login_resp.data)
        self.assertNotIn('password', login_resp.data)
        self.assertNotIn(self.password, login_resp.data)
        token = Token.objects.get(user=self.user)
        self.assertEqual(login_resp.data.get('key'), token.key)

    def test_login_with_wrong_email(self):
        """Test login with wrong email"""
        self.assertTrue(user_exists(self.email))
        login_resp = self.client.post(
            URL_REST_AUTH_LOGIN,
            {
                'email': 'testunitwrong@domain.com',
                'password': self.password,
            }
        )
        self.assertEqual(login_resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_login_with_wrong_pasword(self):
        """Test login with wrong password"""
        self.assertTrue(user_exists(self.email))
        login_resp = self.client.post(
            URL_REST_AUTH_LOGIN,
            {
                'email': self.email,
                'password': 'TestiNG321..',
            }
        )
        self.assertEqual(login_resp.status_code, status.HTTP_400_BAD_REQUEST)


    def test_browsable_api_sucesffull_login(self):
        """Test succesfull login via browsable api page"""
        login_resp = self.client.post(
            URL_REST_AUTH_LOGIN,
            {
                'email': self.email,
                'password': self.password,
            }
        )
        self.assertEqual(login_resp.status_code, status.HTTP_200_OK)

    def test_browsable_api_failed_login(self):
        """Test succesfull login via browsable api page"""
        login_resp = self.client.post(
            URL_REST_AUTH_LOGIN,
            {
                'email': 'testtest@different.com',
                'password': self.password,
            }
        )
        self.assertEqual(login_resp.status_code, status.HTTP_400_BAD_REQUEST)




class PrivateUserRestAuthAPITests(TestCase):
    """Tests the users API (private endpoints)"""
    def setUp(self):
        self.client = APIClient()
        self.profile_info = {
            'title': 'mr.', 
            'company': 'TestCompany', 
            'position': 'Director', 
            'country': 'Kyrat', 
            'city': 'SomeCity',
        }
        self.email = 'testunit@domain.com'
        self.password = 'Testing321..'
        self.credentials = {
            'email': self.email,
            'password': self.password,
            'first_name': 'UserFirstName',
            'last_name': 'Testsurname',
        }

        self.user = create_user(**self.credentials)
        self.client.force_login(self.user)
        self.profile = Profile.objects.get(user=self.user)
        self.profile.title = self.profile_info.get('title')
        self.profile.company = self.profile_info.get('company')
        self.profile.position = self.profile_info.get('position')
        self.profile.country = self.profile_info.get('country')
        self.profile.city = self.profile_info.get('city')
        self.profile.save()

    def test_logout(self):
        """Test logout endpoints"""
        self.assertTrue(user_exists(self.email))
        logout_resp = self.client.get(URL_REST_AUTH_LOGOUT)
        self.assertTrue(logout_resp.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
        logout_resp = self.client.post(URL_REST_AUTH_LOGOUT)
        self.assertTrue(logout_resp.status_code, status.HTTP_200_OK)
        self.assertAlmostEqual(
            logout_resp.data,
            {"detail": "Successfully logged out."}
            )

    def test_current_user_profile(self):
        """Test if the current user can view profile info
        """
        resp = self.client.get(URL_CURRENT_USR)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        serializer = ProfileSerializer(self.profile)
        data = JSONRenderer().render(serializer.data)
        self.assertContains(resp, data)
        self.assertEqual(resp.data, serializer.data)


    def test_current_user_profile_with_unauthorized_access(self):
        """Test unauthorized access to user profile info
        """
        self.client.logout()
        resp = self.client.get(URL_CURRENT_USR)
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)
       
    def test_current_user_display(self):
        """
            Tests the current user display view, including profile and user info
            !!!Can be challending, since overwrites the rest-auth user url
        """
        resp = self.client.get(URL_CURRENT_USER_DISPLAY)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        # Only get request is accepted
        allow_methods = resp._headers.get('allow')[1]
        self.assertEqual(allow_methods, 'GET, HEAD, OPTIONS')

        serializer = UserDisplaySerializer(self.user, data=resp.data)
        self.assertTrue(serializer.is_valid())

    def test_current_user_display_with_unauthorized_access(self):
        """
            Tests the current user display view, with unauthorize access
            !!!Can be challending, since overwrites the rest-auth user url
        """
        self.client.logout()
        resp = self.client.get(URL_CURRENT_USER_DISPLAY)
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)

    # Profiles ViewSet
    def test_profile_list_for_admin_unsuccesfull(self):
        """Test if profile list cannot be viewed by non admin users"""
        resp = self.client.get(
            URL_USER_PROFILE_LIST
        )
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)

    def test_profile_list_for_admin_succesfull(self):
        """Test if profile list is viewed by admin"""
        self.user.is_staff = True
        self.user.save()
        resp = self.client.get(
            URL_USER_PROFILE_LIST
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

    def test_profile_list_for_admin_unauthorized(self):
        """Test if profile list is viewed by unauth users"""
        self.client.logout()
        resp = self.client.get(
            URL_USER_PROFILE_LIST
        )
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)

    def test_profile_detail_for_admin_unsuccesfull(self):
        """Test if profile detail cannot be viewed by non admin users"""
        profile = Profile.objects.first()
        URL_USER_PROFILE_DETAIL = reverse('users:profile-detail', 
                    kwargs={'pk':profile.id})
        resp = self.client.get(
            URL_USER_PROFILE_DETAIL
        )
        resp = self.client.get(
            URL_USER_PROFILE_DETAIL
        )
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)

    def test_profile_list_for_admin_succesfull(self):
        """Test if profile detail page is viewed by admin"""
        self.user.is_staff = True
        self.user.save()
        self.assertGreater(Profile.objects.count(), 0)
        profile = Profile.objects.first()
        URL_USER_PROFILE_DETAIL = reverse('users:profile-detail', 
                    kwargs={'pk':profile.id})
        resp = self.client.get(
            URL_USER_PROFILE_DETAIL
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)      


    def test_profile_detail_for_admin_unauthorized(self):
        """Test if profile detail cannot be viewed by unauth users"""
        self.client.logout()
        profile = Profile.objects.first()
        URL_USER_PROFILE_DETAIL = reverse('users:profile-detail', 
                    kwargs={'pk':profile.id})
        resp = self.client.get(
            URL_USER_PROFILE_DETAIL
        )
        resp = self.client.get(
            URL_USER_PROFILE_DETAIL
        )
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)