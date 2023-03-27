from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from firac.views import index, output, file_input, manual_input

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', index, name='index'),
    path('file_input/', file_input, name='file_input'),
    path('manual_input/', manual_input, name='manual_input'),
    path('output/', output, name='output'),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
