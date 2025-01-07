from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('signup/', views.signup_view, name='signup'),
    path('', views.home_page, name='home'),
    path('logout/', views.logout_view, name='logout'),
    path('faculty_profile/', views.create_or_edit_faculty_profile, name='create_or_edit_faculty_profile'),  # Create or edit
    path('faculty_profile/<int:id>/', views.faculty_profile_view, name='faculty_profile_view'),  # View profile
    path('faculty/profiles/', views.list_faculty_profiles, name='faculty_profiles_list'),
]
