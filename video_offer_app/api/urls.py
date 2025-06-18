# urls.py
from django.urls import path
from .views import VideoListCreateView, VideoDetailView

urlpatterns = [
    path('', VideoListCreateView.as_view(), name='video-list-create'),
    path('<int:pk>/', VideoDetailView.as_view(), name='video-detail'),
]
