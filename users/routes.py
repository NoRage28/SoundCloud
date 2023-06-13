from django.urls import path, include


urlpatterns = [
    path("", include("users.urls.base_urls")),
    path("auth/", include("users.urls.auth_urls")),
]
