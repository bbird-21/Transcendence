from django.shortcuts import render
from django.contrib.auth.decorators import login_required
# Create your views here.

@login_required
def index(request):
    return render(request, "chat/index.html")

@login_required
def room(request, room_name):
    return render(request, "chat/room.html", {"room_name": room_name})

# ---- Direct Message -------------------
@login_required
def send_direct_message(request, userID):
    return render(request, "chat/direct_message.html")

