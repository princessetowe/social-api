# Social Media API

A scalable **Social Media REST API** built with **Django** and **Django REST Framework (DRF)**. The project is modularized into multiple apps such as **accounts**, **posts**, **messaging**, **notifications**, and **search**, and includes **Swagger/OpenAPI documentation** for easy API exploration.

---

## 🚀 Features

* Custom user authentication (username, email, or phone number)
* Email verification system
* Public & private user accounts
* Follow, follow requests, and blocking system
* User statistics (followers, following, posts count)
* Messaging between users
* Notifications system
* Posts creation and interaction
* Search functionality
* API rate limiting with custom throttle responses
* Swagger / OpenAPI documentation

---

## 🧱 Project Structure

All applications live inside a single Django project called **`backend`**.

```
backend/
├── accounts/
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── backends.py
│   ├── exceptions.py
│   ├── models.py
│   ├── serializers.py
│   ├── signals.py
│   ├── tests.py
│   ├── throttles.py
│   ├── urls.py
│   └── views.py
├── backend/
│   ├── __init__.py
│   ├── asgi.py
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── messaging/
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── models.py
│   ├── serializers.py
│   ├── tests.py
│   ├── urls.py
│   └── views.py
├── notifications/
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── models.py
│   ├── serializers.py
│   ├── signals.py
│   ├── tests.py
│   ├── urls.py
│   └── views.py
├── posts/
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── models.py
│   ├── serializers.py
│   ├── signals.py
│   ├── tests.py
│   ├── urls.py
│   └── views.py
├── search/
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── models.py
│   ├── serializers.py
│   ├── tests.py
│   ├── urls.py
│   └── views.py
├── utils/
│   ├── hashtag.py
│   └── tags.py
├── manage.py
├── requirements.txt
├── README.md
```

---

## 👤 Accounts App

The **accounts** app handles authentication, user profiles, and social relationships.

### 🔐 Authentication

* Custom authentication backend allows users to log in using:

  * Username
  * Email address
  * Phone number

Implemented in `backends.py` by extending Django’s `ModelBackend`.

### 🧑 Custom User Model

* Extends `AbstractUser`
* Unique email field
* Optional phone number (with validation)
* Profile picture and bio
* Country field
* Privacy setting (`is_private`)

### ✉️ Email Verification

* Email verification tokens generated using UUID
* Tokens expire after **8 hours**
* Linked to users via a foreign key

### 🤝 Follow System

* Users can follow other users
* Private accounts require approval via **follow requests**
* Unique constraints prevent duplicate relationships

### 📊 User Statistics

* One-to-one relationship with user
* Tracks:

  * Number of posts
  * Followers count
  * Following count

### 🚫 Blocking

* Users can block other users
* Blocked users cannot interact
* Duplicate blocks are prevented

---

## ⚠️ Exception Handling

A custom DRF exception handler is implemented to improve API error responses.

### Throttling Response

When a user exceeds the request limit:

```json
{
  "error": "Too many requests",
  "message": "Please try again in X seconds."
}
```

This ensures consistent and user-friendly API feedback.

---

## 📨 Other Apps Overview

### 📝 Posts

* Create, update, and delete posts
* Supports **hashtags** in posts
* Comments support **mentions (@username)** and **hashtags (#tag)**
* Tracks post counts per user

### 💬 Messaging

* One-to-one private messaging
* Group chat support
* Designed for real-time or asynchronous communication

### 🔔 Notifications

Notifications are generated for key user activities, including:

* Like
* Comment
* Follow
* Tag
* Follow request
* Message

This ensures users stay informed about interactions relevant to them.

### 🔍 Search

* Search by **hashtags**
* Search users by **name**
* Search users by **username**

---

## 📄 API Documentation (Swagger)

Swagger/OpenAPI is integrated for easy testing and exploration of endpoints.

Once the server is running, access:

```
/api/docs/
```

(or the configured Swagger URL)

---

## 🛠️ Installation & Setup

### 1️⃣ Clone the repository

```bash
git clone https://github.com/princessetowe/social-api.git
cd social-api
```

### 2️⃣ Create and activate virtual environment

```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

### 3️⃣ Install dependencies

```bash
pip install -r requirements.txt
```

### 4️⃣ Configure environment variables

Create a `.env` file and set:

```
SECRET_KEY=
DEBUG=True
DATABASE_URL=
EMAIL_HOST=
EMAIL_PORT=
EMAIL_HOST_USER=
EMAIL_HOST_PASSWORD=
```

### 5️⃣ Run migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

### 6️⃣ Start the server

```bash
python manage.py runserver
```

---

## 🔐 Authentication & Permissions

* JWT (depending on configuration)
* Protected endpoints require authentication
* Permissions vary by app and endpoint

---

## 🧪 Testing

```bash
python manage.py test
```

---

## 📌 Tech Stack

* Python
* Django
* Django REST Framework
* SQLite (configurable)
* Swagger / OpenAPI
* django-phonenumber-field
* django-countries

---

## 📄 License

This project is licensed under the MIT License.

---

## ✨ Author

Built with ❤️ for scalable social platforms.

Feel free to contribute, open issues, or suggest improvements.