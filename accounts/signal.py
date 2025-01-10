from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from .models import StudentProfile, TeacherProfile, AdminProfile

User = get_user_model()

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if not created:
        return

    if instance.user_type == 'student' and not hasattr(instance, 'studentprofile'):
        StudentProfile.objects.create(user=instance)
    elif instance.user_type == 'teacher' and not hasattr(instance, 'teacherprofile'):
        TeacherProfile.objects.create(user=instance)
    elif instance.user_type == 'admin' and not hasattr(instance, 'adminprofile'):
        AdminProfile.objects.create(user=instance)
