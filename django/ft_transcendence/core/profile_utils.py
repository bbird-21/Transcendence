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
		print("No chat yet")
		chat = Chat.objects.create(fromUser=request.user, toUser=chatWithUser)

	print("Chat exists")
	return chat
