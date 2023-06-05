from django.shortcuts import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from unittest import mock
import jwt
from users.tokens import account_token_generator

User = get_user_model()


class UserSignUpAPIViewTest(APITestCase):
    def setUp(self) -> None:
        self.url = reverse("sign_up")

    def test_sign_up_success(self):
        data = {"email": "test@gmail.com", "password": "12345678test"}
        response = self.client.post(self.url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["send_email"], True)
        self.assertEqual(User.objects.all().count(), 1)

    def test_sign_up_failure(self):
        invalid_data = [
            {"email": "", "password": "12345678test"},
            {"email": "test@gmail.com", "password": ""},
            {"email": "test", "password": "12345678test"},
            {"email": "test@gmail.com", "password": "1234"},
        ]

        for data in invalid_data:
            response = self.client.post(self.url, data, format="json")

            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
            self.assertEqual(User.objects.all().count(), 0)

    @mock.patch("users.utils.EmailSender.send_activation_email")
    def test_sign_up_send_activation_email_failure(self, mock_send_activation_email):
        mock_send_activation_email.return_value = False
        data = {"email": "test@gmail.com", "password": "12345678test"}
        response = self.client.post(self.url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(response.data["send_email"])
        self.assertEqual(User.objects.all().count(), 1)


class ActivateAccountAPIViewTest(APITestCase):
    def setUp(self) -> None:
        self.user = User.objects.create_user(
            email="test@gmail.com", password="12345678test"
        )
        self.uidb64 = urlsafe_base64_encode(force_bytes(self.user.pk))
        self.token = account_token_generator.make_token(self.user)

    def test_account_activation_success(self):
        url = reverse("activate", args=[self.uidb64, self.token])
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["success"])
        self.assertTrue(User.objects.get(pk=self.user.pk).is_active)

    def test_account_activation_failure_invalid_token(self):
        invalid_token = self.token + "some_data"
        url = reverse("activate", args=[self.uidb64, invalid_token])
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(response.data["success"])
        self.assertFalse(User.objects.get(pk=self.user.pk).is_active)

    def test_account_activation_failure_invalid_uidb64(self):
        invalid_uidb64 = self.uidb64 + "some_data"
        url = reverse("activate", args=[invalid_uidb64, self.token])
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(response.data["success"])
        self.assertFalse(self.user.is_active)


class UserSignInAPIViewTest(APITestCase):
    def setUp(self) -> None:
        self.email = "test@gmail.com"
        self.password = "12345678test"
        self.user = User.objects.create_user(email=self.email, password=self.password)
        self.url = reverse("sign_in")

    def test_sign_in_success(self):
        data = {"email": self.email, "password": self.password}
        response = self.client.post(self.url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["user_email"], self.email)

    def test_sign_in_failure_email(self):
        wrong_email = "wrong@gmail.com"
        error_message = "User with such email doesn't exist"
        data = {"email": wrong_email, "password": self.password}
        response = self.client.post(self.url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data["detail"], error_message)

    def test_sign_in_failure_password(self):
        wrong_password = "12345678wrong"
        error_message = "You passed a wrong password"
        data = {"email": self.email, "password": wrong_password}
        response = self.client.post(self.url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data["detail"], error_message)


class RefreshAccessTokenAPIViewTest(APITestCase):
    def setUp(self) -> None:
        self.user = User.objects.create_user(
            email="test@gmail.com", password="12345678test", is_active=True
        )
        self.refresh_token = "refresh_token"
        self.url = reverse("sign_in_refresh")

    @mock.patch("jwt.decode")
    def test_sign_in_refresh_success(self, mock_jwt_decode):
        payload = {"user_id": self.user.pk}
        mock_jwt_decode.return_value = payload
        data = {"refresh_token": self.refresh_token}
        response = self.client.post(self.url, data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["access_token"])

    @mock.patch("jwt.decode", side_effect=jwt.ExpiredSignatureError)
    def test_sign_in_refresh_failure_expired_token(self, mock_jwt_decode):
        data = {"refresh_token": self.refresh_token}
        response = self.client.post(self.url, data)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(
            response.data["detail"], "Expired refresh token, please login again"
        )

    @mock.patch("jwt.decode")
    def test_sign_in_refresh_failure_inactive_user(self, mock_jwt_decode):
        self.user.is_active = False
        self.user.save()

        payload = {"user_id": self.user.pk}
        mock_jwt_decode.return_value = payload
        data = {"refresh_token": self.refresh_token}
        response = self.client.post(self.url, data)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data["detail"], "User is inactive")

    @mock.patch("jwt.decode")
    def test_sign_in_refresh_failure_non_existent_user(self, mock_jwt_decode):
        payload = {"user_id": 2}
        mock_jwt_decode.return_value = payload
        data = {"refresh_token": self.refresh_token}
        response = self.client.post(self.url, data)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data["detail"], "User not found")


class ChangePasswordAPIViewTest(APITestCase):
    def setUp(self) -> None:
        self.password = "12345678test"
        self.new_password = "123456789test"
        self.user = User.objects.create_user(
            email="test@gmail.com", password=self.password, is_active=True
        )
        self.client.force_authenticate(user=self.user)
        self.url = reverse("change_password")

    def test_change_password_success(self):
        data = {
            "old_password": self.password,
            "new_password": self.new_password,
            "new_password_2": self.new_password,
        }
        response = self.client.put(self.url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["success"])

    def test_change_password_failure_wrong_old_password(self):
        wrong_password = "12345678wrong"
        data = {
            "old_password": wrong_password,
            "new_password": self.new_password,
            "new_password_2": self.new_password,
        }
        response = self.client.put(self.url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["old_password"], ["Old password isn't correct"])

    def test_change_password_failure_different_new_passwords(self):
        wrong_password = "12345678wrong"
        data = {
            "old_password": self.password,
            "new_password": self.new_password,
            "new_password_2": wrong_password,
        }
        response = self.client.put(self.url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["password"], ["Password fields didn't match"])


class ResetPasswordApiViewTest(APITestCase):
    def setUp(self) -> None:
        self.email = "test@gmail.com"
        self.user = User.objects.create_user(email=self.email, password="12345678test")
        self.uidb64 = urlsafe_base64_encode(force_bytes(self.user.pk))
        self.token = account_token_generator.make_token(self.user)
        self.request_url = reverse("reset_password_request")
        self.confirm_url = reverse(
            "reset_password_confirm", args=[self.uidb64, self.token]
        )

    @mock.patch("users.utils.EmailSender.send_reset_password_email")
    def test_reset_password_request_success(self, mock_send_reset_password_email):
        mock_send_reset_password_email.return_value = True
        data = {"email": self.email}
        response = self.client.post(self.request_url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data.get("email"), data)
        self.assertTrue(response.data["send_email"])

    @mock.patch("users.utils.EmailSender.send_reset_password_email")
    def test_reset_password_request_failure_send_email(
        self, mock_send_reset_password_email
    ):
        mock_send_reset_password_email.return_value = False
        data = {"email": self.email}
        response = self.client.post(self.request_url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data.get("email"), data)
        self.assertFalse(response.data["send_email"])

    def test_password_reset_request_failure_wrong_email(self):
        wrong_email = "test1@gmail.com"
        data = {"email": wrong_email}
        response = self.client.post(self.request_url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data["non_field_errors"], ["User with such email doesn't exist"]
        )

    def test_password_confirm_success(self):
        data = {"new_password": "123456789test"}
        response = self.client.patch(self.confirm_url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["success"])

    @mock.patch("users.models.User.objects.get")
    def test_password_confirm_failure_non_existent_user(self, mock_user_get):
        mock_user = User(email="wrong@gmail.com", pk=2)
        mock_user_get.return_value = mock_user
        data = {"new_password": "123456789test"}
        response = self.client.patch(self.confirm_url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(response.data["success"])

    @mock.patch("users.tokens.account_token_generator.check_token")
    def test_password_confirm_failure_bad_token(self, mock_check_token):
        mock_check_token.return_value = False
        data = {"new_password": "123456789test"}
        response = self.client.patch(self.confirm_url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(response.data["success"])


class SpotifyAuthAPIViewTest(APITestCase):
    def setUp(self) -> None:
        self.user = User.objects.create_user(
            email="test@gmail.com", password="12345678test"
        )
        self.url = reverse("spotify_callback")

    @mock.patch("users.services.spotify.spotify_auth")
    def test_spotify_auth_success(self, mock_spotify_auth):
        mock_spotify_auth.return_value = self.user
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["user_id"], self.user.pk)

    @mock.patch("users.services.spotify.spotify_auth")
    def test_spotify_auth_failure(self, mock_spotify_auth):
        mock_spotify_auth.return_value = None
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data["error"], "Something went wrong. Please try again"
        )
