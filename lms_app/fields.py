from django.db import models

class LowercaseCharField(models.CharField):
    def get_prep_value(self, value):
        value = super().get_prep_value(value)
        return value.lower() if isinstance(value, str) else value