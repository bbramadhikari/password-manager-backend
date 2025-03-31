from django.urls import path

from .views import (
    SignupView,
    LoginView,
    UserDetailView,
    VerifyOtpView,
    SendOtpEmailView,
    AddPasswordView,
    ImageUploadView,
    ImageListView,
    VerifyFaceId,
)
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    path("signup/", SignupView.as_view(), name="signup"),
    path("login/", LoginView.as_view(), name="login"),
    path("me/", UserDetailView.as_view(), name="user-detail"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("verify-otp/", VerifyOtpView.as_view(), name="verify_otp"),
    path("send-otp-email/", SendOtpEmailView.as_view(), name="send_otp_email"),
    path("add_password/", AddPasswordView.as_view(), name="add_password"),
    path("image-upload/", ImageUploadView.as_view(), name="image_upload"),
    path("image/", ImageListView.as_view(), name="view_image"),
    path("verify-face-id/", VerifyFaceId.as_view(), name="verify_face_id"),
]
