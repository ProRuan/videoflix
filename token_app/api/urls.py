# Third-party suppliers
from django.urls import path

# Local imports
from token_app.api.views import ActivationTokenCheckView, TokenCheckView

app_name = "token_app"

urlpatterns = [
    path("activation-token-check/", ActivationTokenCheckView.as_view(),
         name="activation_token_check"),
    path("token-check/", TokenCheckView.as_view(), name="token_check"),
]
