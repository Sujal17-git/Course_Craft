from django.urls import path
from . import views

app_name = 'teacher'

urlpatterns = [
    path('dashboard/', views.dashboard, name='dashboard'),
    path('create-class/', views.create_class, name='create_class'),
    path('manage-profile/', views.manage_profile, name='manage_profile'),
    path('class/<int:class_id>/', views.class_detail, name='class_detail'),

]