from django.apps import AppConfig
from django.db.models import CharField
from .lookups import EndsWithZ


class LmsAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'lms_app'



class LmsAppConfig(AppConfig):
    name = 'lms_app'

    def ready(self):
        CharField.register_lookup(EndsWithZ)