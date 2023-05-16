from django.urls import path
from . import views

urlpatterns = [
    path('process_polydata/', views.process_polydata, name='process_polydata'),
]
