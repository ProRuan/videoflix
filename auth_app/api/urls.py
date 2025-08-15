# Third-party suppliers
from django.urls import path

# Local imports
from .views import (
    AccountActivationView,
    ForgotPasswordView,
    LoginView,
    RegistrationView,
    ResetPasswordView,
    EmailCheckView,
)

urlpatterns = [
    path('registration/', RegistrationView.as_view(), name='registration'),
    path('account-activation/', AccountActivationView.as_view(),
         name='account-activation'),
    path('login/', LoginView.as_view(), name='login'),
    path('forgot-password/', ForgotPasswordView.as_view(), name='forgot-password'),
    path('reset-password/', ResetPasswordView.as_view(), name='reset-password'),
    path('email-check/', EmailCheckView.as_view(), name='email-check'),
]
