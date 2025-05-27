from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('account.urls')),
    path('teacher/', include('teacher.urls')),
    path('student/', include('student.urls')),
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)