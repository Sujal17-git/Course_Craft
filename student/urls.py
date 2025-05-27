# student/urls.py
from django.urls import path
from . import views

app_name = 'student'

urlpatterns = [
    path('dashboard/', views.dashboard, name='dashboard'),
    path('manage-profile/', views.manage_profile, name='manage_profile'),
    path('class/<int:class_id>/', views.view_class, name='view_class'),
    path('class/<int:class_id>/section/<int:section_id>/', views.section_detail, name='section_detail'),
    path('class/<int:class_id>/section/<int:section_id>/resources/', views.view_resources, name='view_resources'),
    path('class/<int:class_id>/leave/', views.leave_class, name='leave_class'),
]