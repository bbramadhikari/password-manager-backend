
# Password Manager Backend

This is the backend for the **Password Manager Application** built using Django and Django REST Framework. It provides authentication, password management, and OTP verification functionalities.

## Features
- User Registration & Authentication (JWT Authentication)
- Password Management (Add, View, Delete Passwords)
- Face ID Verification
- OTP Verification via Email
- Image Upload & Processing

## Requirements
- Python 3.x
- Django 5.1.7
- Django REST Framework 3.15.2
- Django CORS Headers 4.7.0
- Django Extensions 3.2.3
- djangorestframework_simplejwt 5.5.0
- dlib 19.24.6
- face-recognition 1.3.0
- face-recognition-models 0.3.0
- opencv-python 4.11.0.86
- pillow 11.1.0
- psycopg2-binary 2.9.10
- pyotp 2.9.0
- python-dotenv 1.1.0

## Installation

1. Clone the repository:
```bash
   git clone https://github.com/your-username/password-manager-backend.git
```

2. Navigate to the project directory:
```bash
   cd password-manager-backend
```

3. Create and activate a virtual environment:
```bash
   python -m venv env
   source env/bin/activate  # On Windows use `.\env\Scripts\activate`
```

4. Install dependencies:
```bash
   pip install -r requirements.txt
```

5. Apply migrations:
```bash
   python manage.py migrate
```

6. Start the server:
```bash
   python manage.py runserver
```

## Environment Variables

Create a `.env` file in your project root and add the following variables:
```
SECRET_KEY=your_secret_key
DEBUG=True
ALLOWED_HOSTS=*
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your_email@example.com
EMAIL_HOST_PASSWORD=your_password
```

## Usage

- To register a user, visit `/api/signup/`
- To login and obtain tokens, visit `/api/login/`
- To add a password, make a POST request to `/api/passwords/`
- To view passwords, make a GET request to `/api/passwords/`
- To verify OTP, visit `/api/users/verify-otp/`

## Author
Created by: **Baburam Adhikari**
Email: **psnbabu5@gmail.com**

## License
This project is licensed under the MIT License.

