from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('account.urls')),
    path('teacher/', include('teacher.urls')),
    path('student/', include('student.urls')),
]