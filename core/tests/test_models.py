from django.test import TestCase
from django.contrib.auth import get_user_model
from django.conf import settings
from django.core.exceptions import ValidationError
from core.models import Profile


from django.db.utils import IntegrityError

User = get_user_model()

def create_user(arg, params):

    if arg == 'staff':
        return User.objects.create_staffuser(**params)
    elif arg == 'standard':
        return User.objects.create_user(**params)
    elif arg == 'demo':
        return User.objects.create_demo_user(**params)
    elif arg == 'super':
        return User.objects.create_superuser(**params)
    else:
        return None


class ModelTests(TestCase):

    def setUp(self):
        self.params = dict(
                            email = 'test@domain.com',
                            first_name= 'UserFirstName',
                            last_name = 'TESTUSERSURNAME', #UPPER IN MODEL
                            password = 'Testing321..',
                        )

    
    def test_if_second_profile_cannot_be_created(self):
        """Test if second profile with same user instance can be created"""
        user = create_user('standard', self.params)
        #Check if profile created
        profil = Profile.objects.last()
        self.assertEqual(
            user,
            profil.user
        )      
        with self.assertRaises(IntegrityError):
            profil_2 = Profile.objects.create(user=user)
            profil_2.save()


    def test_unique_email(self):
        """Test if existing email still registers"""
        user = create_user('standard', self.params)

        with self.assertRaises(IntegrityError):
            nparams = dict(email=self.params['email'], password='ADifferentTesting321..', 
                first_name='somename', last_name='somesirname')
            create_user('standard', nparams)


    ## USER MANAGER CREATION METHODS VALIDATION IF CREATED WITH THE SAME DATA 
    def test_demo_user_creation_with_same_data(self):
        """Tests a DEMO user created with the same email, password, 
            first_name, last_name and if no admin, staff, superuser privillages
        
        """
        user = create_user('demo', self.params)

        self.assertEqual(self.params['email'], user.email)
        self.assertEqual(self.params['first_name'], user.first_name)
        self.assertEqual(self.params['last_name'], user.last_name)
        self.assertTrue(user.check_password(self.params['password']))

        self.assertFalse(user.is_admin)
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)
        self.assertTrue(user.is_active)
        self.assertTrue(user.is_demo_user)
        #Check if profile created
        profil = Profile.objects.last()
        self.assertEqual(
            user,
            profil.user
        )

    def test_standard_user_creation_with_correct_data(self):
        """Tests a STANDARD user created with the same email, password, 
            first_name, last_name and if no admin, staff, superuser privillages
        
        """
        user = create_user('standard', self.params)

        self.assertEqual(self.params['email'], user.email)
        self.assertEqual(self.params['first_name'], user.first_name)
        self.assertEqual(self.params['last_name'], user.last_name)
        self.assertTrue(user.check_password(self.params['password']))

        self.assertFalse(user.is_admin)
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)
        self.assertTrue(user.is_active)
        self.assertFalse(user.is_demo_user)
        #Check if profile created
        profil = Profile.objects.last()
        self.assertEqual(
            user,
            profil.user
        )


    def test_staff_user_creation_with_correct_data(self):
        """Tests a STAFF user created with the same email, password, 
            first_name, last_name and if no admin, staff, superuser privillages
        
        """
        user = create_user('staff', self.params)

        self.assertEqual(self.params['email'], user.email)
        self.assertEqual(self.params['first_name'], user.first_name)
        self.assertEqual(self.params['last_name'], user.last_name)
        self.assertTrue(user.check_password(self.params['password']))

        self.assertFalse(user.is_admin)
        self.assertTrue(user.is_staff)
        self.assertFalse(user.is_superuser)
        self.assertTrue(user.is_active)
        self.assertFalse(user.is_demo_user)
        #Check if profile created
        profil = Profile.objects.last()
        self.assertEqual(
            user,
            profil.user
        )


    def test_super_user_creation_with_correct_data(self):
        """Tests a super user created with the same email, password, 
            first_name, last_name and if no admin, staff, superuser privillages
        
        """
        user = create_user('super', self.params)

        self.assertEqual(self.params['email'], user.email)
        self.assertEqual(self.params['first_name'], user.first_name)
        self.assertEqual(self.params['last_name'], user.last_name)
        self.assertTrue(user.check_password(self.params['password']))

        self.assertTrue(user.is_admin)
        self.assertTrue(user.is_staff)
        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_active)
        self.assertFalse(user.is_demo_user)
        #Check if profile created
        profil = Profile.objects.last()
        self.assertEqual(
            user,
            profil.user
        )


    def test_normalized_email(self):
        """Test if email is normalized"""
        nparams = dict(
            email='test@TESTDOMAIN.COM', password='Testing321..', 
            first_name='test', last_name='User'
        )
        user = create_user('standard', nparams)
        self.assertEqual(user.email, nparams['email'].lower())
        #Check if profile created
        profil = Profile.objects.last()
        self.assertEqual(
            user,
            profil.user
        )


    def test_email_domains_with_blacklist_domains(self):
        """Test IF blacklisted email domain creates user"""
        blacklisted_emails = [f'test@{i}' for i in settings.EMAIL_DOMAIN_BLACKLIST]
            
        for email in blacklisted_emails:
            with self.assertRaises(ValidationError):
                self.params['email'] = email
                user = create_user('standard', self.params)
                

    def test_invalid_email(self):
        """Test if blank email doesnt work at registration"""
        for a in ['standard', 'staff', 'demo', 'super']:
            with self.assertRaises(ValueError):
                params = dict(email=None, password='Testing321..', 
                    first_name='first_name', last_name='last_name')
                create_user(a, params)

  