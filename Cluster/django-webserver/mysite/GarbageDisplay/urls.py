from django.urls import path
from . import views

app_name = 'GarbageDisplay'
urlpatterns = [
    path('', views.home),
    path('update/', views.update),
]
