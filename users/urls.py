from django.urls import path
from users.views import (
    UserSignUpAPIView,
    ActivateAccountAPIView,
    SignInAPIView,
    ObtainAccessTokenAPIView,
    TestView,
    ChangePasswordAPIView,
    ResetPasswordRequestAPIView,
    ResetPasswordConfirmAPIView,
    SpotifyLoginAPIView,
    SpotifyAuthAPIView,
)

urlpatterns = [
    path("sign_up/", UserSignUpAPIView.as_view(), name="sign_up"),
    path("spotify_login/", SpotifyLoginAPIView.as_view(), name="spotify_login"),
    path("spotify_callback/", SpotifyAuthAPIView.as_view(), name="spotify_callback"),
    path(
        "activate/<str:uidb64>/<str:token>",
        ActivateAccountAPIView.as_view(),
        name="activate",
    ),
    path("sign_in/", SignInAPIView.as_view(), name="sign_in"),
    path(
        "sign_in/refresh/", ObtainAccessTokenAPIView.as_view(), name="sign_in_refresh"
    ),
    path("test/", TestView.as_view()),
    path("change_password/", ChangePasswordAPIView.as_view(), name="change_password"),
    path(
        "reset_password_request/",
        ResetPasswordRequestAPIView.as_view(),
        name="reset_password_request",
    ),
    path(
        "reset_password_confirm/<str:uidb64>/<str:token>/",
        ResetPasswordConfirmAPIView.as_view(),
        name="reset_password_confirm",
    ),
]
