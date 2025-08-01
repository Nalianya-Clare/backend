import uuid

from django.contrib.auth.models import BaseUserManager, AbstractUser, PermissionsMixin, Group
from django.core.mail import send_mail
from django.core.validators import RegexValidator
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from util.storage_location.utils import PublicMediaStorage


class UserManager(BaseUserManager):
    """Define a model manager for a User model with no username field."""
    use_in_migrations = True

    @classmethod
    def normalize_email(cls, email):
        return super().normalize_email(email).lower()

    def _create_user(self, email, password=None, **extra_fields):
        """Create and save a User with the given email and password."""
        if not email:
            raise ValueError('The given email address must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_user(self, email, password=None, **extra_fields):
        """Create and save a regular User with the given email and password."""
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        extra_fields.setdefault('is_medical_staff', False)
        return self._create_user(email, password, **extra_fields)

    def create_admin_user(self, email, password=None, **extra_fields):
        """Create and save an Organization Admin User with the given email and password."""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_medical_staff', True)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        """Create and save a SuperUser with the given email and password."""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('role', 'super')

        if extra_fields.get('is_staff') is not True:
            raise ValueError(_("Super user must have is_staff=True."))

        if extra_fields.get('role') != 'super':
            raise ValueError(_("Super user must have role=super."))

        if extra_fields.get('is_superuser') is not True:
            raise ValueError(_("Super user must have is_superuser=True."))

        return self._create_user(email, password, **extra_fields)

  

class User(AbstractUser, PermissionsMixin):
    USER = 'user'
    ADMIN = 'admin'
    SUPER = 'super'
    ROLES = (
        (USER, 'User'),
        (ADMIN, 'Medical Staff'),
        (SUPER, 'Super Admin'),
    )
    GENDER = (
        ('male', 'Male'),
        ('female', 'Female'),
        ('others', 'Others')
    )
    PROFESSION = (
        ('gynecologist', 'gynecologist'),
        ('obstetricians', 'obstetricians'),
        ('other', 'Other')
    )

    AUTH_PROVIDERS = {
        'email': 'email', 'google': 'google', 'twitter': 'twitter', 'facebook': 'facebook'
    }

    alphanumeric = RegexValidator(r'^[0-9a-zA-Z]*$', message='Only alphanumeric characters are allowed.')
    phone_validation = RegexValidator(r"^\+(\d{1,4})\s(\d{7,10})$",
                                      message='Invalid phone format. accepted format is (+254 xxxxxxxxx)')

    username = models.CharField(_('User Name'), default='', max_length=150, validators=[alphanumeric],
                                null=True, blank=True)
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(_('Email'), unique=True, max_length=100)
    first_name = models.CharField(_('First name'), max_length=125, null=True, blank=True, default='',
                                  validators=[alphanumeric])
    last_name = models.CharField(_('Last name'), max_length=125, null=True, blank=True, default='',
                                 validators=[alphanumeric])
    phone = models.CharField(_('Phone number'), max_length=20, null=True, blank=True, default='',
                             validators=[phone_validation])

    profile_picture = models.ImageField(_('Profile picture'), default='', null=True, blank=True,
                                        upload_to="uploads/user/profile/",
                                        storage=PublicMediaStorage())
    gender = models.CharField(max_length=20, choices=GENDER, null=True, blank=True)
    profession = models.CharField(max_length=50, choices=PROFESSION, null=True, blank=True)
    verified = models.BooleanField(default=False)
    is_staff = models.BooleanField(_('Staff status'),
                                   default=False,
                                   help_text=_('Designates whether the user can log into this admin site.')
                                   )
    is_active = models.BooleanField(_('Active'),
                                    default=True,
                                    help_text=_('Designates whether this user should be treated as active. \
                                                    Unselect this instead of deleting accounts.'
                                                ), )
    is_superuser = models.BooleanField(_('Super Admin status'),
                                       default=False,
                                       help_text='Grants the all system privileges to the user'
                                       )
    is_medical_staff = models.BooleanField(_('Medical Staff'),
                                          default=False,
                                          help_text=_('Designates whether the user is a medical staff.')
                                          )
    is_approved_staff = models.BooleanField(_('Approved Staff'),
                                             default=False,
                                             help_text=_('Designates whether the user is an approved medical staff.')
                                             )
    meeting_url = models.CharField(_('Meeting URL'), max_length=255, null=True, blank=True)
    auth_provider = models.CharField(max_length=255, blank=True, null=True, default=AUTH_PROVIDERS.get('email'))
    date_joined = models.DateTimeField(_('date joined'), auto_now_add=True)
    date_updated = models.DateTimeField(_('updated at'), auto_now=True)
    last_login = models.DateTimeField(_("last login"), blank=True, null=True)
    password_expiry_date = models.DateTimeField(null=True, blank=True)

    role = models.CharField(_("User role"), max_length=20, choices=ROLES, default=USER, null=True, blank=True)

    objects = UserManager()
    USERNAME_FIELD = 'email'
    EMAIL_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name', 'phone', 'password', 'gender']

    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')
        ordering = ['date_joined']

    def __str__(self):
        return f'{self.email}'

    def set_password(self, raw_password, days:int=120):
        # Calculate password expiry date
        self.password_expiry_date = timezone.now() + timezone.timedelta(days=days)
        super().set_password(raw_password)

    def get_full_name(self):
        """
            Returns the first_name + the last_name, with a space in between.
        """
        fullname = f'{self.first_name} {self.last_name}'
        return fullname.strip()

    def get_email(self):
        """Returns user's email"""
        return self.email

    def email_user(self, subject, message, from_email=None, **kwargs):
        """Sending email to this user"""
        send_mail(subject, message, from_email, [self.email], **kwargs)

    def is_user_admin(self):
        user = Group.objects.get(name=self.ADMIN)
        return user in self.groups.all()

    def is_super_admin(self):
        user = Group.objects.get(name=self.SUPER_ADMIN)
        return user in self.groups.all()

    def user_roles(self):
        if self.is_user_admin:
            return _(self.ADMIN)
        if self.is_super_admin:
            return _(self.SUPER_ADMIN)
        if self.is_staff:
            return _(self.STAFF)

    def get_department_name(self):
        if self.department:
            return f'{self.department.name}'

    def delete(self, *args, **kwargs):
        # first, delete the image file
        if self.profile_picture:
            self.profile_picture.delete(save=False)
        # now delete the object
        super(User, self).delete(*args, **kwargs)


class LoggedInUser(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(User, related_name='logged_in_user', on_delete=models.CASCADE)
    session_key = models.CharField(max_length=32, blank=True, null=True)
    refresh_token = models.CharField(max_length=600, blank=True, null=True)

    def __str__(self):
        return self.user.first_name