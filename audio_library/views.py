import os

from rest_framework import generics, viewsets, parsers, views, status
from rest_framework.response import Response
from django.db.models import Q
from django_filters.rest_framework import DjangoFilterBackend
from django.http import FileResponse

from audio_library.models import Genre, License, Album, Track, PlayList, Comment
from audio_library.serializers import (
    GenreSerializer,
    LicenseSerializer,
    AlbumSerializer,
    CreateTrackSerializer,
    TrackSerializer,
    CreatePlayListSerializer,
    PlayListSerializer,
    CommentSerializer,
    CommentAuthorSerializer,
)
from audio_library.classes import MixedSerializer, Pagination
from core.permissions import IsAuthor
from core.services import delete_old_file


class GenreAPIView(generics.ListAPIView):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer


class LicenseAPIView(viewsets.ModelViewSet):
    serializer_class = LicenseSerializer
    permission_classes = [IsAuthor]

    def get_queryset(self):
        return License.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class AlbumAPIView(viewsets.ModelViewSet):
    parser_classes = (parsers.MultiPartParser,)
    serializer_class = AlbumSerializer
    permission_classes = [IsAuthor]

    def get_queryset(self):
        return Album.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def perform_destroy(self, instance):
        delete_old_file(instance.cover.path)
        instance.delete()


class PublicAlbumAPIView(generics.ListAPIView):
    serializer_class = AlbumSerializer

    def get_queryset(self):
        return Album.objects.filter(user__id=self.kwargs.get("pk"), private=False)


class TrackAPIView(MixedSerializer, viewsets.ModelViewSet):
    parser_classes = (parsers.MultiPartParser,)
    permission_classes = [IsAuthor]
    serializer_class = CreateTrackSerializer
    serializer_classes_by_action = {"list": TrackSerializer}

    def get_queryset(self):
        return Track.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def perform_destroy(self, instance):
        delete_old_file(instance.cover.path)
        delete_old_file(instance.file.path)
        instance.delete()


class PlayListAPIView(MixedSerializer, viewsets.ModelViewSet):
    parser_classes = (parsers.MultiPartParser,)
    permission_classes = [IsAuthor]
    serializer_class = CreatePlayListSerializer
    serializer_classes_by_action = {"list": PlayListSerializer}

    def get_queryset(self):
        return PlayList.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def perform_destroy(self, instance):
        delete_old_file(instance.cover.path)
        instance.delete()


class TrackListAPIView(generics.ListAPIView):
    queryset = Track.objects.filter(
        Q(album=None) | Q(album__private=False), private=False
    )
    serializer_class = TrackSerializer
    pagination_class = Pagination
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["title", "user__username", "album__name", "genre__name"]


class AuthorTrackListAPIView(generics.ListAPIView):
    serializer_class = TrackSerializer
    pagination_class = Pagination
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["title", "album__name", "genre__name"]

    def get_queryset(self):
        return Track.objects.filter(
            Q(album=None) | Q(album__private=False),
            user__id=self.kwargs.get("pk"),
            private=False,
        )


class StreamingTrackAPIView(views.APIView):
    def add_audition(self):
        self.track.auditions += 1
        self.track.save()

    def get(self, request, pk):
        try:
            self.track = Track.objects.get(pk=pk)
        except:
            return Response(
                {"track": "Such track doesn't exist"}, status=status.HTTP_404_NOT_FOUND
            )

        if self.track.file and os.path.exists(self.track.file.path):
            self.add_audition()
            return FileResponse(
                open(self.track.file.path, "rb"), filename=self.track.file.name
            )
        else:
            return Response(
                {"track": "File with this track doesn't exist or removed"},
                status=status.HTTP_404_NOT_FOUND,
            )


class DownloadTrackAPIView(views.APIView):
    def add_download(self):
        self.track.downloads += 1
        self.track.save()

    def get(self, request, pk):
        try:
            self.track = Track.objects.get(pk=pk)
        except:
            return Response(
                {"track": "Such track doesn't exist"}, status=status.HTTP_404_NOT_FOUND
            )

        if self.track.file and os.path.exists(self.track.file.path):
            self.add_download()
            return FileResponse(
                open(self.track.file.path, "rb"),
                filename=self.track.file.name,
                as_attachment=True,
            )
        else:
            return Response(
                {"track": "File with this track doesn't exist or removed"},
                status=status.HTTP_404_NOT_FOUND,
            )


class CommentAPIView(generics.ListAPIView):
    serializer_class = CommentSerializer

    def get_queryset(self):
        return Comment.objects.filter(track__id=self.kwargs.get("pk"))


class CommentAuthorAPIView(viewsets.ModelViewSet):
    serializer_class = CommentAuthorSerializer
    permission_classes = [IsAuthor]

    def get_queryset(self):
        return Comment.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
