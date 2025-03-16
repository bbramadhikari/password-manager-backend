from django.urls import path
from .views import SignupView, LoginView, UserDetailView  # Import UserDetailView

urlpatterns = [
    path("signup/", SignupView.as_view(), name="signup"),
    path("login/", LoginView.as_view(), name="login"),
    path("me/", UserDetailView.as_view(), name="user-detail"),  # Get user info
]
