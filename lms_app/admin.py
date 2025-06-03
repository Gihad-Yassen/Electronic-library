from django.contrib import admin
from django import forms 
from django.forms import TextInput, Textarea    
from django.db import models
from tinymce.widgets import TinyMCE
from .models import Book, Category, Course
from django.utils.translation import gettext_lazy as _
from django.utils.html import format_html
from taggit.models import Tag


class BookForm(forms.ModelForm):
    ACTIVE_CHOICES = (
        (True, "مفعل"),
        (False, "غير مفعل"),
    )

    active = forms.ChoiceField(choices=ACTIVE_CHOICES, label='ACTIVE')
    
    active = forms.ChoiceField(
        choices=ACTIVE_CHOICES,
        widget=forms.RadioSelect, 
        label='الحالة'
    )

    class Meta:
        model = Book
        fields = ['title', 'category', 'course', 'active']
        
class CourseForm(forms.ModelForm):
    description = forms.CharField(widget=TinyMCE(attrs={'cols': 80, 'rows': 30}))

    class Meta:
        model = Course
        fields = '__all__'


# عرض الكتب داخل الكورس بشكل مضغوط
class BookInline(admin.TabularInline): 
    model = Book
    extra = 1  
    fields = ['title', 'author', 'status', 'price']  
    show_change_link = True 


# لوحة تحكم الكورسات
class CourseAdmin(admin.ModelAdmin):
    form = CourseForm
    inlines = [BookInline]
    list_display = ['name','description', 'renderd_description']
    search_fields = ['name', 'description']
    list_editable = ['description']

    def get_sortable_by(self, request):
        # منع الترتيب على   'description'
        return {'name'}

    def get_inline_instances(self, request, obj=None):
        if not request.user.is_superuser:
           return []  # لا تعرض الكتب إذا لم يكن المستخدم مشرفًا
        return super().get_inline_instances(request, obj)
    
    @admin.display(description=_("description"))
    def renderd_description(self,obj):
        return format_html(obj.description)
        
    def get_formsets_with_inlines(self, request, obj=None):
        for inline in self.get_inline_instances(request, obj):
            # لا تعرض BookInline في صفحة الإضافة
            if not isinstance(inline, BookInline) or obj is not None:
                yield inline.get_formset(request, obj), inline

# لوحة تحكم الكتب
class BookAdmin(admin.ModelAdmin):
    
    formfield_overrides = {
        models.CharField: {
            'widget': TextInput(attrs={'size': 60})     
        },
      
    }
    form = BookForm
    list_display = ['title', 'author', 'category', 'status', 'course', 'is_active_display']
    search_help_text = "ابحث بالعنوان أو اسم المؤلف أو اسم الدورة"
    list_display_links = ['title', 'author'] 
    list_max_show_all = 100
    list_per_page = 2
    list_select_related = ['category', 'course',]
    search_fields = ['title', 'author', 'course__name']
    autocomplete_fields = ['course', 'category']
    list_filter = ['category', 'status', 'course', 'active']
    empty_value_display = ' لا توجد قيمة '
    actions = ['activate_books', 'deactivate_books']
    actions_on_top = True     
    actions_on_bottom = True 
    filter_horizontal =()
    ordering = ['-active', 'category', '-id']   
    readonly_fields = ['category']
    save_as = True
    save_as_continue = True
    save_on_top = True 
    show_full_result_count = True
    
    

    @admin.display(ordering='active', description='الحالة', boolean=True)
    def is_active_display(self, obj):
        return obj.active

    def get_sortable_by(self, request):
        return {*self.get_list_display(request)} - {'status'}

    def activate_books(self, request, queryset):
        updated = queryset.update(active=True)
        self.message_user(request, f"تم تفعيل {updated} كتاب بنجاح.")

    @admin.action(description="  deactivate books")
    def deactivate_books(self, request, queryset):
        updated = queryset.update(active=False)
        self.message_user(request, f"{updated} كتاب تم إلغاء تفعيله.")


    fieldsets = (
        ('معلومات الكتاب', {
            'fields': ('title', 'author', 'category', 'tags'),
            'description': 'معلومات أساسية عن الكتاب.',
            'classes': ('wide',),
        }),
        ('معلومات النشر والدورة', {
            'fields': ('status', 'course', 'price'),
            'description': 'تفاصيل حول الدورة المرتبطة وسعر الكتاب.',
            'classes': ('collapse',),
        }),
        ('الحالة', {
            'fields': ('active',),
            'description': 'هل الكتاب مفعل أم لا؟',
        }),
    )

           


# لوحة تحكم الفئات
class CategoryAdmin(admin.ModelAdmin):
    search_fields = ['name']


# تسجيل النماذج في لوحة الإدارة
admin.site.register(Book, BookAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Course, CourseAdmin)
   


