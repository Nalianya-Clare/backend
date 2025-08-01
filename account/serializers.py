import os
from datetime import datetime, timedelta
from typing import Dict, Any

from adrf.serializers import Serializer
from django.conf import settings
from django.contrib.auth import get_user_model, authenticate
from django.contrib.auth.models import Group, Permission
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.utils.http import urlsafe_base64_decode
from rest_framework import serializers, exceptions, status
from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer, AuthUser, TokenRefreshSerializer
from rest_framework_simplejwt.tokens import Token, RefreshToken

from account.models import User, LoggedInUser
from util.emails.success_event_registration import send_mail
from util.errors.exceptionhandler import CustomInternalServerError
from util.helper import generate_unique_string
from util.messages.hundle_messages import success_response


class CheckRefreshTokenSerializer(serializers.Serializer):
    refresh = serializers.CharField()

    class Meta:
        fields = ['refresh']


class CustomTokenObtainSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user: AuthUser) -> Token:
        token = super().get_token(user)

        token['firstname'] = user.first_name if user.first_name else None
        token['lastname'] = user.last_name if user.last_name else None
        token['verified'] = user.verified
        token['email'] = user.email
        token['provider'] = user.auth_provider
        token['status'] = 'Active' if user.is_active else 'In-active'
        token['phone'] = user.phone if user.phone else None
        token['profession'] = str(user.profession) if user.profession else None
        token['role'] = user.role

        return token

    def validate(self, attrs: Dict[str, Any]) -> Dict[Any, Any]:
        data = super().validate(attrs)
        user = self.user
        if user:
            # Check if the user has an active session
            active_sessions = LoggedInUser.objects.filter(user=user).first()

            if active_sessions:
                refresh_token = active_sessions.refresh_token
                # Invalidate existing token

                try:
                    refresh_tokens = RefreshToken(refresh_token)
                    refresh_tokens.blacklist()
                except (TokenError, AttributeError):
                    pass

                # Update the session with the new refresh token
                active_sessions.refresh_token = data['refresh']
                active_sessions.save()

            else:
                # Create a new session
                LoggedInUser.objects.create(user=user, refresh_token=data['refresh'])
        return data


class RefreshTokenSerializer(TokenRefreshSerializer):
    def validate(self, attrs: Dict[str, Any]) -> Dict[str, str]:
        data = super().validate(attrs)
        refresh_token = LoggedInUser.objects.filter(refresh_token=attrs["refresh"]).first()

        if refresh_token:
            refresh_token.refresh_token = data['refresh']
            refresh_token.save()

        return data


class LoginSerializer(CustomTokenObtainSerializer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def validate(self, attrs):
        try:

            try:
                token = super().validate(attrs)
            except AuthenticationFailed:
                raise CustomInternalServerError(
                    message="Invalid username or password.",
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    code="invalid_credentials"
                )
            res = dict()

            if self.user.password_expiry_date and self.user.password_expiry_date < timezone.now():
                raise CustomInternalServerError(
                    message="Password expired. please reset your password to continue.",
                    status_code=status.HTTP_400_BAD_REQUEST,
                    code="bad_request"
                )

            res["token"] = token
            res["expires_in"] = datetime.utcnow() + timedelta(
                seconds=settings.SIMPLE_JWT['ACCESS_TOKEN_LIFETIME'].seconds)

            response_data = success_response(status_code=status.HTTP_200_OK, message_code="authentication",
                                             message=res)

            return response_data
        except CustomInternalServerError as api_exec:
            raise api_exec

        except Exception as e:
            raise CustomInternalServerError(message=str(e))


class RegistrationSerializer(serializers.ModelSerializer, CustomTokenObtainSerializer):
    confirm_psd = serializers.CharField(style={input: 'password'}, write_only=True)
    full_name = serializers.SerializerMethodField(method_name='get_user_full_name')
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.response_data = None

    class Meta:
        model = get_user_model()
        fields = ['id', 'profession', 'email', 'first_name', 'last_name', 'full_name', 'phone', 'gender',
                 'password', 'confirm_psd', 'is_superuser', 'is_staff', 'is_medical_staff','verified', 'auth_provider',
                  'is_active', 'role', 'date_joined', 'meeting_url', 'last_login']
        extra_kwargs = {
            'password': {'write_only': True},
            'is_superuser': {'write_only': True},
            'is_staff': {'write_only': True},
        }
        read_only_fields = ['id', 'date_joined', 'full_name']

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['email'] = instance.email
        return representation

    def get_user_full_name(self, obj):
        return obj.get_full_name()

    def validate(self, attrs):
        """
        overrides the parent serializer class validate method
        :param attrs:
        :return: 
        """
        email: str = attrs.get('email', None)
        valid_email = self.Meta.model.objects.normalize_email(email)

        if get_user_model().objects.filter(email=valid_email):

            raise exceptions.AuthenticationFailed('The user with the email provided exist', "user_exists", )
        else:
            password = attrs.get('password')
            password2 = attrs.get('confirm_psd')
            role = attrs.get('role', None)

            if role in [User.ADMIN, User.SUPER]:
                password = generate_unique_string()
                attrs['password'] = password
            else:
                if password != password2:
                    raise exceptions.AuthenticationFailed('Passwords must match.', "password_mismatch")
                try:
                    validate_password(password=password)
                except ValidationError as err:
                    raise serializers.ValidationError({'password': list(err.messages)})
                
            attrs.pop('confirm_psd', None)

            if 'role' in attrs:
                role = attrs['role']
                try:
                    if role == User.ADMIN:
                        user = get_user_model().objects.create_admin_user(**attrs)
                        group = Group.objects.get(name='Admins')
                        group.user_set.add(user)

                    elif role == User.SUPER:
                        user = get_user_model().objects.create_superuser(**attrs)
                        group = Group.objects.get(name='Super admin')
                        group.user_set.add(user)
                    else:
                        user = get_user_model().objects.create_user(**attrs)
                    send_account_creation_email(user=user, role=role, password_=password, login_url_=settings.CONSOLE_URL)
                    self.response_data = success_response(status_code=status.HTTP_200_OK, message_code="authentication",
                                                message="Account created")
                    user.set_password(password,int(settings.PASSWORD_EXPIRY_DAYS))
                    user.save()
                except Group.DoesNotExist as err:
                    raise serializers.ValidationError({'group_error': str(err)})

            else:
                user = get_user_model().objects.create_user(**attrs)
                send_account_creation_email(user=user)
                token = super().validate(attrs)
                data = {
                    "token": token,
                    "expires_in": settings.SIMPLE_JWT.get('ACCESS_TOKEN_LIFETIME')
                }
                self.response_data = success_response(status_code=status.HTTP_200_OK, message_code="authentication",
                                                message=data)
                
                user.set_password(password)
                user.save()
        return self.response_data


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = get_user_model()
        fields = ['id', 'email', 'first_name', 'last_name', 'phone', "profile_picture",
                  'role','gender', 'profession', 'is_active', 'meeting_url'
                  ]
    
 

class GoogleLoginSerializer(serializers.ModelSerializer, CustomTokenObtainSerializer):
    password = os.getenv('GOOGLE_CLIENT_SECRET')

    class Meta:
        model = User
        fields = ['id', 'email', 'first_name', 'last_name', 'phone', 'password', 'auth_provider']
        read_only_fields = ['id']

    def validate(self, attrs):
        email = attrs.get('email')
        res = dict()
        try:
            user = User.objects.get(email=email)
            if attrs.get('auth_provider') == user.auth_provider:
                authenticate(email=email, password=self.password)
                attrs['password'] = self.password
                token = super().validate(attrs)

                res["new_user"] = False
                res["token"] = token
                res["expires_in"] = datetime.now() + timedelta(
                    seconds=settings.SIMPLE_JWT['ACCESS_TOKEN_LIFETIME'].seconds)

                response_data = success_response(status_code=status.HTTP_200_OK, message_code="authentication",
                                                 message=res)

                return response_data
            else:
                response_data = success_response(status_code=status.HTTP_400_BAD_REQUEST, message_code="authentication",
                                                 message={'message': 'Account exists with different loin provider'})
                return response_data
        except User.DoesNotExist:
            user = User.objects.create_user(**attrs)
            user.set_password(self.password)
            user.save()

            token = super().validate(attrs)

            res["new_user"] = True
            res["token"] = token
            res["expires_in"] = datetime.utcnow() + timedelta(
                seconds=settings.SIMPLE_JWT['ACCESS_TOKEN_LIFETIME'].seconds)

            response_data = success_response(status_code=status.HTTP_200_OK, message_code="authentication",
                                             message=res)
            return response_data


class PasswordResetSerializer(serializers.Serializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        fields = ('password',)

    def __init__(self, *args, **kwargs):
        self.user = None
        super().__init__(*args, **kwargs)

    def validate(self, data):
        try:
            password = data.get('password')
            token = self.context.get("kwargs").get("token")
            encoded_pk = self.context.get("kwargs").get("encoded_pk")

            if token is None or encoded_pk is None:
                raise CustomInternalServerError(
                    message="Missing data",
                    status_code=status.HTTP_400_BAD_REQUEST,
                    code="bad_request"
                )

            pk = urlsafe_base64_decode(encoded_pk).decode()
            user = User.objects.filter(pk=pk)
            if not user.exists():
                raise CustomInternalServerError(
                    message="User with ID not found.",
                    status_code=status.HTTP_404_NOT_FOUND,
                    code="not_found"
                )
            self.user = user.first()

            if not PasswordResetTokenGenerator().check_token(self.user, token):
                raise CustomInternalServerError(
                    message="Invalid reset token.",
                    status_code=status.HTTP_400_BAD_REQUEST,
                    code="bad_request"
                )

            validate_password(password=password)

            if self.user.check_password(password):
                raise CustomInternalServerError(
                    message="You cannot reuse an old password.",
                    status_code=status.HTTP_400_BAD_REQUEST,
                    code="bad_request"
                )

            self.user.set_password(password)
            self.user.save()
            return data
        except CustomInternalServerError as api_exec:
            raise api_exec
        except ValidationError as e:
            raise CustomInternalServerError(
                message=e.messages,
                status_code=status.HTTP_400_BAD_REQUEST
            )




class EmailSerializer(serializers.Serializer):
    email = serializers.EmailField()
    is_admin = serializers.BooleanField(default=False)

    class Meta:
        fields = ('email',)


class VerificationCodeSerializer(Serializer):
    code = serializers.CharField(required=True)
    authkey = serializers.CharField(required=False)


class PermissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Permission
        fields = ("id", "codename")


class GroupSerializer(serializers.ModelSerializer):
    name = serializers.CharField()
    permissions = PermissionSerializer(many=True, required=False)

    def __init__(self, *args, **kwargs):
        self.permission = None
        super().__init__(*args, **kwargs)

    class Meta:
        model = Group
        fields = "__all__"

    def create(self, validated_data):
        try:
            if "permissions" in validated_data:
                self.permission = validated_data.pop("permissions", None)

            if self.Meta.model.objects.filter(name=validated_data['name']).exists():
                raise CustomInternalServerError(
                    message="Group '{}' already exists".format(validated_data['name']),
                    status_code=status.HTTP_400_BAD_REQUEST,
                    code="bad_request"
                )

            group_instance = self.Meta.model.objects.create(**validated_data)

            if self.permission is not None:
                for perm in self.permission:
                    permission_instance = Permission.objects.filter(codename=perm.get("codename"))
                    if permission_instance.exists():
                        group_instance.permissions.add(permission_instance.first())

            return group_instance

        except CustomInternalServerError as api_exec:
            raise api_exec

        except Exception as e:
            raise CustomInternalServerError(
                message=str(e),
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def update(self, instance, validated_data):
        try:
            permissions = validated_data.pop("permissions", None)
            updated_fields = [k for k in validated_data]

            for key, value in validated_data.items():
                setattr(instance, key, value)
            instance.save(update_fields=updated_fields)

            if permissions is not None:
                instance.permissions.clear()
                for perm in permissions:
                    permission_instance = Permission.objects.filter(codename=perm.get("codename"))
                    if permission_instance.exists():
                        instance.permissions.add(permission_instance.first())

                instance.save()

            return instance

        except Exception as e:
            raise CustomInternalServerError(
                message=str(e),
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

# ADD ROLE(ACCOUNT TYPE), DATE CREATED
# 
def send_account_creation_email(
        user: User,
        role: str = None,
        password_: str = None,
        login_url_: str = settings.CONSOLE_URL,
        current_year=datetime.now().year) -> None:
    
    password_expiry_days = settings.PASSWORD_EXPIRY_DAYS
    template_name = "account_creation.html"
    subject = f"{user.first_name}, Thank you for joining appointment app."

    email = user.email
    if role == User.USER:
        context = {
            'full_name': '{} {}'.format(user.first_name, user.last_name),
            'name': user.first_name,
        }
    else:
        context = {
            'full_name': '{} {}'.format(user.first_name, user.last_name),
            'name': user.first_name,
            'password': password_,
            'email': email,
            'login_url': login_url_,
            'current_year': current_year,
            'password_expiry_days': password_expiry_days
        }
            
   

    recipient_list = [email]
    reply_to = [settings.EMAIL_REPLY_TO]

    send_mail(subject, template_name, context, recipient_list, reply_to)