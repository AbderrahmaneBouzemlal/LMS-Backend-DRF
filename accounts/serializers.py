from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import StudentProfile, TeacherProfile, AdminProfile

User = get_user_model()


class StudentProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentProfile
        fields = ('student_id', 'grade_level', 'parent_name', 'parent_phone',
                  'parent_email', 'date_of_birth', 'address', 'avatar',
                  'enrollment_date')
        read_only_fields = ('enrollment_date',)


class TeacherProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = TeacherProfile
        fields = ('teacher_id', 'subjects', 'qualifications', 'employment_date',
                  'department', 'date_of_birth', 'address', 'avatar')


class AdminProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = AdminProfile
        fields = ('admin_id', 'department', 'role', 'employment_date',
                  'date_of_birth', 'address', 'avatar')


class UserSerializer(serializers.ModelSerializer):
    student_profile = StudentProfileSerializer(read_only=True)
    teacher_profile = TeacherProfileSerializer(read_only=True)
    admin_profile = AdminProfileSerializer(read_only=True)

    class Meta:
        model = User
        fields = ('id', 'email', 'user_type', 'phone', 'first_name', 'last_name',
                  'date_joined', 'student_profile', 'teacher_profile', 'admin_profile')
        read_only_fields = ('date_joined',)


class UserRegistrationSerializer(serializers.ModelSerializer):
    student_profile = StudentProfileSerializer(required=False)
    teacher_profile = TeacherProfileSerializer(required=False)
    admin_profile = AdminProfileSerializer(required=False)
    password = serializers.CharField(write_only=True)
    confirm_password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ('email', 'password', 'confirm_password', 'user_type',
                  'first_name', 'last_name', 'phone', 'student_profile',
                  'teacher_profile', 'admin_profile')

    def validate(self, data):
        if data['password'] != data.pop('confirm_password'):
            raise serializers.ValidationError("Passwords do not match")

        user_type = data.get('user_type')
        profile_data = None

        if user_type == 'student':
            profile_data = data.get('student_profile')
        elif user_type == 'teacher':
            profile_data = data.get('teacher_profile')
        elif user_type == 'admin':
            profile_data = data.get('admin_profile')

        if not profile_data:
            raise serializers.ValidationError(f"Profile data required for {user_type}")

        return data

    def create(self, validated_data):
        user_type = validated_data.get('user_type')

        # Remove all profile data from validated_data
        student_profile_data = validated_data.pop('student_profile', None)
        teacher_profile_data = validated_data.pop('teacher_profile', None)
        admin_profile_data = validated_data.pop('admin_profile', None)

        # Get the password and remove it from validated_data
        password = validated_data.pop('password')

        # Create the user
        user = User(**validated_data)
        user.set_password(password)
        user.save()

        # Create the appropriate profile based on user_type
        if user_type == 'student' and student_profile_data:
            StudentProfile.objects.create(user=user, **student_profile_data)
        elif user_type == 'teacher' and teacher_profile_data:
            TeacherProfile.objects.create(user=user, **teacher_profile_data)
        elif user_type == 'admin' and admin_profile_data:
            AdminProfile.objects.create(user=user, **admin_profile_data)

        return user