from django.contrib.auth.decorators import login_required
from chat.models import Chat
from django.db.models import Q


@login_required
def get_or_create_chat(request, chatWithUser):
	refUser = request.user

	chat = Chat.objects.filter(
			Q(fromUser=refUser, toUser=chatWithUser) |
			Q(fromUser=chatWithUser, toUser=refUser)
		).first()

	if not chat:
		chat = Chat.objects.create(fromUser=request.user, toUser=chatWithUser)

	return chat

def _has_friend_request_(request, user_profile):
	friend_request_receiver = request.user.receiver.all()
	friend_request_sender   = request.user.sender.all()
	# Is there friend request that the user has received from user_profile
	for received in friend_request_receiver:
		if received.sender == user_profile:
			return True
	# Is there friend request that the user has send to user_profile
	for send in friend_request_sender:
		if send.receiver == user_profile:
			return True
	return False

def _is_friend_(request, user_profile):
	# Is userprofile a friend
	for friend in request.user.userprofile.friends.all():
		if friend.id == user_profile.id:
			return True
	return False

