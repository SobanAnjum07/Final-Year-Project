
from django.urls import path, include
from . import views
urlpatterns = [

    path('login/', views.login_view, name='login'),
    path('signup/', views.signup_view, name='signup'),
    path('', views.home_page, name='home'),
    path('logout/', views.logout_view, name='logout'),
   
]