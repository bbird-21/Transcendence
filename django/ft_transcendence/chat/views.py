from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from chat.models import Chat, Message
from django.db.models import Q
from django.contrib.auth.models import User
import json
from django.utils.safestring import mark_safe

@login_required
def index(request):
    return render(request, "chat/index.html")

@login_required
def room(request, room_name, userID):
    from_user = request.user.id
    to_user   = User.objects.get(id=userID)

    my_string = 'Hello'

    context = {
        "my_string": my_string,
        "room_name": room_name,
        "userID": to_user.id,
        "sender_username": request.user.username,
        "receiver_username": to_user.username
    }
    return render(request, "chat/room.html", context)

# ---- Direct Message -------------------
@login_required
def direct_message(request):
    return render(request, "chat/direct_message.html")
