import os

from adrf.views import APIView
from django.shortcuts import redirect
from rest_framework import serializers, status
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView

from account.serializers import GoogleLoginSerializer
from .service import GoogleAuthService


class PublicApi(APIView):
    """
    Define a base ApiView class
    """
    authentication_classes = ()
    permission_classes = ()


class GoogleLoginRedirectApi(PublicApi):
    """
        Create a redirect view.
        This view redirects to google login page/interface to enable user key his email address
    """

    def get(self, request, *args, **kwargs):
        """
        A simple api get func to redirect user to the Google login page
        The redirect uri is generated from googleAuthService
        :param request:
        :param args:
        :param kwargs:
        :return: Redirects to google login page
        """
        google_login_flow = GoogleAuthService()
        authorization_url, state = google_login_flow.get_authorization_url()
        request.session['google_auth_state'] = state

        return redirect(authorization_url)


class GoogleLogin(PublicApi, TokenObtainPairView):
    """
    Create a view to be used by Google as a redirect or callback
    """

    class InputSerializer(serializers.Serializer):
        code = serializers.CharField(required=False)
        error = serializers.CharField(required=False)
        state = serializers.CharField(required=False)

    def get(self, request, *args, **kwargs):
        """
            This func gets the request parameters returned by google auth i.e., code, error and state
            Use error param to validate the endpoint
            state -> helps to prevent cross-site-scripting attacks
            :param request:
            :param args:
            :param kwargs: Code, error, state
            :return: Response with jwt auth_tokens
        """
        input_serializer = self.InputSerializer(data=request.GET)
        input_serializer.is_valid(raise_exception=True)

        validated_data = input_serializer.validated_data

        code = validated_data.get("code")
        error = validated_data.get("error")
        state = validated_data.get("state")

        if error is not None:
            return Response({'error': error},
                            status=status.HTTP_400_BAD_REQUEST)

        if code is None or state is None:
            return Response({'error': 'Code and state are required'},
                            status=status.HTTP_400_BAD_REQUEST)

        session_state = request.session.get('google_auth_state')

        if session_state is None:
            return Response({"error": "CSRF check failed."},
                            status=status.HTTP_400_BAD_REQUEST)

        del request.session['google_auth_state']

        if state != session_state:
            return Response(
                {"error": "CSRF check failed."},
                status=status.HTTP_400_BAD_REQUEST
            )
        google_login = GoogleAuthService()
        google_tokens = google_login.get_tokens(code=code)
        decoded_id_token = google_tokens.decode_id_token()
        # user_info = google_login.get_user_info(google_tokens=google_tokens)
        data = {
            'first_name': decoded_id_token['given_name'],
            'last_name': decoded_id_token['family_name'],
            'auth_provider': 'google',
            'email': decoded_id_token["email"],
            'password': os.getenv('GOOGLE_CLIENT_SECRET')
        }
        google_serializer = GoogleLoginSerializer(data=data)
        google_serializer.is_valid(raise_exception=True)
        return Response(google_serializer.validated_data, status=status.HTTP_200_OK)
