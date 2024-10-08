from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
	path("", views.login, name="login"),
	path("logout/", views.logout, name="logout"),
	path("home/", views.home, name="home"),
	path("my_profile/", views.my_profile, name="my_profile"),
	path("profile/<str:username>", views.profile, name="profile"),
	path("social/", views.social, name="social"),
	path("test/", views.test, name="test"),
	path("send_friend_request/<int:userID>/", views.send_friend_request, name="send_friend_request"),
	path("accept_friend_request/<int:requestID>/", views.accept_friend_request, name="accept_friend_request"),
	path("delete_current_user_friend_request/", views.delete_current_user_friend_request, name="delete_current_user_friend_request"),
	path("denied_friend_request/<int:requestID/", views.denied_friend_request, name="denied_friend_request"),
	path("remove_friend/<int:friendID>/", views.remove_friend, name="remove_friend"),
	path("block_user/<int:userID>/", views.block_user, name="block_user"),
	path("unblock_user/<int:userID>/", views.unblock_user, name="unblock_user")

]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
