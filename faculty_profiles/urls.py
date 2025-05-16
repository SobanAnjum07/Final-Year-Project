from django.urls import path
from . import views

urlpatterns = [
    path('', views.faculty_dashboard, name='faculty_dashboard'),
    path('upload/', views.upload_lecture, name='upload_lecture'),
    path('edit/<int:lecture_id>/', views.edit_lecture, name='edit_lecture'),
    path('delete/<int:lecture_id>/', views.delete_lecture, name='delete_lecture'),
    path('create/', views.create_faculty_profile, name='create_faculty_profile'),
    path('subjects/', views.manage_subjects, name='manage_subjects'),
    path('directory/', views.faculty_directory, name='faculty_directory'),
    path('directory/<int:faculty_id>/', views.faculty_detail, name='faculty_detail'),
]