from .models import Chat
from django.db.models import Q

def get_or_create_chat(request, chatWithUser):
	refUser = request.user

	chat = Chat.objects.filter(
			Q(fromUser=refUser, toUser=chatWithUser) |
			Q(fromUser=chatWithUser, toUser=refUser)
		).first()

	if not chat:
		chat = Chat.objects.create(fromUser=request.user, toUser=chatWithUser)

	return chat
