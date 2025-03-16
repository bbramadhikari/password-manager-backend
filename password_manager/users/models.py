from django.contrib.auth.models import AbstractUser
from django.db import models
import cv2
import numpy as np
import base64
import hashlib
import re

# Load Haar Cascade for face detection
CASCADE_PATH = cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
face_cascade = cv2.CascadeClassifier(CASCADE_PATH)


class CustomUser(AbstractUser):
    phone = models.CharField(max_length=15, unique=True)
    face_image = models.TextField(null=True, blank=True)  # Store hashed face image

    groups = models.ManyToManyField(
        "auth.Group",
        related_name="customuser_set",
        blank=True,
    )
    user_permissions = models.ManyToManyField(
        "auth.Permission",
        related_name="customuser_permissions_set",
        blank=True,
    )

    def process_face_image(self, image_data):
        """
        - Detects and extracts the face from the image.
        - Converts to grayscale.
        - Resizes to (100x100).
        - Hashes the processed image.
        """
        try:
            # Remove Base64 header if present
            image_data = re.sub(r"^data:image/[^;]+;base64,", "", image_data)

            # Decode Base64 image
            image_bytes = base64.b64decode(image_data)
            np_arr = np.frombuffer(image_bytes, np.uint8)
            img = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

            # Check if image is valid
            if img is None:
                raise ValueError("Invalid image data. Could not decode.")

            # Convert to grayscale
            gray_img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

            # Detect faces
            faces = face_cascade.detectMultiScale(
                gray_img, scaleFactor=1.1, minNeighbors=5, minSize=(50, 50)
            )

            if len(faces) == 0:
                raise ValueError("No face detected!")

            # Get the first detected face (x, y, w, h)
            x, y, w, h = faces[0]

            # Crop face region
            face_crop = gray_img[y : y + h, x : x + w]

            # Resize to 100x100 for consistency
            face_resized = cv2.resize(face_crop, (100, 100))

            # Encode cropped face back to Base64
            _, buffer = cv2.imencode(".png", face_resized)
            encoded_face = base64.b64encode(buffer).decode()

            # Hash the processed image
            hashed_image = hashlib.sha256(encoded_face.encode()).hexdigest()
            return hashed_image

        except Exception as e:
            print(f"⚠️ Error processing face image: {e}")
            return None  # Return None if there's an error

    def save_face_image(self, image_data):
        """Processes and saves the hashed face image."""
        if not self.pk:
            self.save()  # Ensure user exists before saving image

        processed_hash = self.process_face_image(image_data)
        if processed_hash:
            self.face_image = processed_hash
            self.save(update_fields=["face_image"])

    def verify_face_image(self, image_data):
        """Verifies if the given face image matches the stored hash."""
        processed_hash = self.process_face_image(image_data)
        return self.face_image == processed_hash if processed_hash else False
