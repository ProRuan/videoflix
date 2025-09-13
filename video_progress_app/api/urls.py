# Third-party suppliers
from django.urls import path

# Local imports
from .views import VideoProgressCreateView, VideoProgressDetailView

app_name = "video_progress_app"

urlpatterns = [
    path("", VideoProgressCreateView.as_view(), name="video-progress-create"),
    path("<int:pk>/", VideoProgressDetailView.as_view(),
         name="video-progress-detail"),
]
