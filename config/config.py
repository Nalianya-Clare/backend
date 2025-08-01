import os
from datetime import timedelta


def ckeditor_config():
    customColorPalette = [
        {
            'color': 'hsl(4, 90%, 58%)',
            'label': 'Red'
        },
        {
            'color': 'hsl(340, 82%, 52%)',
            'label': 'Pink'
        },
        {
            'color': 'hsl(291, 64%, 42%)',
            'label': 'Purple'
        },
        {
            'color': 'hsl(262, 52%, 47%)',
            'label': 'Deep Purple'
        },
        {
            'color': 'hsl(231, 48%, 48%)',
            'label': 'Indigo'
        },
        {
            'color': 'hsl(207, 90%, 54%)',
            'label': 'Blue'
        },
    ]
    CKEDITOR_5_CONFIGS = {
        'default': {
            'toolbar': ['heading', '|', 'bold', 'italic', 'link',
                        'bulletedList', 'numberedList', 'blockQuote', 'imageUpload', ],

        },
        'extends': {
            'blockToolbar': [
                'paragraph', 'heading1', 'heading2', 'heading3',
                '|',
                'bulletedList', 'numberedList',
                '|',
                'blockQuote',
            ],
            'toolbar': ['heading', '|', 'outdent', 'indent', '|', 'bold', 'italic', 'link', 'underline',
                        'strikethrough',
                        'code', 'subscript', 'superscript', 'highlight', '|', 'codeBlock', 'sourceEditing',
                        'insertImage',
                        'bulletedList', 'numberedList', 'todoList', '|', 'blockQuote', 'imageUpload', '|',
                        'fontSize', 'fontFamily', 'fontColor', 'fontBackgroundColor', 'mediaEmbed', 'removeFormat',
                        'insertTable', ],
            'image': {
                'toolbar': ['imageTextAlternative', '|', 'imageStyle:alignLeft',
                            'imageStyle:alignRight', 'imageStyle:alignCenter', 'imageStyle:side', '|'],
                'styles': [
                    'full',
                    'side',
                    'alignLeft',
                    'alignRight',
                    'alignCenter',
                ]

            },
            'table': {
                'contentToolbar': ['tableColumn', 'tableRow', 'mergeTableCells',
                                   'tableProperties', 'tableCellProperties'],
                'tableProperties': {
                    'borderColors': customColorPalette,
                    'backgroundColors': customColorPalette
                },
                'tableCellProperties': {
                    'borderColors': customColorPalette,
                    'backgroundColors': customColorPalette
                }
            },
            'heading': {
                'options': [
                    {'model': 'paragraph', 'title': 'Paragraph', 'class': 'ck-heading_paragraph'},
                    {'model': 'heading1', 'view': 'h1', 'title': 'Heading 1', 'class': 'ck-heading_heading1'},
                    {'model': 'heading2', 'view': 'h2', 'title': 'Heading 2', 'class': 'ck-heading_heading2'},
                    {'model': 'heading3', 'view': 'h3', 'title': 'Heading 3', 'class': 'ck-heading_heading3'}
                ]
            }
        },
        'list': {
            'properties': {
                'styles': 'true',
                'startIndex': 'true',
                'reversed': 'true',
            }
        }
    }

    return CKEDITOR_5_CONFIGS


def jazzmin_config():
    jazzmin_setting = {
        # title of the window (Will default to current_admin_site.site_title if absent or None)
        "site_title": "Appointment app",

        # Title on the login screen (19 char max) (defaults to current_admin_site.site_header if absent or None)
        "site_header": "Appointment app console",

        # Title on the brand (19 chars max) (defaults to current_admin_site.site_header if absent or None)
        "site_brand": "Appointment app console",

        # Logo to use for your site, must be present in static files, used for brand on the top left
        "site_logo": "img/logo-mlh.png",

        # Logo to use for your site, must be present in static files, used for login form logo (defaults to site_logo)
        "login_logo": "/img/logo-mlh.png",

        # Logo to use for login form in dark themes (defaults to login_logo)
        "login_logo_dark": None,

        # CSS classes that are applied to the logo above
        "site_logo_classes": "img-circle",

        # The Relative path to a favicon for your site will default to site_logo if absent (ideally 32x32 px)
        "site_icon": None,

        # Welcome text on the login screen
        "welcome_sign": "Welcome to Appointment app",

        # Copyright on the footer
        "copyright": "Tc4a",

        # List of model admins to search from the search bar, search bar omitted if excluded
        # If you want to use a single search field you don't need to use a list, you can use a simple string
        "search_model": ["events.event", "auth.Group"],

        # Field name on a user model that contains avatar ImageField/URLField/Char-field or a callable that receives the
        # user
        "user_avatar": None,

        ############
        # Top Menu #
        ############

        # Links to put along the top menu
        "topmenu_links": [

            # Url that gets reversed (Permissions can be added)
            {"name": "Home", "url": "admin:index", "permissions": ["auth.view_user"]},

            # external url that opens in a new window (Permissions can be added)
            # {"name": "Support", "url": "https://github.com/farridav/django-jazzmin/issues", "new_window": True},

            # model admin to link to (Permissions checked against a model)
            {"model": "auth.User"},

            # App with a dropdown menu to all its model pages (Permissions checked against models)
            {"app": "event_enrolment"},
        ],

        #############
        # User Menu #
        #############

        # Additional links to include in the user menu on the top right ("app" url type is not allowed)
        "usermenu_links": [
            # {"name": "Support", "url": "https://github.com/farridav/django-jazzmin/issues", "new_window": True},
            # {"model": "auth.user"}
        ],

        #############
        # Side Menu #
        #############

        # Whether to display the side menu
        "show_sidebar": True,

        # Whether to aut expand the menu
        "navigation_expanded": True,

        # Hide these apps when generating a side menu e.g. (auth)
        "hide_apps": [],

        # Hide these models when generating side menu (e.g auth.user)
        "hide_models": [],

        # List of apps (and/or models) to a base side menu ordering off of (does not need to contain all apps/models)
        "order_with_respect_to": ["events", "event_enrolment", "organization", "department", "location", "wards",
                                  "profession", "certificate", "banner"],

        # Custom links to append to app groups, keyed on app name
        "custom_links": {
            "books": [{
                "name": "Make Messages",
                "url": "make_messages",
                "icon": "fas fa-comments",
                "permissions": ["books.view_book"]
            }]
        },

        # Custom icons for side menu apps/models See https://fontawesome.com/icons?d=gallery&m=free&v=5.0.0,5.0.1,
        # 5.0.10, 5.0.11,5.0.12,5.0.13,5.0.2,5.0.3,5.0.4,5.0.5,5.0.6,5.0.7,5.0.8,5.0.9,5.1.0,5.1.1,5.2.0,5.3.0,5.3.1,
        # 5.4.0,5.4.1, 5.4.2,5.13.0,5.12.0,5.11.2,5.11.1,5.10.0,5.9.0,5.8.2,5.8.1,5.7.2,5.7.1,5.7.0,5.6.3,5.5.0,
        # 5.4.2 for the full list of 5.13.0 free icon classes
        "icons": {
            "auth": "fas fa-users-cog",
            "auth.user": "fas fa-user",
            "auth.Group": "fas fa-users",
            "events_enrolment.eventenrollment": "fas fa-users",
        },
        # Icons that are used when one is not manually specified
        "default_icon_parents": "fas fa-chevron-circle-right",
        "default_icon_children": "fas fa-circle",

        #################
        # Related Modal #
        #################
        # Use modals instead of popups
        "related_modal_active": True,

        #############
        # UI Tweaks #
        #############
        # Relative paths to custom CSS/JS scripts (must be present in static files)
        "custom_css": None,
        "custom_js": None,
        # Whether to link font from fonts.googleapis.com (use custom_css to supply font otherwise)
        "use_google_fonts_cdn": True,
        # Whether to show the UI customizer on the sidebar
        "show_ui_builder": True,

        ###############
        # Change view #
        ###############
        # Render out the change view as a single form, or in tabs, current options are
        # - single
        # - horizontal_tabs (default)
        # - vertical_tabs
        # - collapsible
        # - carousel
        "changeform_format": "horizontal_tabs",
        # override change forms on a per modeladmin basis
        "changeform_format_overrides": {"auth.user": "collapsible", "auth.group": "vertical_tabs"},
        # Add a language dropdown into the admin
        "language_chooser": False,
    }

    return jazzmin_setting


def logging_config(base_dir):
    """ Logging setup script or Log configuration"""
    LOGGING = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "verbose": {
                "format": "{levelname} {asctime} {module} {message}",
                "style": "{",
            },
            "simple": {
                "format": "{levelname} {message}",
                "style": "{"
            }
        },

        "handlers": {
            "console": {
                "level": "DEBUG",
                "class": "logging.StreamHandler",
                "formatter": "simple",
            },
            "file": {
                "level": "DEBUG",
                "class": "logging.FileHandler",
                "filename": os.path.join(base_dir, "debug.log"),
                "formatter": "verbose",
            },
            "sentry": {
                "level": "ERROR",
                "class": "sentry_sdk.integrations.logging.EventHandler",
            },
        },
        "root": {
            "handlers": ["console"],
            "level": "INFO",
        },
        "loggers": {
            "oauthlib": {
                "handlers": ["console"],
                "level": "DEBUG",
                "propagate": True,
            },
            "src": {
                "handlers": ["console", "file", "sentry"],
                "level": "DEBUG",
                "propagate": True,
            },
        },
    }
    return LOGGING


def api_docs_config() -> dict:
    """ API documentation setup script """
    SPECTACULAR_SETTINGS = {
        'TITLE': 'Appointment app API Documentation',
        'DESCRIPTION': 'Welcome to the Appointment app Backend API reference! It contains a guide on how to integrate our API and '
                       'outlines important information to assist you through the integration process. The API is a REST '
                       'API over HTTP using JSON as the exchange format. It uses standard HTTP response codes, '
                       'authentication, and verbs.',
        'VERSION': '1.0.0',
        'SERVE_INCLUDE_SCHEMA': True,
        'SWAGGER_UI_DIST': 'SIDECAR',
        'SWAGGER_UI_FAVICON_HREF': 'SIDECAR',
        'REDOC_DIST': 'SIDECAR',
    }

    return SPECTACULAR_SETTINGS


def rest_framework_config() -> dict:
    """Rest_framework config"""
    REST_FRAMEWORK = {
        'DEFAULT_AUTHENTICATION_CLASSES': [
            # 'oauth2_provider.contrib.rest_framework.OAuth2Authentication',
            'rest_framework_simplejwt.authentication.JWTStatelessUserAuthentication',
            # 'rest_framework.authentication.BasicAuthentication',
            # 'rest_framework.authentication.SessionAuthentication',
        ],
        'DEFAULT_FILTER_BACKENDS': ['django_filters.rest_framework.DjangoFilterBackend'],
        'DEFAULT_PARSER_CLASSES': [
            'rest_framework.parsers.JSONParser',
        ],
        'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
        'PAGE_SIZE': 30,

        'EXCEPTION_HANDLER': 'util.errors.exceptionhandler.custom_exception_handler',

        'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
        'DEFAULT_VERSIONING_CLASS': 'rest_framework.versioning.URLPathVersioning',
        'DEFAULT_VERSION': 'v1',
        'ALLOWED_VERSIONS': {'v1', 'v1', 'v2'},
        'VERSION_PARAM': 'version',
        'DEFAULT_THROTTLE_CLASSES': (
            'rest_framework.throttling.UserRateThrottle',

        ),
        'DEFAULT_THROTTLE_RATES': {
            # 'loginAttempts': '10/hr',
            'anon': '10/minute',
            'user': '1000/min',
            'premium': '12/minute'
        }
    }

    return REST_FRAMEWORK


def jwt_auth_config(secret_key: str) -> dict:
    SIMPLE_JWT = {
        "ACCESS_TOKEN_LIFETIME": timedelta(days=1),
        "REFRESH_TOKEN_LIFETIME": timedelta(days=2),
        "ROTATE_REFRESH_TOKENS": True,
        "BLACKLIST_AFTER_ROTATION": True,
        "UPDATE_LAST_LOGIN": True,

        "ALGORITHM": "HS256",
        "SIGNING_KEY": secret_key,
        "VERIFYING_KEY": "",
        "AUDIENCE": None,
        "ISSUER": None,
        "JSON_ENCODER": None,
        "JWK_URL": None,
        "LEEWAY": 0,

        "AUTH_HEADER_TYPES": ("Bearer",),
        "AUTH_HEADER_NAME": "HTTP_AUTHORIZATION",
        "USER_ID_FIELD": "id",
        "USER_ID_CLAIM": "user_id",
        "USER_AUTHENTICATION_RULE": "rest_framework_simplejwt.authentication.default_user_authentication_rule",

        "AUTH_TOKEN_CLASSES": ("rest_framework_simplejwt.tokens.AccessToken",),
        "TOKEN_TYPE_CLAIM": "token_type",
        "TOKEN_USER_CLASS": "rest_framework_simplejwt.models.TokenUser",

        "JTI_CLAIM": "jti",

        "SLIDING_TOKEN_REFRESH_EXP_CLAIM": "refresh_exp",
        "SLIDING_TOKEN_LIFETIME": timedelta(minutes=5),
        "SLIDING_TOKEN_REFRESH_LIFETIME": timedelta(hours=2),

        "TOKEN_OBTAIN_SERIALIZER": "account.serializers.CustomTokenObtainSerializer",
        "TOKEN_REFRESH_SERIALIZER": "rest_framework_simplejwt.serializers.TokenRefreshSerializer",
        "TOKEN_VERIFY_SERIALIZER": "rest_framework_simplejwt.serializers.TokenVerifySerializer",
        "TOKEN_BLACKLIST_SERIALIZER": "rest_framework_simplejwt.serializers.TokenBlacklistSerializer",
        "SLIDING_TOKEN_OBTAIN_SERIALIZER": "rest_framework_simplejwt.serializers.TokenObtainSlidingSerializer",
        "SLIDING_TOKEN_REFRESH_SERIALIZER": "rest_framework_simplejwt.serializers.TokenRefreshSlidingSerializer",
    }

    return SIMPLE_JWT
