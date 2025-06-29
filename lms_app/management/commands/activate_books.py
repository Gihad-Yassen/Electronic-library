from django.core.management.base import BaseCommand
from lms_app.models import Book

class Command(BaseCommand):
    help = 'تفعيل جميع الكتب غير المفعلة'

    def handle(self, *args, **kwargs):
        books_to_activate = Book.objects.filter(active=False)
        count = books_to_activate.count()

        if count == 0:
            self.stdout.write(self.style.WARNING("لا توجد كتب بحاجة للتفعيل."))
        else:
            books_to_activate.update(active=True)
            self.stdout.write(self.style.SUCCESS(f"تم تفعيل {count} كتاب."))
