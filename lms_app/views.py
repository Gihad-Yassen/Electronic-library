from django.shortcuts import render , redirect , get_object_or_404
from .models import * 
from .forms import BookForm ,CategoryForm
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Book
from .serializers import BookSerializer
from django.db.models import Count



def index(request):
    if request.method == 'POST':
        add_book = BookForm(request.POST, request.FILES)
        if add_book.is_valid(): 
            add_book.save()

        add_category = CategoryForm(request.POST)
        if add_category.is_valid():
            add_category.save()
    context = {
        'categories' : Category.objects.all(),
        'books': Book.objects.all(),
        'form': BookForm(),
        'formcat': CategoryForm(),
        'allbooks': Book.objects.filter(active=True).count(),
        'allsold': Book.objects.filter(status='sold').count(),
        'allrental': Book.objects.filter(status='rental').count(),
        'allavailbe': Book.objects.filter(status='availble').count(),

    }
    return render(request,'pages/index.html' , context)


def books(request):
    context = {
        'categories' : Category.objects.all(),
        'books': Book.objects.all(),
        'formcat': CategoryForm(),

}
    return render(request,'pages/books.html', context)

def update(request, id):
    book_id = Book.objects.get(id=id)
    if request.method == 'POST':
        book_save = BookForm(request.POST, request.FILES, instance=book_id)
        if book_save.is_valid():
            book_save.save()
            return redirect('/')
    else:
        book_save =  BookForm(instance=book_id)
    context = {
        'form':book_save,
    }
    return render(request, 'pages/update.html',context)



def delete(request, id):
    book_delete = get_object_or_404(Book, id=id)
    if request.method == 'POST':
        book_delete.delete()
        return redirect('/')
    return render(request, 'pages/delete.html')


class BookViewSet(viewsets.ModelViewSet):
    queryset = Book.objects.all()
    serializer_class = BookSerializer

    @action(detail=False, methods=['get'])
    def stats(self, request):
        total_books = Book.objects.count()
        by_category = Book.objects.values('category').annotate(count=Count('id'))
        return Response({
            'total_books': total_books,
            'books_by_category': list(by_category),
        })
