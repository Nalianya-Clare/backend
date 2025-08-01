from django.shortcuts import render

# Create your views here.
import random
from datetime import datetime
from http import HTTPMethod

import requests
from adrf.viewsets import ViewSet
from asgiref.sync import sync_to_async
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, Permission
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.core.exceptions import ValidationError
from django.urls import reverse
from django.utils import timezone
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.views.decorators.csrf import csrf_exempt
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import exceptions, status
from rest_framework.decorators import action

from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.generics import GenericAPIView
from rest_framework.pagination import PageNumberPagination
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
from rest_framework_simplejwt.authentication import JWTStatelessUserAuthentication
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from util.emails.success_event_registration import send_mail
from util.errors.exceptionhandler import CustomInternalServerError
from util.messages.hundle_messages import success_response, error_response
from .models import User, LoggedInUser
from .serializers import (RegistrationSerializer, UserSerializer, PasswordResetSerializer,
                          EmailSerializer,
                          VerificationCodeSerializer, LoginSerializer, RefreshTokenSerializer,
                          CheckRefreshTokenSerializer, GroupSerializer,
                          PermissionSerializer)


class AccountCustomView(ModelViewSet, ViewSet):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTStatelessUserAuthentication]
    pagination_class = PageNumberPagination
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]

    async def create(self, request, *args, **kwargs):
        """Upload resource to the database"""
        serializer = self.get_serializer(data=request.data)
        await self.valid_serializer(serializer)
        data = await serializer.create(serializer.validated_data)
        response = success_response(status_code=status.HTTP_201_CREATED, message_code="upload_data",
                                    message={
                                        "enrolled": False,
                                        "event_id": data.id if data.id else '',
                                        "message": "Created successfully",
                                    })
        return Response(response, status=status.HTTP_201_CREATED)

    async def retrieve(self, request, *args, **kwargs):
        instance = await self.get_resource_object()
        serializer = self.get_serializer(instance)
        data = await self.get_serializer_data(serializer)
        response = success_response(status_code=status.HTTP_200_OK, message_code="get_data", message={"data": data})
        return Response(data=response, status=status.HTTP_200_OK)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        if getattr(instance, '_prefetched_objects_cache', None):
            instance._prefetched_objects_cache = {}
        data = success_response(status_code=status.HTTP_200_OK, message_code="update_success",
                                message="Updated successfully")
        return Response(data=data, status=status.HTTP_200_OK)

    def get_all_professional(self, request, *args, **kwargs):
        queryset = self.queryset.filter(is_professional=True)
        serializer = self.get_serializer(queryset, many=True)
        response = success_response(status_code=status.HTTP_200_OK, message_code="get_data",
                                    message={"data": serializer.data})
        return Response(data=response, status=status.HTTP_200_OK)
        
    def perform_update(self, serializer):
        serializer.save()

    def partial_update(self, request, *args, **kwargs):
        kwargs['partial'] = True
        return self.update(request, *args, **kwargs)

    async def destroy(self, request, *args, **kwargs):
        """
        Delete resource from the database
        :param request:
        :param args:
        :param kwargs:
        :return:
        """
        instance = await self.get_resource_object()
        if not instance:
            raise exceptions.NotFound("Resource not found", "not_found")
        return await self.destroy_object(instance)

    @sync_to_async
    def destroy_object(self, instance):
        instance.delete()
        response_data = success_response(status_code=status.HTTP_204_NO_CONTENT, message_code="delete_success",
                                         message="Deleted successfully.")

        return Response(data=response_data, status=status.HTTP_200_OK)

    @sync_to_async
    def get_resource_object(self):
        return self.get_object()

    @sync_to_async
    def get_serializer_data(self, serializer):
        return serializer.data

    @sync_to_async
    def valid_serializer(self, serializer):
        return serializer.is_valid(raise_exception=True)

class RegistrationView(TokenObtainPairView):
    """
            Handle http POST requests to add users.

            Returns:
            - Response: JSON response with object details or error message.
    """
    queryset = get_user_model().objects.all()
    serializer_class = RegistrationSerializer
    parser_classes = [MultiPartParser, FormParser, JSONParser]


class RefreshTokenView(TokenRefreshView):
    queryset = get_user_model().objects.all()
    serializer_class = RefreshTokenSerializer

class CheckRefreshTokenValidity(APIView):
    serializer_class = CheckRefreshTokenSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTStatelessUserAuthentication]

    def __init__(self, *args, **kwargs):
        self.response = None
        super().__init__(*args, **kwargs)

    def get(self, request, *args, **kwargs) -> Response:
        try:
            data = {
                'refresh': kwargs['refresh']
            }
            serializer = self.serializer_class(data=data)
            serializer.is_valid(raise_exception=True)
            user = request.user

            refresh_token = serializer.validated_data.get('refresh')

            if user:
                # Check if the user has an active session
                active_sessions = LoggedInUser.objects.filter(refresh_token=refresh_token).first()

                if active_sessions is not None:
                    refresh_tokens = active_sessions.refresh_token
                    # Invalidate existing token
                    try:
                        RefreshToken(refresh_token)
                    except (TokenError,) as e:
                        return error_response(status_code=status.HTTP_401_UNAUTHORIZED, error_code="permission_denied",
                                              message=e)
                    self.response = success_response(status_code=status.HTTP_200_OK, message_code="authorised",
                                                     message={"valid token"})
                else:
                    self.response = error_response(status_code=status.HTTP_401_UNAUTHORIZED,
                                                   error_code="permission_denied",
                                                   message="Invalid/expired token")
                return Response(self.response, status=200)
        except Exception as e:
            raise CustomInternalServerError(
                message=str(e),
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class LoginView(TokenObtainPairView):
    serializer_class = LoginSerializer
    # throttle_classes = (UserLoginRateThrottle,)


class UsersView(AccountCustomView):
    serializer_class = UserSerializer
    queryset = User.objects.all().order_by('-date_joined')
    pagination_class = PageNumberPagination
    parser_classes = [MultiPartParser, FormParser, JSONParser]


    # get user with proffesions only
    @action(detail=False, methods=[HTTPMethod.GET], permission_classes=[AllowAny],)
    def get_medical_staff(self, request, *args, **kwargs):
        queryset = self.queryset.filter(is_medical_staff=True, is_approved_staff=True)
        serializer = self.get_serializer(queryset, many=True)
        response = success_response(status_code=status.HTTP_200_OK, message_code="get_data",
                                    message={"data": serializer.data})
        return Response(data=response, status=status.HTTP_200_OK)
        

class PasswordReset(GenericAPIView):
    serializer_class = EmailSerializer

    @csrf_exempt
    def post(self, request):
        try:
            serializer = self.serializer_class(data=request.data)
            serializer.is_valid(raise_exception=True)
            email = serializer.validated_data.get('email')
            user = User.objects.filter(email=email).first()

            is_admin = serializer.validated_data.get('is_admin')

            if user:
                encoded_pk = urlsafe_base64_encode(force_bytes(user.pk))
                token = PasswordResetTokenGenerator().make_token(user)

                reset_url = reverse("account:confirm-reset-password", kwargs={
                    "encoded_pk": encoded_pk,
                    "token": token
                })

                if is_admin:
                    reset_password_url = "{}/password-reset/{}/{}".format(settings.ADMIN_URL, encoded_pk, token)
                else:
                    reset_password_url = "{}/reset/{}/{}".format(settings.FRONT_END_URL, encoded_pk, token)

                password_reset_url = "localhost:8000{}".format(reset_url)
                self.send_mail(user, reset_password_url)
                response = success_response(status_code=status.HTTP_200_OK, message_code="password_reset",
                                            message={"message": "Password resent link sent to {}."
                                                                " If you didn't receive an email in your inbox, "
                                                                "check your spam/junk folders".format(user.email)})
                return Response(response, status=status.HTTP_200_OK)
            else:
                response_data = error_response(status_code=status.HTTP_403_FORBIDDEN, error_code="permission_denied",
                                               message="User doesn't exist.")
                return Response(response_data, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            raise CustomInternalServerError(
                message=str(e),
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def send_mail(self, user: get_user_model(), reset_password_url: str) -> None:
        try:
            subject = "Your request to reset your Appointment App account password"
            template_name = "reset_password.html"
            current_year = datetime.now().year
            context = {
                'full_name': '{} {}'.format(user.first_name, user.last_name),
                'name': user.first_name,
                'url': reset_password_url,
                "current_year": current_year
            }

            recipient_list = [user.email]
            reply_to = [settings.EMAIL_REPLY_TO]

            send_mail(subject, template_name, context, recipient_list, reply_to)
        except Exception as e:
            raise CustomInternalServerError(
                message=str(e),
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class ResetPasswordView(GenericAPIView):
    serializer_class = PasswordResetSerializer

    # throttle_classes = (UserLoginRateThrottle,)

    @csrf_exempt
    def patch(self, request, *args, **kwargs):
        try:
            # get kwargs from the url param sent from the password reset request
            serializer = self.serializer_class(data=request.data, context={"kwargs": kwargs})
            serializer.is_valid(raise_exception=True)

            response = success_response(status_code=status.HTTP_200_OK, message_code="password_reset",
                                        message="password reset successful")
            return Response(response, status=status.HTTP_200_OK)

        except ValidationError as e:
            raise CustomInternalServerError(
                message=str(e),
                status_code=status.HTTP_400_BAD_REQUEST
            )


class EmailVerification(APIView):
    serializer_class = EmailSerializer

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @csrf_exempt
    def post(self, request, *args, **kwargs):
        try:
            serializer = self.serializer_class(data=request.data)
            serializer.is_valid(raise_exception=True)
            if 'email' in serializer.validated_data:
                email = serializer.validated_data['email']
                code = ''.join([str(random.randint(0, 9)) for _ in range(4)])
                expiry = timezone.now() + timezone.timedelta(minutes=10)

                request.session['code'] = {
                    'value': code,
                    'expiry': str(expiry)
                }
                request.session['email'] = email
                request.session.save()

                session = request.session.session_key
                self.send_verification_code(code, email)
                response = success_response(status_code=status.HTTP_200_OK, message_code="verify_success",
                                            message={
                                                "message": f"verification code sent to {email}",
                                                "session": session
                                            })
                return Response(data=response, status=status.HTTP_200_OK)
        except Exception as e:
            raise CustomInternalServerError(
                message=str(e),
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def send_verification_code(self, verification_code: str, recipient_mail: str) -> None:
        try:
            subject = "Account Verification."
            template_name = "code_verification.html"
            context = {
                'code': verification_code
            }
            recipient_list = [recipient_mail]
            reply_to = [settings.EMAIL_REPLY_TO]

            send_mail(subject, template_name, context, recipient_list, reply_to)
        except Exception as e:
            raise CustomInternalServerError(
                message=str(e),
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class CodeView(APIView):
    serializer_class = VerificationCodeSerializer

    @csrf_exempt
    def post(self, request, *args, **kwargs):
        try:
            serializer = self.serializer_class(data=request.data)
            serializer.is_valid(raise_exception=True)

            url = request.build_absolute_uri(f'/auth/v1/account/verify/confirm/{serializer.validated_data.get("code")}')

            # cookies = {'sessionid': serializer.validated_data.get('authkey'), 'secure': True}
            cookie_header = f'sessionid={serializer.validated_data.get("authkey")}; Secure'

            res = requests.get(url, headers={'Cookie': cookie_header}).json()

            return Response(data=res, status=status.HTTP_200_OK)
        except Exception as e:
            raise CustomInternalServerError(
                message=str(e),
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class CodeVerification(APIView):
    serializer_class = VerificationCodeSerializer

    def __init__(self, *args, **kwargs):
        self.email_valid = False
        self.response = None
        self.response_data = None
        self.user = None
        super().__init__(*args, **kwargs)

    def get(self, request, *args, **kwargs) -> Response:
        try:
            data = {
                'code': kwargs['code']
            }

            serializer = self.serializer_class(data=data)
            serializer.is_valid(raise_exception=True)
            if 'code' in serializer.validated_data:
                request_code = serializer.validated_data.get('code')
                session_code = request.session.get('code')

                if not session_code:
                    response_data = error_response(status_code=status.HTTP_400_BAD_REQUEST,
                                                   message='Invalid verification code', error_code="code_verification")
                    return Response(response_data, status=status.HTTP_400_BAD_REQUEST)

                code = session_code['value']

                expiry_date = session_code['expiry']

                format_string = '%Y-%m-%d %H:%M:%S.%f+00:00'

                exp = datetime.strptime(expiry_date, format_string)

                if timezone.now().replace(tzinfo=None) > exp:
                    response_data = error_response(status_code=status.HTTP_400_BAD_REQUEST,
                                                   message='verification code has expired',
                                                   error_code="code_verification")
                    return Response(response_data, status=status.HTTP_400_BAD_REQUEST)

                if int(request_code) != int(code):
                    response_data = error_response(status_code=status.HTTP_400_BAD_REQUEST,
                                                   message='Invalid code', error_code="code_verification")
                    return Response(response_data, status=status.HTTP_400_BAD_REQUEST)

                # set email_valid to true if code verification is ok
                self.email_valid = True
                request.session['email_valid'] = self.email_valid

                try:
                    self.user = get_user_model().objects.get(email=request.session.get('email'),
                                                             verified=False)
                    self.user.verified = True
                    self.user.save()

                    self.response = success_response(status_code=status.HTTP_200_OK, message_code="verify_success",
                                                     message={"verified": True,
                                                              "message": "Account verification successful"})
                except get_user_model().DoesNotExist:

                    self.user = get_user_model().objects.filter(email=request.session.get('email'),
                                                                verified=True).first()
                    if self.user:
                        self.response_data = error_response(status_code=status.HTTP_404_NOT_FOUND,
                                                            message='account already verified',
                                                            error_code="code_verification")
                        return Response(self.response_data, status=status.HTTP_404_NOT_FOUND)

                    self.response_data = error_response(status_code=status.HTTP_404_NOT_FOUND,
                                                        message='verification failed', error_code="code_verification")
                    return Response(self.response_data, status=status.HTTP_404_NOT_FOUND)

                # clear the session verification code
                del request.session['code']
                return Response(data=self.response, status=status.HTTP_200_OK)
        except Exception as e:
            raise CustomInternalServerError(
                message=str(e),
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class GroupView(AccountCustomView):
    serializer_class = GroupSerializer
    queryset = Group.objects.all()
    lookup_field = "id"


class PermissionView(AccountCustomView):
    serializer_class = PermissionSerializer
    queryset = Permission.objects.all()
    pagination_class = PageNumberPagination
