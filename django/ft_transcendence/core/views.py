# ---- Shorcuts -------------------------
from django.shortcuts import render
from django.shortcuts import redirect
from django.urls import reverse

# ---- Authentication -------------------
from django.contrib.auth.models import User
from .models import FriendRequest

# ---- Forms ----------------------------
from .forms import (
    NameForm,
    AvatarForm,
    UsernameForm,
    SearchUser
)

# ---- Decorators ----------------------
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import never_cache


# ---- Etc ------------------------------
from django.http import HttpResponseRedirect
from django.http import HttpResponse
from django.views.generic import TemplateView
from chat.models import Chat
from django.contrib.auth import logout as django_logout
from django.db.models import Q


# --- Utils -----------------------------
from chat.chat_utils import get_or_create_chat

from .utils.login_utils import (
    create_user,
    sign_in_strategy,
    sign_up_strategy,
    login_page
)
from .utils.social_utils import (
    send_friend_request,
    accept_friend_request,
    decline_friend_request,
    remove_friend,
    user_is_friend,
    cancel_friend_request,
    block_user,
    unblock_user,
    get_social_data,
    user_profile,
    has_received_friend_request,
    has_sent_friend_request,
    _is_friend_
)


# ---- <login.html> ---------------------
def login(request):
    if request.user.is_authenticated:
        return redirect("/home/")
    if request.method == "POST":
        if "signin-username" in request.POST:
            return sign_in_strategy(request)
        elif "signup-username" in request.POST:
            return sign_up_strategy(request)
        else:
            return HttpResponseRedirect(reverse('core:login'))
    else:
        return login_page(request)

def logout(request):
        django_logout(request)
        return redirect(reverse('core:login'))

# ---- <home.html> ----------------------
@login_required
@never_cache
def home(request):
    received_friend_requests = request.user.receiver.values_list('sender__username')

    context = {
        "friend_requests": received_friend_requests
    }
    return render(request, "core/home.html", context)

@login_required
@never_cache
def my_profile(request):
    avatar_is_valid = True
    if request.method == "POST":
        # This form update the existing UserProfile for the current user, instead of creating a new one
        avatar_form = AvatarForm(request.POST, request.FILES, instance=request.user.userprofile, prefix="avatar")
        username_form = UsernameForm(request.POST, prefix="username", instance=request.user)
        if 'avatar-avatar' in request.FILES and avatar_form.is_valid():
            avatar_form.save()
            return HttpResponseRedirect("/my_profile/")
        elif username_form.is_valid():
            username_form.save()
            return HttpResponseRedirect("/my_profile/")
        else:
            avatar_is_valid = False
            print(avatar_form.errors)  # For debugging purposes
    avatar_form = AvatarForm(prefix="avatar")
    username_form = UsernameForm(prefix="username")
    avatar_url = request.user.userprofile.avatar.url
    return render(request, "core/my_profile.html", {
        "avatar_form": avatar_form,
        "username_form": username_form,
        "avatar": avatar_url,
        "avatar_is_valid": avatar_is_valid,
        "userprofile": request.user.userprofile
    })

# ---- <social.html> ---------------------------
@login_required
@never_cache
def profile(request, username):
    user_profile = User.objects.get(username=username)
    from_user = request.user.id
    to_user = user_profile.id
    is_friend = _is_friend_(request, user_profile)
    received_friend_request = has_received_friend_request(request, user_profile)
    sent_friend_request     = has_sent_friend_request(request, user_profile)
    chat = get_or_create_chat(request, user_profile)
    room_name = chat.id
    all_users = User.objects.all()

    print(f"received_friend_request : {received_friend_request}")
    print(f"sent_friend_request     : {sent_friend_request}")
    print(f"username                : {username}")
    context = {
        "all_users": all_users,
        "user_profile": user_profile,
        "received_friend_request": received_friend_request,
        "sent_friend_request": sent_friend_request,
        "is_friend": is_friend,
        "room_name": room_name
    }

    return render(request, "core/user_profile.html", context)


@login_required
@never_cache
def social(request, searched_username="", user_found=True):
    context = get_social_data(request)
    search_user_form = SearchUser(prefix="search")
    if request.method == "POST":
        search_user_form = SearchUser(request.POST, prefix="search")
        if search_user_form.is_valid():
            return user_profile(request, search_user_form)
        else:
            return redirect("/home/")

    context['search_form'] = search_user_form
    context['user_found'] = user_found
    return render(request, "core/social.html", context)

