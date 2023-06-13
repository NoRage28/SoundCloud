from django.urls import path
from rest_framework.routers import DefaultRouter
from users.endpoints.views import UserAPIView, AuthorAPIView, SocialLinkAPIView

router = DefaultRouter()
router.register(r"social_links", SocialLinkAPIView, basename="social_link")

urlpatterns = [
    path("me/", UserAPIView.as_view({"get": "retrieve", "put": "update"}), name="me"),
    path("author", AuthorAPIView.as_view({"get": "list"}), name="authors_list"),
    path(
        "author/<int:pk>",
        AuthorAPIView.as_view({"get": "retrieve"}),
        name="author_record",
    ),
]

urlpatterns += router.urls
