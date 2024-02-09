from django.urls import path
from . import views

urlpatterns = [
    path('generate_root/', views.generate_root, name='generate_root'),
    path('generate_root_json/', views.generate_root_json, name='generate_root_json'),
]
