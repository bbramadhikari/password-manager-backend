from datetime import datetime
from django.contrib.auth.models import AbstractUser
from django.db import models
import cv2
import numpy as np
import base64
import hashlib
import re
from django.contrib.auth.hashers import make_password
import pyotp  # For OTP generation


# Load Haar Cascade for face detection
CASCADE_PATH = cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
face_cascade = cv2.CascadeClassifier(CASCADE_PATH)


# Save Face Image
def image_upload_to(instance, filename):
    # Create a custom filename with the current date and time
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    lowercase_filename = filename.lower()
    return f"images/{timestamp}_{lowercase_filename}"


class Image(models.Model):
    user = models.ForeignKey(
        "CustomUser",
        on_delete=models.CASCADE,
        related_name="image",
    )
    image = models.ImageField(upload_to=image_upload_to)  # Store the actual image
    image_url = models.CharField(
        max_length=255, blank=True, null=True
    )  # Store the URL (optional)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = "users"

    def save(self, *args, **kwargs):
        if not self.image_url and self.image:
            self.image_url = self.image.url  # Set image_url to the image URL
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Image {self.id}"


class CustomUser(AbstractUser):
    phone = models.CharField(max_length=15, unique=True)
    face_image = models.OneToOneField(
        "Image",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="user_face_image",
    )
    otp_secret = models.CharField(max_length=255, blank=True, null=True)
    otp_generated = models.CharField(max_length=255, blank=True, null=True)

    # OTP related methods
    def generate_otp_secret(self):
        """Generate a secret key for OTP if not already generated."""
        if not self.otp_secret:
            totp = pyotp.random_base32()  # Generate a new secret key for OTP
            self.otp_secret = totp
            self.save()
        return self.otp_secret

    def get_otp(self):
        """Generate OTP using the stored OTP secret."""
        totp = pyotp.TOTP(self.otp_secret)
        return totp.now()  # Get current OTP

    def verify_otp(self, otp):
        """Verify if the OTP provided is correct."""
        totp = pyotp.TOTP(self.otp_secret)
        return totp.verify(otp)  # Returns True if OTP is valid, False otherwise


class Password(models.Model):
    user = models.ForeignKey(
        "CustomUser", on_delete=models.CASCADE, related_name="passwords"
    )
    domain_name = models.CharField(max_length=255)
    password = models.CharField(max_length=255)  # Store the hashed password
    link = models.URLField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = "users"

    def __str__(self):
        return self.domain_name

    def save(self, *args, **kwargs):
        """Override save method to hash the password before saving."""
        # if self.password:
        #     self.password = make_password(self.password)  # Hash the password
        super().save(*args, **kwargs)
