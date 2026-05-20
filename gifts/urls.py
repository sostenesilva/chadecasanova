from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('presentes/<int:pk>/reservar/',  views.reserve_gift, name='reserve_gift'),
    path('presentes/<int:pk>/confirmar/', views.confirm_gift,  name='confirm_gift'),
    path('presentes/<int:pk>/cancelar/',  views.cancel_gift,   name='cancel_gift'),
]
