# Third-party suppliers
from django.urls import path

# Local imports
from .views import (
    ForgotPasswordView, LoginView,
    RegistrationView, ResetPasswordView
)

urlpatterns = [
    path('registration/', RegistrationView.as_view(), name='registration'),
    path('login/', LoginView.as_view(), name='login'),
    path('forgot-password/', ForgotPasswordView.as_view(), name='forgot-password'),
    path('reset-password/', ResetPasswordView.as_view(), name='reset-password'),
]
