from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from chat.models import Chat
from django.db.models import Q
@login_required
def index(request):
    return render(request, "chat/index.html")

@login_required
def room(request, room_name, userID):
    from_user = request.user.id
    to_user   = userID

    # chat, created = Chat.objects.filter(Q(fromUser_id=from_user, toUser_id=to_user) | Q(fromUser_id=to_user, toUser_id=from_user)).get_or_create(fromUser_id=from_user, toUser_id=to_user)

    print(f"roomid : {room_name}")
    return render(request, "chat/room.html", {
        "room_name": room_name,
        "userID": userID
    })

# ---- Direct Message -------------------
@login_required
def send_direct_message(request, userID):
    return render(request, "chat/direct_message.html")
