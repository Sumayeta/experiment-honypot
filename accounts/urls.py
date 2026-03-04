from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('signup/', views.signup, name='signup'),
    path("login/", views.login_view, name="login"),   # login_view added
    path("logout/", views.logout_view, name="logout"), # logout_view added
    path('dashboard/', views.dashboard_view, name='dashboard'), 

]