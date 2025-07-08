from django.db.models import Lookup, CharField

class EndsWithZ(Lookup):
    lookup_name = 'endswith_z'

    def as_sql(self, compiler, connection):
        lhs, params = compiler.compile(self.lhs)
        return f"{lhs} LIKE %s", params + ['%z']