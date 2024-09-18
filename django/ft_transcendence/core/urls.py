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
	path("send_friend_request/<int:userID>/", views.send_friend_request, name="send_friend_request"),
	path("accept_friend_request/<int:requestID", views.accept_friend_request, name="accept_friend_request")
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
