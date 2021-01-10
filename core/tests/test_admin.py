from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from core.models import Profile
from django.urls import reverse
from rest_framework import status

# Cient Doc: https://docs.djangoproject.com/en/2.2/topics/testing/tools/#overview-and-a-quick-example
class AdminSiteTests(TestCase):

    def setUp(self):
        """test client, admin_user and user created"""
        self.client = Client()
        self.admin_user = get_user_model().objects.create_superuser(
            email = 'admin@testdomain.com',
            first_name= 'Alpertest',
            last_name = 'Akbastest',
            password = 'Testing321..',

        )
        self.client.force_login(self.admin_user)
        self.user = get_user_model().objects.create_user(
            email = 'test@domain.com',
            first_name= 'UserFirstName',
            last_name = 'Testsurname',
            password = 'Testing321..',
        )
        self.user.save()


    def test_users_listed(self):
        """Test if users are listed in the users page"""
        url = reverse('admin:core_user_changelist')
        resp = self.client.get(url)
        self.assertContains(resp, self.user.first_name)
        self.assertContains(resp, self.user.last_name)
        self.assertContains(resp, self.user.email)
   


    def test_user_change_page(self):
        """Test if user edit / change page workds correctly """
        url = reverse('admin:core_user_change', args=[self.user.id])
        resp = self.client.get(url)

        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, self.user.email)
        self.assertContains(resp, self.user.first_name)
        self.assertContains(resp, self.user.last_name)
        self.assertContains(resp,'Is active')
        self.assertContains(resp,'Is staff')
        self.assertContains(resp,'Superuser status')
        self.assertContains(resp,'Is demo user')
        self.assertContains(resp,'Is admin')
        self.assertContains(resp,'Last login:')


    def test_create_user_page(self):
        """Test the add user page on admin """
        url = reverse('admin:core_user_add')
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp,'Email')
        self.assertContains(resp,'Password')
        self.assertContains(resp,'Password confirmation:')
        self.assertContains(resp,'First name:')
        self.assertContains(resp,'Last name:')

    def test_user_history_page(self):
        """Test the user history page on admin """
        url = reverse('admin:core_user_history', args=[self.user.id])
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, self.user.email)



class AdminSiteProfileTests(TestCase):
    """Test for Profile Admin Page"""
    def setUp(self):
        """test client, admin_user and user created"""
        self.client = Client()
        self.admin_user = get_user_model().objects.create_superuser(
            email = 'admin@testdomain.com',
            first_name= 'Alpertest',
            last_name = 'Akbastest',
            password = 'Testing321..',

        )
        self.client.force_login(self.admin_user)
        self.user = get_user_model().objects.create_user(
            email = 'test@domain.com',
            first_name= 'UserFirstName',
            last_name = 'Testsurname',
            password = 'Testing321..',
        )

        ## retrieve profile
        self.profil = Profile.objects.get(user=self.user)
        self.profil.title = 'Mr.'
        self.profil.company = 'Test Company'
        self.profil.position = 'Test Position'
        self.profil.save()


    def test_profiles_listed(self):
        """Test if profiles are listed in the users page"""
        url = reverse('admin:core_profile_changelist')
        resp = self.client.get(url)

        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, self.profil.user.email)
        self.assertContains(resp, self.profil.full_name)
        self.assertContains(resp, self.profil.title)
        self.assertContains(resp, self.profil.company)
        self.assertContains(resp, self.profil.position)


    def test_profile_change_page(self):
        """Test if profile edit / change page workds correctly """
        url = reverse('admin:core_profile_change', args=[self.profil.id])
        resp = self.client.get(url)

        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, self.profil.user.email)
        self.assertContains(resp, self.profil.title)
        self.assertContains(resp, self.profil.company)
        self.assertContains(resp, self.profil.position)


    def test_create_profile_page(self):
        """Test the add profile page on admin """
        url = reverse('admin:core_profile_add')
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, 'Title')
        self.assertContains(resp, 'User:')
        self.assertContains(resp, 'Company')
        self.assertContains(resp, 'Position')
        self.assertContains(resp, 'Location')
        self.assertContains(resp, 'Country')
        self.assertContains(resp, 'Is company admin')

    def test_profile_history_page(self):
        """Test the profile history page on admin """
        url = reverse('admin:core_profile_history', args=[self.profil.id])
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, self.profil.user.email)



class AdminSiteBasicUserProfileTests(TestCase):
    """Test if non admin users can log in to user admin"""
    def setUp(self):
        """test client, auser created"""
        self.client = Client()
        self.user = get_user_model().objects.create_user(
            email = 'test@domain.com',
            first_name= 'UserFirstName',
            last_name = 'Testsurname',
            password = 'Testing321..',
        )
        self.client.force_login(self.user)

        
    def test_if_users_listed(self):
        """Test if users are listed in the users page if standard user tries admin"""
        url = reverse('admin:core_user_changelist')
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 302)
        self.assertNotEqual(resp.status_code, 200)

