from rest_framework import parsers, permissions, viewsets
from users.serializers.base_serializers import (
    UserSerializer,
    AuthorSerializer,
    SocialLinkSerializer,
)
from users.models import User
from users.permissions import IsAuthor


class UserAPIView(viewsets.ModelViewSet):
    parser_classes = (parsers.MultiPartParser,)
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return self.request.user

    def get_object(self):
        return self.get_queryset()


class AuthorAPIView(viewsets.ReadOnlyModelViewSet):
    queryset = User.objects.all().prefetch_related("social_links")
    serializer_class = AuthorSerializer
    permission_classes = [permissions.IsAuthenticated]


class SocialLinkAPIView(viewsets.ModelViewSet):
    serializer_class = SocialLinkSerializer
    permission_classes = [IsAuthor]

    def get_queryset(self):
        return self.request.user.social_links.all()

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
