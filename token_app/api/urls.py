# Standard libraries

# Third-party suppliers
from django.urls import path

# Local imports
from token_app.api.views import TokenCheckView

app_name = "token_app"

urlpatterns = [
    path("check/", TokenCheckView.as_view(), name="check"),
]
