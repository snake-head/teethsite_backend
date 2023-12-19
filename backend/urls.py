from django.urls import path
from . import views

urlpatterns = [
    path('generate_root/', views.generate_root, name='generate_root'),
]
