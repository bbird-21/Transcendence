from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
	path("", views.login, name="login"),
	path("logout/", views.logout, name="logout"),
	path("home/", views.home, name="home"),
	path("profile/", views.profile, name="profile"),
	path("social/", views.social, name="social"),
	path("test/", views.test, name="test"),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
