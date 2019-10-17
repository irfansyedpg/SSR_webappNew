
from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name="blog-home"),
    path('home', views.home, name="blog-about"),
    path('translation', views.translation, name="blog-about"),
    path('actionUrl', views.button_click),
]
