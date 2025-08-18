from django.urls import path
from .views import TokenCreationView, TokenCheckView

urlpatterns = [
    path("creation/", TokenCreationView.as_view(), name="token-creation"),
    path("check/", TokenCheckView.as_view(), name="token-check"),
]
