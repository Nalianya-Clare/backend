from random import SystemRandom
from typing import Dict
import jwt
import requests

from attr import define
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured

from django.urls import reverse_lazy
from urllib.parse import urlencode

from oauthlib.common import UNICODE_ASCII_CHARACTER_SET
from rest_framework.exceptions import APIException


@define
class GoogleLoginCredentials:
    """
    Define google login credential variables
    """
    client_id: str
    client_secret: str
    project_id: str


@define
class GoogleAccessTokens:
    """
        Define id_token and access_token
        :return: decoded id_token
    """
    id_token: str
    access_token: str

    def decode_id_token(self) -> Dict[str, str]:
        """
        This method helps to decode the jwt id_token, to access the token information (Profile, email)
        :return:
        """
        id_token = self.id_token
        decoded_token = jwt.decode(jwt=id_token, options={"verify_signature": False})
        return decoded_token


class GoogleAuthService:
    """
    This service helps in setting up required google endpoint, scopes and the query params values to enable the app
    authorization
    """
    API_URI = reverse_lazy('account:social-auth:callback')

    GOOGLE_AUTH_URL = 'https://accounts.google.com/o/oauth2/auth'
    ACCESS_TOKEN_URL = 'https://oauth2.googleapis.com/token'
    GOOGLE_USER_INFO_URL = 'https://www.googleapis.com/oauth2/v3/userinfo'

    SCOPES = [
        "https://www.googleapis.com/auth/userinfo.email",
        "https://www.googleapis.com/auth/userinfo.profile",
        "openid",
    ]

    def __init__(self):
        self._credentials = get_google_login_credentials()

    @staticmethod
    def _generate_state_session_token(length=30, chars=UNICODE_ASCII_CHARACTER_SET):
        """
        This func generates the sate code that is shared with Google server, This is used to prevent the cross-site
        scripting attacks when making calls to google auth end point
        """
        rand = SystemRandom()
        state = "".join(rand.choice(chars) for _ in range(length))
        return state

    def _get_redirect_uri(self):
        """ Create an url that Google will use to send authorization code on success (callback url) """
        domain = settings.BASE_BACKEND_URL
        api_uri = self.API_URI
        redirect_uri = f"{domain}{api_uri}"
        return redirect_uri

    def get_authorization_url(self):
        """
            Create a Google authorization url and pass the required parameters
            This is the url responsible launching google login screen
        """
        redirect_uri = self._get_redirect_uri()
        state = self._generate_state_session_token()

        params = {
            "response_type": "code",
            "client_id": self._credentials.client_id,
            "redirect_uri": redirect_uri,
            "scope": " ".join(self.SCOPES),
            "state": state,
            "access_type": "offline",
            "include_granted_scopes": "true",
            "prompt": "select_account",
        }

        query_params = urlencode(params)
        authorization_url = f"{self.GOOGLE_AUTH_URL}?{query_params}"

        return authorization_url, state

    def get_tokens(self, *, code: str) -> GoogleAccessTokens:
        """
        This method helps retrieve both google id_token(jwt format) and the access_token with the help of the
        authorization code return by Google
        :param code:
        :return: Id_token and access_tokens from Google authorization server
        """
        redirect_uri = self._get_redirect_uri()

        data = {
            "code": code,
            "client_id": self._credentials.client_id,
            "client_secret": self._credentials.client_secret,
            "redirect_uri": redirect_uri,
            "grant_type": "authorization_code",
        }

        response = requests.post(self.ACCESS_TOKEN_URL, data=data)
        if not response.ok:
            raise APIException(response.text)

        tokens = response.json()
        google_tokens = GoogleAccessTokens(
            id_token=tokens['id_token'],
            access_token=tokens['access_token']
        )

        return google_tokens

    def get_user_info(self, *, google_tokens: GoogleAccessTokens):
        """
        This method uses the access_token to get the user information
        :param google_tokens:
        :return:
        """
        access_token = google_tokens.access_token

        response = requests.get(
            self.GOOGLE_USER_INFO_URL,
            params={"access_token": access_token}
        )

        if not response.ok:
            raise APIException(response.text)
        return response.json()


def get_google_login_credentials() -> GoogleLoginCredentials:
    """
    Setting credentials from Google console
    :return: google credentials
    """
    client_id = settings.GOOGLE_CLIENT_ID
    client_secret = settings.GOOGLE_CLIENT_SECRET
    project_id = settings.GOOGLE_PROJECT_ID

    if not client_id:
        raise ImproperlyConfigured('GOOGLE_CLIENT_ID is missing in the config file')
    if not client_secret:
        raise ImproperlyConfigured('GOOGLE_CLIENT_SECRET is not configured')
    if not project_id:
        raise ImproperlyConfigured('GOOGLE_PROJECT_ID not configured')

    credentials = GoogleLoginCredentials(
        client_id=client_id,
        client_secret=client_secret,
        project_id=project_id
    )
    return credentials
