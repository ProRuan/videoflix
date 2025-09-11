# Third-party suppliers
from django.urls import path

# Local imports
from auth_app.api.views import (
    AccountActivationView,
    ActivationTokenCheckView,
    AccountDeletionView,
    AccountReactivationView,
    DeregistrationView,
    EmailCheckView,
    LoginView,
    LogoutView,
    PasswordResetView,
    PasswordUpdateView,
    RegistrationView,
    TokenCheckView,
)

app_name = "auth_app"

urlpatterns = [
    path("registration/", RegistrationView.as_view(), name="registration"),
    path(
        "activation-token-check/",
        ActivationTokenCheckView.as_view(),
        name="activation_token_check",
    ),
    path(
        "account-activation/",
        AccountActivationView.as_view(),
        name="account_activation",
    ),
    path(
        "account-reactivation/",
        AccountReactivationView.as_view(),
        name="account_reactivation",
    ),
    path("email-check/", EmailCheckView.as_view(), name="email_check"),
    path("login/", LoginView.as_view(), name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("password-reset/", PasswordResetView.as_view(), name="password_reset"),
    path("password-update/", PasswordUpdateView.as_view(),
         name="password_update"),
    path("deregistration/", DeregistrationView.as_view(),
         name="deregistration"),
    path(
        "account-deletion/",
        AccountDeletionView.as_view(),
        name="account_deletion",
    ),
    path("token-check/", TokenCheckView.as_view(), name="token_check"),
]
