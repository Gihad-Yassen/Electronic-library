from django.urls import path, include
from . import views
from rest_framework.routers import DefaultRouter
from .views import BookViewSet


router = DefaultRouter()
router.register(r'books', BookViewSet, basename='book')


urlpatterns = [
    
    path('', views.index, name='index'),
    path('books/', views.books, name='books'),
    path('update/<int:id>', views.update, name='update'),
    path('delete/<int:id>', views.delete, name='delete'),
    path('api/', include(router.urls)),
    path('course-autocomplete/', views.course_autocomplete, name='course-autocomplete'),
]
