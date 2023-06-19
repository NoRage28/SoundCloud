from django.urls import path, include
from rest_framework import routers
from audio_library.views import (GenreAPIView, LicenseAPIView, AlbumAPIView, PublicAlbumAPIView)

router = routers.DefaultRouter()
router.register(r"license", LicenseAPIView, basename="license")
router.register(r"album", AlbumAPIView, basename="album")

urlpatterns = [
    path("genre/", GenreAPIView.as_view(), name="genre"),
    path("author_albums/<int:pk>/", PublicAlbumAPIView.as_view(), name="author_albums"),
]

urlpatterns += router.urls
