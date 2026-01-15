from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings

from .models import StudentProfile, TeacherProfile, AdminProfile


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_user_profile(sender, instance, created, **kwargs):
    if not created:
        return

    if instance.role == instance.STUDENT:
        StudentProfile.objects.create(user=instance)

    elif instance.role == instance.TEACHER:
        TeacherProfile.objects.create(user=instance)

    elif instance.role == instance.ADMIN:
        AdminProfile.objects.create(user=instance)
