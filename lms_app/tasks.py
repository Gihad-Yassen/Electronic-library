from celery import shared_task
from .models import Book

@shared_task
def generate_books_pdf_task(book_ids):
    for book_id in book_ids:
        try:
            book = Book.objects.get(id=book_id)
            # مثال مبسط: طباعة في الكونسل فقط
            print(f"🔧 Generating PDF for book: {book.title}")
            # يمكنك هنا توليد ملف PDF فعلي وتخزينه أو إرساله بالبريد
        except Book.DoesNotExist:
            continue
