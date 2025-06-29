from django.db import models
from taggit.managers import TaggableManager
from django.utils.translation import gettext_lazy as _
from django_lifecycle import LifecycleModel, hook, AFTER_CREATE, AFTER_UPDATE, BEFORE_SAVE



class Category(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name


class Course(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class Book(LifecycleModel): 
    STATUS_CHOICES = [
        ('availble', 'availble'),
        ('rental', 'rental'),
        ('sold', 'sold'),
    ]

    course = models.ForeignKey(Course, on_delete=models.PROTECT, null=True, blank=True)
    title = models.CharField(max_length=250)
    author = models.CharField(max_length=250, null=True, blank=True)
    photo_book = models.ImageField(upload_to='photos', null=True, blank=True)
    photo_author = models.ImageField(upload_to='photos', null=True, blank=True)
    pages = models.IntegerField(null=True, blank=True)
    price = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    retal_price_day = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    retal_period = models.IntegerField(null=True, blank=True)
    total_retal = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    active = models.BooleanField(default=False)
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, null=True, blank=True)
    category = models.ForeignKey(Category, on_delete=models.PROTECT, null=True, blank=True)
    tags = TaggableManager()
    published_date = models.DateField(null=True, blank=True)
    status_color = models.CharField(max_length=7, blank=True, help_text="اختر لون الحالة")

    def __str__(self):
        return self.title

    
    @hook(BEFORE_SAVE)
    def calculate_total_retal(self):
        if self.retal_price_day and self.retal_period:
            self.total_retal = self.retal_price_day * self.retal_period

    @hook(AFTER_CREATE)
    def trigger_pdf_generation(self):
        print(f"✅ تم إنشاء الكتاب: {self.title}")
        from .tasks import generate_books_pdf_task 
        generate_books_pdf_task.delay([self.id])  



    @hook(AFTER_UPDATE, when='active', has_changed=True)
    def log_active_change(self):
        if self.active:
            print(f"📗 تم تفعيل الكتاب: {self.title}")
        else:
            print(f"📕 تم إلغاء تفعيل الكتاب: {self.title}")


    @hook(AFTER_UPDATE, when='status', has_changed=True)
    def log_status_change(self):
        print(f"🔄 تم تغيير حالة الكتاب '{self.title}' إلى: {self.status}")
