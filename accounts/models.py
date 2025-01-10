from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _
from .managers import CustomUserManager


class User(AbstractUser):
    username = None
    email = models.EmailField(_('email address'), unique=True)
    USER_TYPES = (
        ('student', 'Student'),
        ('teacher', 'Teacher'),
        ('admin', 'Administrator')
    )
    user_type = models.CharField(max_length=20, choices=USER_TYPES)
    phone = models.CharField(max_length=15, blank=True)

    groups = models.ManyToManyField(
        'auth.Group',
        related_name='User_set',
        blank=True
    )

    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='User_permissions_set',
        blank=True
    )


    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['user_type']

    objects = CustomUserManager()

    def __str__(self):
        return self.email


class BaseProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='%(class)s')
    date_of_birth = models.DateField(null=True, blank=True)
    address = models.TextField(blank=True)
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)

    class Meta:
        abstract = True


class StudentProfile(BaseProfile):
    student_id = models.CharField(max_length=20, unique=True)
    grade_level = models.CharField(max_length=20)
    enrollment_date = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"Student Profile: {self.user.email}"


class TeacherProfile(BaseProfile):
    teacher_id = models.CharField(max_length=20, unique=True)
    subjects = models.JSONField(default=list)
    qualifications = models.TextField()
    employment_date = models.DateField()
    department = models.CharField(max_length=100)

    def __str__(self):
        return f"Teacher Profile: {self.user.email}"


class AdminProfile(BaseProfile):
    admin_id = models.CharField(max_length=20, unique=True)
    department = models.CharField(max_length=100)
    role = models.CharField(max_length=100)
    employment_date = models.DateField()

    def __str__(self):
        return f"Admin Profile: {self.user.email}"
