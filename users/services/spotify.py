import requests
import base64
from django.conf import settings
from django.contrib.auth import get_user_model
from rest_framework.exceptions import AuthenticationFailed
from typing import Optional

User = get_user_model()


def get_spotify_jwt(code: str) -> Optional[str]:
    url = "https://accounts.spotify.com/api/token"
    basic_str = f"{settings.SPOTIFY_CLIENT_ID}:{settings.SPOTIFY_SECRET}".encode("ascii")
    basic = base64.b64encode(basic_str)
    data = {
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": "http://127.0.0.1:8000/api/auth/spotify_callback"
    }
    headers = {
        "Authorization": f"Basic {basic.decode('ascii')}"
    }

    response = requests.post(url, data=data, headers=headers)
    if response.status_code == 200:
        res = response.json()
        return res.get("access_token")
    else:
        return None


def get_spotify_email(token: str) -> str:
    get_user_url = "https://api.spotify.com/v1/me"
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(get_user_url, headers=headers)
    res = response.json()
    return res.get("email")


def spotify_auth(code: str) -> User:
    token = get_spotify_jwt(code)
    if token is not None:
        email = get_spotify_email(token)
        user, _ = User.objects.get_or_create(email=email)
        if not user.is_active:
            user.is_active = True
            user.save()
        return user
    else:
        raise AuthenticationFailed("Bad token Spotify")
