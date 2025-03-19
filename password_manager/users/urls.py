from django.urls import path
from .views import SignupView, LoginView, UserDetailView, add_password
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    path("signup/", SignupView.as_view(), name="signup"),
    path("login/", LoginView.as_view(), name="login"),
    path("me/", UserDetailView.as_view(), name="user-detail"),
    path("passwords/", add_password, name="add_password"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
]
