from django.shortcuts import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model

User = get_user_model()


class UserAPIViewTest(APITestCase):
    def setUp(self) -> None:
        self.user = User.objects.create_user(
            email="test@gmail.com", password="12345678test", username="test_user"
        )
        self.url = reverse("me")
        self.client.force_authenticate(user=self.user)

    def test_get_user_data(self):
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["username"], "test_user")

    def test_update_user_data(self):
        data = {"username": "new_name"}
        response = self.client.put(self.url, data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self.user.username, "new_name")


class AuthorAPIViewTest(APITestCase):
    def setUp(self) -> None:
        self.user = User.objects.create_user(
            email="test@gmail.com", password="12345678test", username="test_user"
        )
        self.user.social_links.create(link="https://test_link/")
        User.objects.create_user(
            email="test1@gmail.com", password="12345678test", username="test_user_1"
        )
        self.client.force_authenticate(user=self.user)

    def test_get_list_authors(self):
        url = reverse("authors_list")
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data[0]["username"], "test_user")
        self.assertEqual(response.data[1]["username"], "test_user_1")
        self.assertEqual(len(response.data), 2)

    def test_get_author_record(self):
        url = reverse("author_record", kwargs=({"pk": 1}))
        response = self.client.get(url)
        result = response.json()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        for key, value in result.items():
            if key == "social_links":
                self.assertEqual(
                    result["social_links"], [{"id": 1, "link": "https://test_link/"}]
                )
                continue
            self.assertEqual(getattr(self.user, key), value)


class SocialLinkAPIViewTest(APITestCase):
    def setUp(self) -> None:
        self.user = User.objects.create_user(
            email="test@gmail.com", password="12345678test"
        )
        self.social_link = self.user.social_links.create(link="http://test_link/")
        self.client.force_authenticate(user=self.user)

    def test_create_social_link(self):
        url = reverse("social_link-list")
        link = "https://www.example.com"
        data = {"link": link}
        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["link"], link)
        self.assertEqual(self.user.social_links.last().link, link)

    def test_get_social_links_list(self):
        url = reverse("social_link-list")
        self.user.social_links.create(link="https://www.example.com")
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_get_single_social_link(self):
        url = reverse("social_link-detail", kwargs={"pk": 1})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["link"], self.social_link.link)

    def test_update_social_link(self):
        url = reverse("social_link-detail", kwargs={"pk": 1})
        new_link = "http://www.updated.com/"
        data = {"link": new_link}
        response = self.client.put(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["link"], new_link)
        self.assertEqual(self.user.social_links.last().link, new_link)

    def test_delete_social_link(self):
        url = reverse("social_link-detail", kwargs={"pk": 1})
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(self.user.social_links.count(), 0)
