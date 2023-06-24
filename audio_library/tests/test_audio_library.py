from django.core.files import File

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


class StreamingTrackAPIViewTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="test@gmail.com", password="12345678test"
        )
        self.license = self.user.licenses.create(text="text")
        self.track = self.user.tracks.create(title="title", license=self.license)
        with open("audio_library/tests/test_track.mp3", "rb") as file_data:
            self.track.file.save("test_track.mp3", File(file_data))
        self.track.save()

    def tearDown(self) -> None:
        self.track.file.delete()

    def test_get_valid_track_audition(self):
        url = reverse("stream_track", kwargs={"pk": self.track.pk})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.track.refresh_from_db()
        self.assertEqual(self.track.auditions, 1)

    def test_get_invalid_track_audition(self):
        url = reverse("stream_track", kwargs={"pk": 9999})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data, {"track": "Such track doesn't exist"})

    def test_get_track_audition_without_file(self):
        self.track.file.delete()
        url = reverse("stream_track", kwargs={"pk": self.track.pk})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(
            response.data, {"track": "File with this track doesn't exist or removed"}
        )


class DownloadTrackAPIViewTest(APITestCase):
    def setUp(self) -> None:
        self.user = User.objects.create_user(
            email="test@gmail.com", password="12345678test"
        )
        self.license = self.user.licenses.create(text="text")
        self.track = self.user.tracks.create(title="title", license=self.license)
        with open("audio_library/tests/test_track.mp3", "rb") as file_data:
            self.track.file.save("test_track.mp3", File(file_data))
        self.track.save()

    def tearDown(self) -> None:
        self.track.file.delete()

    def test_get_valid_track_download(self):
        url = reverse("download_track", kwargs={"pk": self.track.pk})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.track.refresh_from_db()
        self.assertEqual(self.track.downloads, 1)

    def test_get_invalid_track_download(self):
        url = reverse("download_track", kwargs={"pk": 9999})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data, {"track": "Such track doesn't exist"})

    def test_get_track_download_without_file(self):
        self.track.file.delete()
        url = reverse("download_track", kwargs={"pk": self.track.pk})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(
            response.data, {"track": "File with this track doesn't exist or removed"}
        )


class PublicAlbumAPIViewTest(APITestCase):
    def setUp(self) -> None:
        self.user = User.objects.create_user(
            email="test@gmail.com", password="12345678test"
        )
        self.first_album = self.user.albums.create(
            name="First Album", description="Description", private=False
        )
        self.second_album = self.user.albums.create(
            name="Second Album", description="Description", private=True
        )

    def test_get_user_albums(self):
        url = reverse("author_albums", kwargs={"pk": self.user.pk})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["name"], "First Album")


class TrackListAPIViewTest(APITestCase):
    def setUp(self) -> None:
        self.user = User.objects.create_user(
            email="test@gmail.com", password="12345678test"
        )
        self.license = self.user.licenses.create(text="text")

        self.track = self.user.tracks.create(title="title", license=self.license)
        with open("audio_library/tests/test_track.mp3", "rb") as file_data:
            self.track.file.save("test_track.mp3", File(file_data))
        self.track.save()

        self.track_1 = self.user.tracks.create(
            title="title_1", license=self.license, private=True
        )
        with open("audio_library/tests/test_track.mp3", "rb") as file_data:
            self.track_1.file.save("test_track_1.mp3", File(file_data))
        self.track_1.save()

    def tearDown(self) -> None:
        self.track.file.delete()
        self.track_1.file.delete()

    def test_get_track_list(self):
        url = reverse("track_list")
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(response.data["results"][0]["title"], "title")


class AuthorTrackListAPIViewTest(APITestCase):
    def setUp(self) -> None:
        self.user = User.objects.create_user(
            email="test@gmail.com", password="12345678test"
        )
        self.license = self.user.licenses.create(text="text")

        self.track = self.user.tracks.create(title="title", license=self.license)
        with open("audio_library/tests/test_track.mp3", "rb") as file_data:
            self.track.file.save("test_track.mp3", File(file_data))
        self.track.save()

        self.track_1 = self.user.tracks.create(
            title="title_1", license=self.license, private=True
        )
        with open("audio_library/tests/test_track.mp3", "rb") as file_data:
            self.track_1.file.save("test_track_1.mp3", File(file_data))
        self.track_1.save()

    def tearDown(self) -> None:
        self.track.file.delete()
        self.track_1.file.delete()

    def test_get_track_list(self):
        url = reverse("author_track_list", kwargs={"pk": self.user.pk})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(response.data["results"][0]["title"], "title")


class CommentAPIViewTest(APITestCase):
    def setUp(self) -> None:
        self.user = User.objects.create_user(
            email="test@gmail.com", password="12345678test"
        )
        self.license = self.user.licenses.create(text="text")

        self.track = self.user.tracks.create(title="title", license=self.license)
        with open("audio_library/tests/test_track.mp3", "rb") as file_data:
            self.track.file.save("test_track.mp3", File(file_data))
        self.track.save()
        self.good_comment = self.user.comments.create(
            track=self.track, text="good_comment"
        )
        self.bad_comment = self.user.comments.create(
            track=self.track, text="bad_comment"
        )

    def tearDown(self) -> None:
        self.track.file.delete()

    def test_get_comments_by_track(self):
        url = reverse("track_comments", kwargs={"pk": self.track.pk})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        self.assertEqual(response.data[0]["text"], "good_comment")
        self.assertEqual(response.data[1]["text"], "bad_comment")
