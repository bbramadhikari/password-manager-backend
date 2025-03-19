from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import check_password
from rest_framework import status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.decorators import api_view, permission_classes
from .serializers import UserSignupSerializer, UserSerializer, PasswordSerializer
from .models import Password

User = get_user_model()  # Get custom user model


# ✅ Signup API with Face Image Processing & Secure Storage
class SignupView(APIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = UserSignupSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)

        if serializer.is_valid():
            validated_data = serializer.validated_data
            validated_data["email"] = validated_data["email"].strip().lower()

            if User.objects.filter(email=validated_data["email"]).exists():
                return Response(
                    {"error": "Email already registered!"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            user = serializer.save()

            face_image = request.data.get("face_image")
            if face_image:
                try:
                    user.save_face_image(face_image)  # ✅ Securely store face image
                except Exception as e:
                    print(f"⚠️ Face image processing error: {e}")
                    return Response(
                        {"error": "Invalid face image data."},
                        status=status.HTTP_400_BAD_REQUEST,
                    )

            refresh = RefreshToken.for_user(user)

            return Response(
                {
                    "message": "Signup successful!",
                    "token": str(refresh.access_token),
                    "refresh": str(refresh),
                    "token_expires_in": refresh.access_token.payload["exp"],
                    "user": {
                        "id": user.id,
                        "username": user.username,
                        "email": user.email,
                    },
                },
                status=status.HTTP_201_CREATED,
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# ✅ Login API (Authenticates User Securely)
class LoginView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        email = request.data.get("email", "").strip().lower()  # ✅ Convert to lowercase
        password = request.data.get("password")

        if not email or not password:
            return Response(
                {"error": "Email and Password are required!"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            user = User.objects.get(
                email__iexact=email
            )  # Case-insensitive email lookup
        except User.DoesNotExist:
            return Response(
                {"error": "Invalid credentials!"}, status=status.HTTP_400_BAD_REQUEST
            )

        if not check_password(password, user.password):  # Verify the hashed password
            return Response(
                {"error": "Invalid credentials!"}, status=status.HTTP_400_BAD_REQUEST
            )

        # Generate JWT Token
        refresh = RefreshToken.for_user(user)

        return Response(
            {
                "message": "Login successful!",
                "token": str(refresh.access_token),
                "refresh": str(refresh),
                "token_expires_in": refresh.access_token.payload["exp"],
                "user": {
                    "id": user.id,
                    "username": user.username,
                    "email": user.email,
                },
            },
            status=status.HTTP_200_OK,
        )


# ✅ User Profile API (Fetches Logged-in User Details)
class UserDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        serializer = UserSerializer(user)
        return Response(serializer.data)


# ✅ Add Password API (Allow authenticated users to add a password)
@api_view(["POST"])
@permission_classes(
    [IsAuthenticated]
)  # Ensure only authenticated users can add passwords
def add_password(request):
    """Allow authenticated users to add a password."""
    serializer = PasswordSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save(user=request.user)  # Save password for authenticated user
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# ✅ Root API (Provide basic API info)
@api_view(["GET"])
@permission_classes([AllowAny])  # No authentication required for this view
def api_root(request):
    return Response(
        {
            "message": "Welcome to the API!",
            "endpoints": {
                "users": "/api/users/",
                "signup": "/api/signup/",
                "login": "/api/login/",
                "me": "/api/me/",
                "passwords": "/api/passwords/",
            },
        }
    )
