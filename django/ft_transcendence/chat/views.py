from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from chat.models import Chat, Message
from django.db.models import Q
from django.contrib.auth.models import User
import json
from django.utils.safestring import mark_safe
from .chat_utils import get_or_create_chat
from django.shortcuts import redirect

@login_required
def index(request):
    return render(request, "chat/index.html")

@login_required
def room(request, room_name, userID):
    user_chats = Chat.get_user_chats(user=request.user)

    if not user_chats.exists():
        return render(request, "chat/room.html")
    last_user_message = user_chats.last().toUser.id
    try:
        User.objects.get(id=userID)
    except User.DoesNotExist as e:
        return redirect('chat:get_room_redirect', userID=last_user_message)


    from_user = request.user.id
    to_user   = User.objects.get(id=userID)
    user_profile = User.objects.get(id=userID)

    context = {
        "room_name": room_name,
        "userID": to_user.id,
        "sender_username": request.user.username,
        "receiver_username": to_user.username,
        "user_chats": user_chats
    }
    return render(request, "chat/room.html", context)

def get_room_redirect(request, userID):
    user_profile = User.objects.get(id=userID)
    chat = get_or_create_chat(request, user_profile)
    room_name = chat.id

    return redirect('chat:room', room_name=room_name, userID=userID)

# ---- Direct Message -------------------
@login_required
def direct_message(request):
    user_chats = Chat.get_user_chats(user=request.user)
    if not user_chats.exists():
        return render(request, "chat/room.html")
    last_user_chat = user_chats.order_by('createdAt').first().toUser

    return get_room_redirect(request, userID=last_user_chat.id)
