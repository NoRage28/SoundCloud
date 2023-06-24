from django.urls import path
from rest_framework import routers

from audio_library.views import (
    GenreAPIView,
    LicenseAPIView,
    AlbumAPIView,
    PublicAlbumAPIView,
    TrackAPIView,
    PlayListAPIView,
    TrackListAPIView,
    AuthorTrackListAPIView,
    StreamingTrackAPIView,
    DownloadTrackAPIView,
    CommentAuthorAPIView,
    CommentAPIView,
)

router = routers.DefaultRouter()
router.register(r"license", LicenseAPIView, basename="license")
router.register(r"album", AlbumAPIView, basename="album")
router.register(r"track", TrackAPIView, basename="track")
router.register(r"playlist", PlayListAPIView, basename="playlist")
router.register(r"comment", CommentAuthorAPIView, basename="comment")

urlpatterns = [
    path(
        "stream_track/<int:pk>/", StreamingTrackAPIView.as_view(), name="stream_track"
    ),
    path(
        "download_track/<int:pk>/",
        DownloadTrackAPIView.as_view(),
        name="download_track",
    ),
    path("genre/", GenreAPIView.as_view(), name="genre"),
    path("author_albums/<int:pk>/", PublicAlbumAPIView.as_view(), name="author_albums"),
    path("track_list/", TrackListAPIView.as_view(), name="track_list"),
    path(
        "author_track_list/<int:pk>/",
        AuthorTrackListAPIView.as_view(),
        name="author_track_list",
    ),
    path("comment_by_track/<int:pk>", CommentAPIView.as_view(), name="track_comments"),
]

urlpatterns += router.urls
