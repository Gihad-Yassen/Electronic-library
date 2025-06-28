from django.contrib import admin, messages
from django import forms
from django.forms import TextInput
from django.db import models
from tinymce.widgets import TinyMCE
from .models import Book, Category, Course
from django.utils.translation import gettext_lazy as _
from django.utils.html import format_html
from django.core import serializers
from django.http import HttpResponse
from django.core.exceptions import ValidationError

# 📌 استيراد مهمة Celery
from .tasks import generate_books_pdf_task

# ✅ إجراء تصدير JSON
def export_as_json(modeladmin, request, queryset):
    response = HttpResponse(content_type="application/json")
    response['Content-Disposition'] = 'attachment; filename=export.json'
    serializers.serialize("json", queryset, stream=response)
    messages.success(request, "تم تصدير البيانات بنجاح.")
    return response

# ✅ إجراء توليد PDF في الخلفية
@admin.action(description="توليد ملفات PDF للكتب (خلفية)")
def generate_pdf_books_background(modeladmin, request, queryset):
    book_ids = list(queryset.values_list('id', flat=True))
    generate_books_pdf_task.delay(book_ids)
    modeladmin.message_user(request, "🚀 تم إرسال المهمة إلى الخلفية بنجاح عبر Celery.", messages.SUCCESS)

# ====== النماذج Forms ======
class BookForm(forms.ModelForm):
    ACTIVE_CHOICES = (
        (True, "مفعل"),
        (False, "غير مفعل"),
    )
    active = forms.ChoiceField(
        choices=ACTIVE_CHOICES,
        widget=forms.RadioSelect,
        label='الحالة'
    )
    class Meta:
        model = Book
        fields = '__all__'
        widgets = {
            'title': TextInput(attrs={'size': 60}),
            'author': TextInput(attrs={'size': 60}),
            'status_color': forms.TextInput(attrs={'type': 'color'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        published_date = cleaned_data.get('published_date')
        retal_period = cleaned_data.get('retal_period')
        if retal_period and not published_date:
            raise ValidationError("يجب تحديد تاريخ النشر إذا تم تحديد فترة التأجير.")
        if retal_period is not None and retal_period <= 0:
            self.add_error('retal_period', "فترة التأجير يجب أن تكون أكبر من صفر.")
        return cleaned_data


class CourseForm(forms.ModelForm):
    description = forms.CharField(widget=TinyMCE(attrs={'cols': 80, 'rows': 30}))
    class Meta:
        model = Course
        fields = '__all__'


class BookInline(admin.StackedInline):
    model = Book
    extra = 2
    can_delete = True
    readonly_fields = ['price']
    fields = ['title', 'author', 'status', 'price']
    show_change_link = True


class PriceRangeFilter(admin.SimpleListFilter):
    title = _('السعر')
    parameter_name = 'price_range'

    def lookups(self, request, model_admin):
        return [
            ('above_150', _('أعلى من 150')),
            ('below_150', _('أقل من 150')),
        ]

    def queryset(self, request, queryset):
        if self.value() == 'above_150':
            return queryset.filter(price__isnull=False, price__gt=150)
        if self.value() == 'below_150':
            return queryset.filter(price__isnull=False, price__lt=150)
        return queryset


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    form = CourseForm
    inlines = [BookInline]
    list_display = ['name', 'description', 'renderd_description']
    search_fields = ['name', 'description']
    list_editable = ['description']

    def get_sortable_by(self, request):
        return {'name'}

    def get_inline_instances(self, request, obj=None):
        if not request.user.is_superuser:
            return []
        return super().get_inline_instances(request, obj)

    @admin.display(description=_("الوصف"))
    def renderd_description(self, obj):
        return format_html(obj.description)

    def has_add_permission(self, request, obj=None):
        return request.user.is_superuser

    def has_change_permission(self, request, obj=None):
        return request.user.is_superuser

    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        messages.success(request, f"تم حفظ الدورة: {obj.name}")


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    form = BookForm
    date_hierarchy = 'published_date'

    formfield_overrides = {
        models.CharField: {'widget': TextInput(attrs={'size': 60})}
    }

    list_display = [
        'title', 'author', 'category', 'status', 'course',
        'is_active_display', 'status_color'
    ]
    list_display_links = ['title', 'author']
    list_filter = ['category', 'status', 'course', 'active', PriceRangeFilter]
    search_fields = ['title', 'author', 'course__name']
    autocomplete_fields = ['course', 'category']
    actions = ['activate_books', 'deactivate_books', export_as_json, generate_pdf_books_background]
    ordering = ['-active', 'category', '-id']
    readonly_fields = ['category']
    save_as = True
    save_as_continue = True
    save_on_top = True
    list_max_show_all = 100
    list_per_page = 2
    search_help_text = "ابحث بالعنوان أو اسم المؤلف أو اسم الدورة"
    empty_value_display = ' لا توجد قيمة '
    actions_on_top = True
    actions_on_bottom = True
    show_full_result_count = True
    list_select_related = ['category', 'course']

    def get_queryset(self, request):
        qs = super().get_queryset(request).prefetch_related('tags')
        if request.user.is_superuser:
            return qs
        return qs.filter(owner=request.user) if hasattr(Book, 'owner') else qs

    @admin.display(ordering='active', description='الحالة', boolean=True)
    def is_active_display(self, obj):
        return obj.active

    @admin.action(description="تفعيل الكتب")
    def activate_books(self, request, queryset):
        updated = queryset.update(active=True)
        messages.success(request, f"تم تفعيل {updated} كتاب بنجاح.")

    @admin.action(description="إلغاء تفعيل الكتب")
    def deactivate_books(self, request, queryset):
        updated = queryset.update(active=False)
        messages.warning(request, f"{updated} كتاب تم إلغاء تفعيله.")

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        if change:
            messages.info(request, f"تم تحديث الكتاب: {obj.title}")
        else:
            messages.success(request, f"تمت إضافة الكتاب: {obj.title}")

    def has_add_permission(self, request, obj=None):
        return request.user.is_superuser or request.user.groups.filter(name='Book Editors').exists()

    def has_change_permission(self, request, obj=None):
        if obj is None:
            return True
        if hasattr(obj, 'owner'):
            return obj.owner == request.user or request.user.is_superuser
        return request.user.is_superuser

    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser

    fieldsets = (
        ('معلومات الكتاب', {
            'fields': ('title', 'author', 'category', 'tags'),
            'description': 'معلومات أساسية عن الكتاب.',
            'classes': ('wide',),
        }),
        ('معلومات النشر والدورة', {
            'fields': ('status', 'status_color', 'course', 'price', 'retal_period', 'published_date'),
            'description': 'تفاصيل حول الدورة المرتبطة وسعر الكتاب.',
            'classes': ('collapse',),
        }),
        ('الحالة', {
            'fields': ('active',),
            'description': 'هل الكتاب مفعل أم لا؟',
        }),
    )


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    search_fields = ['name']
