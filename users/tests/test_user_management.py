from django.core.exceptions import NON_FIELD_ERRORS
from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from core.models import Profile
from django.urls import reverse
from rest_framework import status
from django.conf import settings
from pprint import pprint

import re
from django.core import mail

#Tested URL Endpoints
LOGIN_URL = settings.LOGIN_URL
LOGIN_REDIRECT_URL = settings.LOGIN_REDIRECT_URL
LOGOUT_URL = reverse('web-logout')
REGISTER_URL = reverse('web-register')
USER_PROFILE_URL = reverse('web-user-profile')
PASSWORD_CHANGE_URL = reverse('web-password-change')

#HELPER FUNCTIONS
def user_exists(email_val):
    return get_user_model().objects.filter(email=email_val).exists()

def profile_exists(email_val):
    user = get_user_model().objects.get(email=email_val)
    return Profile.objects.filter(user=user).exists()

def create_user(**params):
    return get_user_model().objects.create_user(**params)


class PublicPagesAutenticationTests(TestCase):
    """ Test Login Register End Points on Web page"""

    def setUp(self):
        self.client = Client()
        # self.csrf_client = Client(enforce_csrf_checks=True)

        self.register_credentials = {
            'first_name': 'UserFirstName',
            'last_name': 'Testsurname',
            'password1': 'Testing321..',
            'password2': 'Testing321..',
            'email': 'testunit@domain.com',
            'verify_email': 'testunit@domain.com',
            'title': 'mr.', 
            'company': 'TestCompany', 
            'position': 'Director', 
            'country': 'Kyrat', 
            'city': 'SomeCity',
        }

        self.credentials = {
            'email': 'testunit@domain.com',
            'password': 'Testing321..',
            'first_name': 'UserFirstName',
            'last_name': 'Testsurname',
        }

    
    def test_web_login_get_request(self):
        """Test get request to login page and status code"""
        url = reverse(LOGIN_URL)
        resp = self.client.get(url, follow=True)
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(template_name='users/login.html')
       

    def test_register_get_request(self):
        """Test register page is loaded with get request"""
        resp = self.client.get(REGISTER_URL)
        self.assertTemplateUsed(template_name='users/register.html')
        self.assertEqual(resp.status_code, 200)


    def test_register_a_new_user_successfully(self):
        """Test if register pages adds new user and profile
        """
        resp = self.client.post(REGISTER_URL, self.register_credentials)
        self.assertTemplateUsed(template_name='users/register.html')
        # Check if user and profile created
        self.assertTrue(user_exists(self.register_credentials['email']))
        self.assertTrue(profile_exists(self.register_credentials['email']))
        # TEST IF REDIRECTS TO LOGIN PAGE AFTER REGISTER
        self.assertRedirects(resp, reverse('web-login'), 
                    status_code=302, 
                    target_status_code=200, 
                    fetch_redirect_response=True)


    def test_register_existing_user(self):
        """Test registering an existing user"""
        user = create_user(**self.credentials)
        self.assertTrue(user_exists(user.email))
        self.assertTrue(profile_exists(user.email))
        resp = self.client.post(REGISTER_URL, self.register_credentials)
        self.assertFormError(resp, form='u_form', field='email', 
                errors=None, msg_prefix='None')
        num_users = get_user_model().objects.filter(email=user.email).count()
        num_profiles = Profile.objects.count()
        self.assertEqual(num_users,1)
        self.assertEqual(num_profiles,1)


    def test_register_without_email_verification(self):
        """Test if existing user can register again"""
        missed_credentials = self.register_credentials
        missed_credentials['verify_email'] = 'someanotheremaiol@test.com'
        resp = self.client.post(REGISTER_URL, missed_credentials, follow=True)
        self.assertFormError(resp, form='u_form', field='email', 
                errors=None, msg_prefix='Your emails must match.')
        

    def test_register_without_email(self):
        """Test if registers without email"""
        missed_credentials = self.register_credentials
        del missed_credentials['email']
        del missed_credentials['verify_email']
        resp = self.client.post(REGISTER_URL, missed_credentials, follow=True)
        self.assertFormError(resp, form='u_form', field='email', 
                errors=None, msg_prefix=None)


    def test_register_without_password_verification(self):
        """Test if registers without password verification"""
        missed_credentials = self.register_credentials
        missed_credentials['password2'] = 'somerandompassword'
        resp = self.client.post(REGISTER_URL, missed_credentials, follow=True)
        self.assertFormError(resp, form='u_form', field='password', 
                errors=None, msg_prefix='Your emails must match.')


    def test_register_without_company(self):
        """Test if registers without company information"""
        missed_credentials = self.register_credentials
        del missed_credentials['company']
        resp = self.client.post(REGISTER_URL, missed_credentials, follow=True)
        self.assertFormError(resp, form='p_form', field=None, 
                errors=None, msg_prefix=None)


    def test_web_login(self):
        """Test login status code, and login successfull"""
        user = create_user(**self.credentials)

        login_resp = self.client.post(reverse(LOGIN_URL), 
            {
                'email': self.credentials['email'],
                'password': self.credentials['password'],
            }, 
            follow=True)

        request_user = login_resp.context['user']
        self.assertTrue(request_user.is_authenticated)

        ### CHECK PROFILE IS THE SAME
        self.assertEqual(
            request_user.profile, Profile.objects.get(user=user)
        )

        self.assertRedirects(login_resp, reverse('web-user-profile'), 
                    status_code=302, 
                    target_status_code=200, 
                    fetch_redirect_response=True)


class PrivateWebUserTests(TestCase):
    """ Test Private user management web endpoints
        When user is logged in.
    """

    def setUp(self):
        self.client = Client()

        self.credentials = {
            'email': 'testunit@domain.com',
            'password': 'Testing321..',
            'first_name': 'UserFirstName',
            'last_name': 'Testsurname',
        }

        
        self.user = get_user_model().objects.create_user(
            **self.credentials
        )

        self.profile_info = {
            'company': 'TestCompany',
            'title': 'Mr.',
            'position': 'Some Speicific Position',
            'country': 'Some Specific Country Name',
            'city': 'Some Specific City Name',
        }

        self.profile = Profile.objects.get(user=self.user)
        self.profile.company = self.profile_info['company']
        self.profile.title = self.profile_info['title']
        self.profile.position = self.profile_info['position']
        self.profile.country = self.profile_info['country']
        self.profile.city = self.profile_info['city']
        self.profile.save()
        self.client.force_login(self.user)

        


    def test_web_logout(self):
        """Test web page logout function"""
        
        self.assertTrue(self.user.is_authenticated)

        resp = self.client.post(LOGOUT_URL)
        self.assertEqual(resp.status_code, 200)
        resp_user = resp.context['user']
        self.assertFalse(resp_user.is_authenticated)
        self.assertTemplateUsed(template_name='users/logout.html')
 

    def test_get_profile_page_when_authorized(self):
        """Test succesful get request to user profile page when authed"""
        resp = self.client.get(USER_PROFILE_URL)
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, self.user.email)
        ## Testing if loaded forms contains data
        self.assertContains(resp, self.user.first_name)
        self.assertContains(resp, self.user.last_name)
        self.assertContains(resp, self.profile.company)
        self.assertContains(resp, self.profile.position)
        self.assertContains(resp, self.profile.country)
        self.assertContains(resp, self.profile.city)
        self.assertContains(resp, self.profile.title)
        self.assertNotContains(resp, self.credentials['password'])
        ## test request user
        self.assertEqual(self.user, resp.context['request'].user)


    def test_post_profile_page_if_updates_user_successfully(self):
        """Test the functionality of update in profile page
            for both User and Profile Models"""

        resp = self.client.post(USER_PROFILE_URL, {
            'first_name': 'New Test Name',
            'company': 'New Updated Company',
            'title': 'Mrs.',
            'position': 'New Speicific Position',
            'country': 'New Specific Country Name',
            'city': 'New Specific City Name',
        }, follow=True)
        self.assertEqual(resp.status_code, 200)
        request_user = resp.context['user']
        self.assertEqual(self.user, request_user)
        self.assertEqual(request_user.profile.company, 'New Updated Company')
        self.assertEqual(request_user.profile.position, 'New Speicific Position')
        self.assertEqual(request_user.profile.country, 'New Specific Country Name')
        self.assertEqual(request_user.first_name, 'New Test Name')


    def test_password_change_functionality(self):
        """Test if password is changed succesfully using
            web-password-change page
        """
        resp = self.client.get(PASSWORD_CHANGE_URL)
        self.assertEqual(resp.status_code, 200)
        resp = self.client.post(
            PASSWORD_CHANGE_URL,
            {
                'old_password': self.credentials['password'],
                'new_password1': 'NewTesting321..',
                'new_password2': 'NewTesting321..',
            },
            follow=True
        )
        self.assertEqual(resp.status_code, 200)

        request_user = resp.context['user']
        self.assertEqual(self.user, request_user)
        self.assertTrue(
            request_user.check_password('NewTesting321..')
        )



class TestUnauthorizedAccess(TestCase):
    """Test unauthorized access to login required pages"""

    def setUp(self):
        self.client = Client()

    def test_get_profile_page_when_not_authorized(self):
        """Test if NO unauthorized access to Profile page"""
        resp = self.client.get(USER_PROFILE_URL)
        redirect_url = '/login/?next=' + USER_PROFILE_URL
        self.assertRedirects(resp, expected_url=redirect_url, 
            status_code=302, 
            target_status_code=200, 
            fetch_redirect_response=True)


    def test_password_change_page(self):
        resp = self.client.get(PASSWORD_CHANGE_URL)
        redirect_url = '/login/?next=' + PASSWORD_CHANGE_URL
        self.assertRedirects(resp, expected_url=redirect_url, 
            status_code=302, 
            target_status_code=200, 
            fetch_redirect_response=True)



class PasswordResetTests(TestCase):
    """Test password reseting"""
    def setUp(self):
        self.client = Client()
        self.credentials = {
            'email': 'alper.akbas@analyticaadvisory.com',
            'password': 'Testing321..',
            'first_name': 'UserFirstName',
            'last_name': 'Testsurname',
        }

        self.user = get_user_model().objects.create_user(
            **self.credentials
        )
        self.reset_url = reverse('password_reset')

        
    def test_mail_send(self):
        """Test email sends succesfully"""
        mail.send_mail('Subject here', 'Here is the message.',
            'alper@aeronautica.services', [self.credentials['email']],
            fail_silently=False)
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, 'Subject here')


    def test_password_reset_access(self):
        """test access to password reset page"""
        resp = self.client.get(self.reset_url )
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(template_name='users/password_reset.html')
        self.assertNotContains(resp, 'DJANGO ADMINISTRATION')


    def test_password_reset_process(self):
        """Test resetting email"""
      
        pre_user = get_user_model().objects.get(email=self.credentials['email'])
        self.assertTrue(pre_user.check_password(self.credentials['password']))

        email_data = {
            'email': self.credentials['email']
        }
        # Make a password reset request by user
        resp = self.client.post(self.reset_url,
                    email_data,
                    follow=True)
        
        self.assertEqual(resp.status_code, 200)

        # Check generated email and retrieve uidb64 and token
        mail_body = mail.outbox[0].body
        ##### GET THE URL including uid and token
        res_url = re.findall(
            'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', 
            mail_body)[0]
        tokens = res_url.replace('http://example.com/password-reset-confirm/','').split('/')     
        token_data = {
            'uidb64': tokens[0],
            'token': tokens[1],
        }
        # Initiate password resetting
        password_reset_data = {
            "new_password1": "newtest1234",
            "new_password2": "newtest1234"
        }

        url = reverse('password_reset_confirm', kwargs=token_data)
        # Make the first request to retrieve url like /password-reset-confirm/<??>/set-password
        password_reset_response = self.client.get(url, follow=True)
        path = password_reset_response.request["PATH_INFO"]
        
        # Confirm and reset the password with new one
        password_reset_process = self.client.post(path, password_reset_data, format='json', follow=True)
        ### Check if redirects to complete page
        self.assertRedirects(password_reset_process, reverse('password_reset_complete'))

        ### Check if user password changed succesfully
        post_user = get_user_model().objects.get(email=self.credentials['email'])
        self.assertTrue(post_user.check_password('newtest1234'))


   