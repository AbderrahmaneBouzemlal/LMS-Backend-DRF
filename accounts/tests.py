# accounts/tests/test_user_registration.py
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
from accounts.models import StudentProfile, TeacherProfile, AdminProfile

User = get_user_model()


class UserRegistrationTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.register_url = reverse('user-list')

    def test_should_not_register_user_without_email(self):
        """
        Given a registration request without an email
        When the registration endpoint is called
        Then it should return a 400 status code with appropriate error message
        """
        data = {
            "password": "test123!@#",
            "confirm_password": "test123!@#",
            "user_type": "student"
        }

        response = self.client.post(self.register_url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('email', response.data)

    def test_should_not_register_user_with_invalid_email(self):
        """
        Given a registration request with invalid email format
        When the registration endpoint is called
        Then it should return a 400 status code with appropriate error message
        """
        data = {
            "email": "invalid-email",
            "password": "test123!@#",
            "confirm_password": "test123!@#",
            "user_type": "student"
        }

        response = self.client.post(self.register_url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('email', response.data)

    def test_should_not_register_user_with_mismatched_passwords(self):
        """
        Given a registration request with mismatched passwords
        When the registration endpoint is called
        Then it should return a 400 status code with appropriate error message
        """
        data = {
            "email": "test@test.com",
            "password": "test123!@#",
            "confirm_password": "different123!@#",
            "user_type": "student"
        }

        response = self.client.post(self.register_url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('non_field_errors', response.data)

    def test_should_not_register_user_with_invalid_user_type(self):
        """
        Given a registration request with invalid user type
        When the registration endpoint is called
        Then it should return a 400 status code with appropriate error message
        """
        data = {
            "email": "test@test.com",
            "password": "test123!@#",
            "confirm_password": "test123!@#",
            "user_type": "invalid_type"
        }

        response = self.client.post(self.register_url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('user_type', response.data)


# accounts/tests/test_student_registration.py
class StudentRegistrationTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.register_url = reverse('user-list')
        self.valid_student_data = {
            "email": "student@test.com",
            "password": "test123!@#",
            "confirm_password": "test123!@#",
            "user_type": "student",
            "student_profile": {
                "student_id": "STU001",
                "grade_level": "10",
                "parent_name": "Parent Name",
                "parent_phone": "1234567890",
                "parent_email": "parent@test.com"
            }
        }

    def test_should_register_valid_student(self):
        """
        Given valid student registration data
        When the registration endpoint is called
        Then it should create a new student user with profile
        """
        response = self.client.post(
            self.register_url,
            self.valid_student_data,
            format='json'
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(User.objects.filter(email=self.valid_student_data['email']).exists())
        self.assertTrue(StudentProfile.objects.filter(
            student_id=self.valid_student_data['student_profile']['student_id']
        ).exists())

    def test_should_not_register_student_with_duplicate_student_id(self):
        """
        Given a student registration with an existing student_id
        When the registration endpoint is called
        Then it should return a 400 status code with appropriate error message
        """
        # First create a student
        self.client.post(self.register_url, self.valid_student_data, format='json')

        # Try to create another student with same student_id
        duplicate_data = self.valid_student_data.copy()
        duplicate_data['email'] = "another@test.com"

        response = self.client.post(self.register_url, duplicate_data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('student_profile', response.data)


# accounts/tests/test_authentication.py
class AuthenticationTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.login_url = reverse('token_obtain_pair')
        self.user_data = {
            "email": "test@test.com",
            "password": "test123!@#"
        }
        self.user = User.objects.create_user(
            email=self.user_data['email'],
            password=self.user_data['password'],
            user_type='student'
        )

    def test_should_obtain_token_pair_with_valid_credentials(self):
        """
        Given valid login credentials
        When the token endpoint is called
        Then it should return access and refresh tokens
        """
        response = self.client.post(self.login_url, self.user_data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)

    def test_should_not_obtain_token_with_invalid_credentials(self):
        """
        Given invalid login credentials
        When the token endpoint is called
        Then it should return a 401 status code
        """
        invalid_data = self.user_data.copy()
        invalid_data['password'] = 'wrongpassword'

        response = self.client.post(self.login_url, invalid_data, format='json')

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


# accounts/tests/test_profile_operations.py
class ProfileOperationsTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.me_url = reverse('me')
        self.user = User.objects.create_user(
            email="test@test.com",
            password="test123!@#",
            user_type="student"
        )
        StudentProfile.objects.create(
            user=self.user,
            student_id="STU001",
            grade_level="10"
        )
        self.client.force_authenticate(user=self.user)

    def test_should_retrieve_own_profile(self):
        """
        Given an authenticated user
        When the profile endpoint is called
        Then it should return the user's profile data
        """
        response = self.client.get(self.me_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['email'], self.user.email)
        self.assertEqual(
            response.data['student_profile']['student_id'],
            "STU001"
        )

    def test_should_update_profile_with_valid_data(self):
        """
        Given valid profile update data
        When the profile update endpoint is called
        Then it should update the user's profile
        """
        update_data = {
            "student_profile": {
                "grade_level": "11"
            }
        }

        response = self.client.patch(self.me_url, update_data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.data['student_profile']['grade_level'],
            "11"
        )
