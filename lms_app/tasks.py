from celery import shared_task
from .models import Book

@shared_task
def generate_books_pdf_task(book_ids):
    for book_id in book_ids:
        try:
            book = Book.objects.get(id=book_id)
        
            print(f"🔧 Generating PDF for book: {book.title}")
        except Book.DoesNotExist:
            continue
