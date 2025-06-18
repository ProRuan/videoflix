# urls.py
from django.urls import path
from .views import VideoListCreateView

urlpatterns = [
    path('', VideoListCreateView.as_view(), name='video-list-create'),
]
