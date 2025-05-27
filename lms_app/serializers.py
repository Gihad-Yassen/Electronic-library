from rest_framework import serializers
from .models import Book

class BookSerializer(serializers.ModelSerializer):
    category_name = serializers.StringRelatedField(source='category', read_only=True)

    class Meta:
        model = Book
        fields = '__all__'
