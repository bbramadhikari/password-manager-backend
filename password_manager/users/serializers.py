from rest_framework import serializers
from .models import CustomUser


class UserSignupSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    face_image = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = CustomUser
        fields = ["username", "phone", "email", "password", "face_image"]

    def validate_email(self, value):
        """Ensure email is always stored in lowercase."""
        return value.strip().lower()

    def create(self, validated_data):
        password = validated_data.pop("password", None)
        face_image = validated_data.pop("face_image", None)

        if not password:
            raise serializers.ValidationError({"password": "Password is required."})

        # Ensure email is lowercase
        validated_data["email"] = validated_data["email"].strip().lower()

        user = CustomUser(**validated_data)
        user.set_password(password)  # Hash password
        user.save()

        if face_image:
            user.save_face_image(face_image)

        return user


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ["id", "username", "email"]
