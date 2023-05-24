from django.urls import path
from users.views import UserSignUpView, ActivateAccountView, SignInView

urlpatterns = [
    path("sign_up/", UserSignUpView.as_view(), name="sign_up"),
    path(
        "activate/<str:uidb64>/<str:token>",
        ActivateAccountView.as_view(),
        name="activate",
    ),
    path("sign_in/", SignInView.as_view(), name="sign_in")
]
