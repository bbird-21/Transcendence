# ---- Shorcuts -------------------------
from django.shortcuts import render
from django.shortcuts import redirect

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


# --- Utils -----------------------------
from .utils.profile_utils import (
    get_or_create_chat,
    _has_friend_request_,
    _is_friend_
)
from .utils.login_utils import (
    create_user,
    sign_in_strategy,
    sign_up_strategy,
    login_page
)
from .utils.social_utils import (
    send_friend_request,
    accept_friend_request,
    denied_friend_request,
    remove_friend,
    user_is_friend,
    delete_pending_friend_request,
    delete_current_user_friend_request,
    block_user,
    unblock_user,
    get_social_data,
    user_profile
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
            return HttpResponseRedirect('/login/')
    else:
        return login_page(request)

def logout(request):
        django_logout(request)
        return redirect('login')  # If user is not authenticated, redirect to home

# ---- <home.html> ----------------------
@login_required
@never_cache
def home(request):
    user = request.user
    return render(request, "core/home.html", {"user": user})

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
            return HttpResponseRedirect("/profile/")
        elif username_form.is_valid():
            username_form.save()
            return HttpResponseRedirect("/profile/")
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
from django.db.models import Q

@login_required
@never_cache
def profile(request, username):
    user_profile = User.objects.get(username=username)
    from_user = request.user.id
    to_user = user_profile.id
    is_friend = _is_friend_(request, user_profile)
    has_friend_request = _has_friend_request_(request, user_profile)
    chat = get_or_create_chat(request, user_profile)
    room_name = chat.id

    context = {
        "user_profile": user_profile,
        "has_friend_request": has_friend_request,
        "is_friend": is_friend,
        "room_name": room_name
    }

    return render(request, "core/profile.html", context)


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

