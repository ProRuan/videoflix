# urls.py
from django.urls import path
from .views import VideoListCreateView, VideoDetailView, VideoProgressListCreate, VideoProgressRetrieveUpdateDelete

urlpatterns = [
    path('', VideoListCreateView.as_view(), name='video-list-create'),
    path('<int:pk>/', VideoDetailView.as_view(), name='video-detail'),

    path('progress/',           VideoProgressListCreate.as_view(),
         name='progress-list-create'),
    path('progress/<int:pk>/',  VideoProgressRetrieveUpdateDelete.as_view(),
         name='progress-detail'),
]


# # video_offer_app/urls.py

# from rest_framework.routers import DefaultRouter
# from .views import VideoProgressViewSet

# router = DefaultRouter()
# router.register(r'progress', VideoProgressViewSet, basename='video-progress')

# urlpatterns = router.urls
