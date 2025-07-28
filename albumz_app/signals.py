from django.contrib.auth.models import User as AuthUser
from django.db.models.signals import post_save
from django.dispatch import receiver

from .domain.models import User as DomainUser


@receiver(post_save, sender=AuthUser)
def create_domain_user(sender, instance, created, **kwargs):
    if created:
        DomainUser.objects.create(auth_user=instance)
