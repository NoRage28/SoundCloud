from django.shortcuts import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model
from audio_library.models import Genre

User = get_user_model()


class GenreAPIViewTest(APITestCase):
    def setUp(self) -> None:
        Genre.objects.create(name="Rock")
        Genre.objects.create(name="Pop")
        Genre.objects.create(name="Metal")
        self.url = reverse("genre")

    def test_get_genres_list(self):
        response = self.client.get(self.url)
        expected_data = [
            {"id": 1, "name": "Rock"},
            {"id": 2, "name": "Pop"},
            {"id": 3, "name": "Metal"},
        ]

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 3)
        self.assertEqual(response.data, expected_data)


class LicenseAPIViewTest(APITestCase):
    def setUp(self) -> None:
        self.user = User.objects.create_user(
            email="test@gmail.com", password="12345678test"
        )
        self.license = self.user.licenses.create(text="license")
        self.client.force_authenticate(user=self.user)

    def test_get_single_license(self):
        url = reverse("license-detail", kwargs={"pk": 1})
        expected_data = {"id": 1, "text": "license"}
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, expected_data)

    def test_get_licenses_list(self):
        url = reverse("license-list")
        self.user.licenses.create(text="another_license")
        expected_data = [
            {"id": 1, "text": "license"},
            {"id": 2, "text": "another_license"},
        ]
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, expected_data)
        self.assertEqual(len(response.data), 2)

    def test_create_license(self):
        url = reverse("license-list")
        data = {"text": "new_license"}
        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["text"], "new_license")
        self.assertEqual(self.user.licenses.last().text, "new_license")

    def test_update_license(self):
        url = reverse("license-detail", kwargs={"pk": 1})
        data = {"text": "update_license"}
        response = self.client.put(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["text"], "update_license")
        self.assertEqual(self.user.licenses.last().text, "update_license")

    def test_delete_license(self):
        url = reverse("license-detail", kwargs={"pk": 1})
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(self.user.licenses.count(), 0)
