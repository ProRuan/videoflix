# Standard libraries

# Third-party suppliers
from django.urls import path

# Local imports
from .views import VideoDetailView, VideoListView

app_name = "video_app"

urlpatterns = [
    path("", VideoListView.as_view(), name="video-list"),
    path("<int:id>/", VideoDetailView.as_view(), name="video-detail"),
]
