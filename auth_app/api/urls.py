# Standard libraries

# Third-party suppliers
from django.urls import path

# Local imports
from auth_app.api.views import (
    AccountActivationView,
    AccountDeletionView,
    AccountReactivationView,
    DeregistrationView,
    EmailCheckView,
    LoginView,
    LogoutView,
    PasswordResetRequestView,
    PasswordUpdateView,
    RegistrationView
)

app_name = "auth_app"

urlpatterns = [
    path("registration/", RegistrationView.as_view(), name="registration"),
    path("account-activation/", AccountActivationView.as_view(),
         name="account-activation"),
    path("account-reactivation/", AccountReactivationView.as_view(),
         name="account-reactivation"),
    path("email-check/", EmailCheckView.as_view(), name="email-check"),
    path("login/", LoginView.as_view(), name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("password-reset/", PasswordResetRequestView.as_view(),
         name="password-reset"),
    path("password-update/", PasswordUpdateView.as_view(),
         name="password-update"),
    path("deregistration/", DeregistrationView.as_view(), name="deregistration"),
    path("account-deletion/", AccountDeletionView.as_view(),
         name="account-deletion"),

]
