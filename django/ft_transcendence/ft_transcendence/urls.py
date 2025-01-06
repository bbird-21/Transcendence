"""
URL configuration for ft_transcendence project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
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
from django.urls import include, path
from core import views
from django.contrib.auth.models import User
from rest_framework import routers
from api import views
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

# Routers provide an easy way of automatically determining the URL conf.
# Because we use ViewSet Routers generate several URL (/users/) (/users/<id>) mapping with corresponding HTTP method (CRUD Operations).
router = routers.DefaultRouter()
router.register(r'users', views.UserViewSet)

urlpatterns = [
    path("", include("core.urls")),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/', include(router.urls)),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    path("fortytwo/", include("fortytwo.urls")),
    path("admin/", admin.site.urls),
    path("accounts/", include("allauth.urls")),
    path("prometheus/", include("django_prometheus.urls")),
    path("chat/", include("chat.urls")),
    path("game/", include("game.urls"))
]
