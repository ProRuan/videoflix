# Third-party suppliers
from django.urls import path

# Local imports
from .views import VideoProgressDetailView, VideoProgressListCreateView

urlpatterns = [
    path(
        '', VideoProgressListCreateView.as_view(),
        name='video-progress-list'
    ),
    path(
        '<int:pk>/', VideoProgressDetailView.as_view(),
        name='video-progress-detail'
    ),
]
