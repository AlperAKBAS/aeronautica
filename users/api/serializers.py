from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.conf import settings
from core.models import Profile
from rest_auth.serializers import LoginSerializer as RestAuthLoginSerializer


class LoginSerializer(RestAuthLoginSerializer):
    """Removes Username form json body for restauth"""
    username = None


class ProfileSerializer(serializers.ModelSerializer):
    """Standard users cannot change is_company_admin"""
    id = serializers.IntegerField(read_only=True)
    user = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Profile
        exclude = ['is_company_admin']


class ProfileSerializerForAdmin(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)
    user = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Profile
        fields = '__all__'



class RegisterNewUserSerializer(serializers.ModelSerializer):
    """Serializer for registering a new user and updated the profile
        Also updates user.profile which is created with signals
    """
    id = serializers.IntegerField(read_only=True)

    title = serializers.CharField(write_only=True)
    company = serializers.CharField(write_only=True)
    position = serializers.CharField(required=True, write_only=True)
    country = serializers.CharField(write_only=True)
    city = serializers.CharField(write_only=True)
  

    verify_password = serializers.CharField(
        required=True, write_only=True, 
        min_length=6, style={'input_type': 'password'})
   
    verify_email = serializers.EmailField(required=True, write_only=True)

    class Meta:
        model = get_user_model()
        fields = ('id', 'email', 'verify_email', 'first_name', 'last_name', 
                'password','verify_password', 
                'title', 'company', 'position',
                'country', 'city' )

        extra_kwargs = {
            'password': {
                'write_only': True,
                'min_length': 6,
                'style': {'input_type': 'password'}
            },
        }

    def create(self, validated_data):
        """Create a new user object with encrypted password and return it"""
        user = get_user_model().objects.create_user(
            email=validated_data.get('email'),
            first_name=validated_data.get('first_name'),
            last_name=validated_data.get('last_name')
        )
        user.set_password(validated_data.get('password'))
        user.save()
        profile = Profile.objects.get(user=user)
        profile.title = validated_data.get('title')
        profile.company = validated_data.get('company')
        profile.position = validated_data.get('position')
        profile.country = validated_data.get('country')
        profile.city = validated_data.get('city')
        profile.save()
        profile = ProfileSerializer(read_only=True)
        return user


    def validate(self, data):
        if data['email'] != data['verify_email']:
            raise serializers.ValidationError('Emails not matching. ')
        if data['password'] != data['verify_password']:
            raise serializers.ValidationError('Passwords not matching. ')
        return data


    def validate_email(self, email_value):
        email_domain = email_value.split('@')[-1]
        if  email_domain in settings.EMAIL_DOMAIN_BLACKLIST:
            raise serializers.ValidationError(f'This domain ({email_domain}) is not supported. Please provide a corporate email address.')
        return email_value



class UserDisplaySerializer(serializers.ModelSerializer):

    profile = ProfileSerializer(many=False, read_only=True)

    class Meta:
        model = get_user_model()
        # fields = ('email', 'first_name', 'last_name')
        exclude = ('password', )