from django.contrib.auth.models import AbstractUser
from django.db import models
import cv2
import numpy as np
import base64
import hashlib
import re
from django.contrib.auth.hashers import make_password


# Load Haar Cascade for face detection
CASCADE_PATH = cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
face_cascade = cv2.CascadeClassifier(CASCADE_PATH)


class CustomUser(AbstractUser):
    phone = models.CharField(max_length=15, unique=True)
    face_image = models.ImageField(upload_to="faces/", null=True, blank=True)

    def process_face_image(self, image_data):
        """Process the face image to extract and save the face using OpenCV."""
        try:
            print(f"🔹 Received face image data: {image_data[:50]}...")

            # Ensure the Base64 string has correct padding
            image_data = self.ensure_base64_padding(image_data)

            # Remove the base64 image header if it exists
            image_data = re.sub(r"^data:image/[^;]+;base64,", "", image_data)

            if not image_data:
                raise ValueError("⚠️ Invalid image data (empty or malformed).")

            # Decode Base64 image
            image_bytes = base64.b64decode(image_data)
            np_arr = np.frombuffer(image_bytes, np.uint8)

            # Attempt to decode the image
            img = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

            if img is None:
                raise ValueError("⚠️ Failed to decode image data.")

            print(f"🔹 Image decoded successfully, shape: {img.shape}")

            # Convert to grayscale
            gray_img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

            # Load Haar Cascade for face detection
            face_cascade = cv2.CascadeClassifier(
                cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
            )

            # Try to detect faces in the image with adjusted parameters
            faces = face_cascade.detectMultiScale(
                gray_img, scaleFactor=1.3, minNeighbors=6, minSize=(30, 30)
            )

            if len(faces) == 0:
                raise ValueError("⚠️ No face detected!")

            # Extract the first face detected
            x, y, w, h = faces[0]
            face_crop = img[y : y + h, x : x + w]
            face_resized = cv2.resize(face_crop, (100, 100))

            # Save the cropped face image
            face_filename = f"face_{self.username}.png"
            cv2.imwrite(f"media/faces/{face_filename}", face_resized)

            return face_filename  # Return the file path of the saved image

        except Exception as e:
            print(f"⚠️ Error processing face image: {e}")
            return None

    def save_face_image(self, image_data):
        """Process and save the face image."""
        if not self.pk:
            self.save()  # Ensure user exists before saving image

        processed_image_path = self.process_face_image(image_data)
        if processed_image_path:
            self.face_image = processed_image_path
            self.save(update_fields=["face_image"])
            print(f"✅ Face image saved successfully: {self.face_image}")
        else:
            print("❌ Failed to save face image.")

    def ensure_base64_padding(self, base64_string):
        """Ensure the Base64 string has correct padding."""
        padding_needed = len(base64_string) % 4
        if padding_needed:
            base64_string += "=" * (4 - padding_needed)  # Add necessary padding
        return base64_string


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
        if self.password:
            self.password = make_password(self.password)  # Hash the password
        super().save(*args, **kwargs)
