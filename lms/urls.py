from django.contrib import admin
from django.urls import include, path
from django.conf import settings
from django.conf.urls.static import static
import debug_toolbar
from django.conf.urls.i18n import i18n_patterns

urlpatterns = [
    path('i18n/', include('django.conf.urls.i18n')),
    path('__debug__/', include(debug_toolbar.urls)),
]

urlpatterns += i18n_patterns(
    path('admin/', admin.site.urls),
    path('', include('lms_app.urls')),
    path('tinymce/', include('tinymce.urls')),
    path("chaining/", include("smart_selects.urls")),
)

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
