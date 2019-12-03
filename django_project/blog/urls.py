
from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name="blog-home"),
    path('home', views.home, name="blog-about"),
    path('translation', views.translation, name="blog-about"),
    path('actionUrl', views.button_click),
    path('detial_click', views.detial_click, name='detial_click'),
    path('downloadexcel', views.download_excel_data),
    path('dtranslation', views.download_excel_transcription),
    path('ddictionary', views.download_excel_data),
]
