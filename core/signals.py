from django.contrib.auth import get_user_model
from core.models import Profile
from django.db.models.signals import post_save
from django.dispatch import receiver

User = get_user_model()


@receiver(post_save, sender=User)
def create_profil(sender, instance, created, **kwargs):
   
    if created:
        Profile.objects.create(user=instance)