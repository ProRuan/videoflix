# Third-party suppliers
from django.urls import path

# Local imports
from .views import VideoDetailView, VideoListView


urlpatterns = [
    path('', VideoListView.as_view(), name='video-list'),
    path('<int:pk>/', VideoDetailView.as_view(), name='video-detail'),
]
