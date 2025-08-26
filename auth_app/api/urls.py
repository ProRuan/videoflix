# Third-party suppliers
from django.urls import path

# Local imports
from .views import (
    AccountActivationView,
    AccountDeletionView,
    DeregistrationView,
    ForgotPasswordView,
    LoginView,
    LogoutView,
    ReactivateAccountView,
    RegistrationView,
    ResetPasswordView,
    EmailCheckView,
    UserEmailView,
)

urlpatterns = [
    path('registration/', RegistrationView.as_view(), name='registration'),
    path('account-activation/', AccountActivationView.as_view(),
         name='account-activation'),
    path('account-reactivation/', ReactivateAccountView.as_view(),
         name='account-reactivation'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('forgot-password/', ForgotPasswordView.as_view(), name='forgot-password'),
    path('reset-password/', ResetPasswordView.as_view(), name='reset-password'),
    path('email-check/', EmailCheckView.as_view(), name='email-check'),
    path('deregistration/', DeregistrationView.as_view(), name='deregistration'),
    path('account-deletion/', AccountDeletionView.as_view(),
         name='account-deletion'),
    path('user-email/', UserEmailView.as_view(), name='user-email'),

]
