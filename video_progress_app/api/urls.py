from django.urls import path
from .views import VideoProgressListCreateView, VideoProgressDetailView

urlpatterns = [
    path('', VideoProgressListCreateView.as_view(),
         name='video-progress-list'),
    path('<int:pk>/',
         VideoProgressDetailView.as_view(), name='video-progress-detail'),
]
