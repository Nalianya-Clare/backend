from storages.backends.s3boto3 import S3Boto3Storage


class StaticStorage(S3Boto3Storage):
    location = 'static'
    default_acl = 'public-read'

    def _clean_name(self, name):
        return name

    def _normalize_name(self, name):
        if not name.endswith('/'):
            name += "/"

        name = self.location + name
        return name


class PublicMediaStorage(S3Boto3Storage):
    location = 'media'
    default_acl = 'public-read'
    file_overwrite = True

    def _clean_name(self, name):
        return name

    def _normalize_name(self, name):
        if not name.endswith('/'):
            name += "/"

        name = self.location + name
        return name


class PrivateMediaStorage(S3Boto3Storage):
    location = 'private'
    default_acl = 'private'
    file_overwrite = False
    custom_domain = False
