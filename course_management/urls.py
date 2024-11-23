"""
URL configuration for course_management project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

# Lines 24 and 25 handle JWT (JSON Web Token) authentication:
#
# path('api/token/') - This endpoint allows users to obtain a new JWT token pair by providing their credentials.
# When a user logs in successfully, it returns both an access token and a refresh token.
#
# path('api/token/refresh/') - This endpoint allows users to obtain a new access token by providing a valid refresh token.
# This is used when the original access token expires, allowing users to stay logged in without re-entering credentials.

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('courses.urls')),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]
