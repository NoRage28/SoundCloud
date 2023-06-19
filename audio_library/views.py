from rest_framework import generics, viewsets, parsers

from audio_library.models import (Genre, License, Album)
from audio_library.serializers import (GenreSerializer, LicenseSerializer, AlbumSerializer)
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
