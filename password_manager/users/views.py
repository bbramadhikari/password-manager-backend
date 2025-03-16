from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import check_password
from rest_framework import status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import UserSignupSerializer, UserSerializer
from rest_framework.permissions import IsAuthenticated

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

        # Debugging: Log user search
        print(f"🔹 Checking for user with email: {email}")

        try:
            user = User.objects.get(
                email__iexact=email
            )  # ✅ Case-insensitive email lookup
        except User.DoesNotExist:
            print(f"❌ Login Failed: User with email '{email}' not found.")
            return Response(
                {"error": "Invalid credentials!"}, status=status.HTTP_400_BAD_REQUEST
            )

        print(f"✅ User Found: '{user.email}' (ID: {user.id})")

        # Verify hashed password
        if not check_password(password, user.password):
            print(f"❌ Login Failed: Incorrect password for '{user.email}'")
            return Response(
                {"error": "Invalid credentials!"}, status=status.HTTP_400_BAD_REQUEST
            )

        print("✅ Password verified successfully!")

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
        print(f"📡 API Called by: {user}")  # ✅ Log user request
        print(f"🔹 Authenticated: {user.is_authenticated}")

        if not user.is_authenticated:
            return Response(
                {"error": "Unauthorized"}, status=status.HTTP_401_UNAUTHORIZED
            )

        serializer = UserSerializer(user)
        return Response(serializer.data)
