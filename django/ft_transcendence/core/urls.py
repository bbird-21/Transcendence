from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

app_name = 'core'

urlpatterns = [
	path("", views.login, name="login"),
	path("mfa/", views.mfa, name="mfa"),
	path("logout/", views.logout, name="logout"),
	path("home/", views.home, name="home"),
	path("my_profile/", views.my_profile, name="my_profile"),
	path("profile/<str:username>", views.profile, name="profile"),
	path("social/", views.social, name="social"),
	path("send_friend_request/<int:userID>/", views.send_friend_request, name="send_friend_request"),
	path("accept_friend_request/<int:friendRequestID>/", views.accept_friend_request, name="accept_friend_request"),
	path("decline_friend_request/<int:friendRequestID>/", views.decline_friend_request, name="decline_friend_request"),
	path("cancel_friend_request/<int:userID>/", views.cancel_friend_request, name="cancel_friend_request"),
	path("remove_friend/<int:friendID>/", views.remove_friend, name="remove_friend"),
	path("block_user/<int:userID>/", views.block_user, name="block_user"),
	path("notifications/", views.notifications, name="notifications"),
	path("unblock_user/<int:userID>/", views.unblock_user, name="unblock_user")

]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
