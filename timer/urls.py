from django.urls import path
from . import views

app_name = 'exercise'

urlpatterns = [
    path('start-timer/', views.start_timer, name='start_timer'),
    path('current-timer/', views.current_timer, name='current_timer'),
]
