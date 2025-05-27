# teacher/urls.py
from django.urls import path
from . import views

app_name = 'teacher'

urlpatterns = [
    path('dashboard/', views.dashboard, name='dashboard'),
    path('create-class/', views.create_class, name='create_class'),
    path('manage-profile/', views.manage_profile, name='manage_profile'),
    path('class/<int:class_id>/', views.class_detail, name='class_detail'),
    path('class/<int:class_id>/add-section/', views.add_section, name='add_section'),
    path('class/<int:class_id>/section/<int:section_id>/', views.section_detail, name='section_detail'),
    path('class/<int:class_id>/students/', views.get_students, name='get_students'),
    path('class/<int:class_id>/remove-student/', views.remove_student, name='remove_student'),
    path('class/<int:class_id>/delete/', views.delete_class, name='delete_class'),
    path('class/<int:class_id>/section/<int:section_id>/manage-resource/', views.manage_resource, name='manage_resource'),
    path('class/<int:class_id>/section/<int:section_id>/delete-resource/<int:resource_id>/', views.delete_resource, name='delete_resource'),
]