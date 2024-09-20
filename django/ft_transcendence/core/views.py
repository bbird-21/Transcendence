# ---- Shorcuts -------------------------
from django.shortcuts import render
from django.shortcuts import redirect

# ---- Authentication -------------------
from django.contrib.auth import logout as django_logout
from django.contrib.auth import login as django_login
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from .models import FriendRequest

# ---- Forms ----------------------------
from .forms import NameForm
from .forms import SignupForm
from .forms import SigninForm
from .forms import AvatarForm
from .forms import UsernameForm
from .forms import SearchUser

# ---- Decorators ----------------------
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import never_cache


# ---- Etc ------------------------------
from django.http import HttpResponseRedirect
from django.http import HttpResponse
from django.views.generic import TemplateView


# ---- <login.html> ---------------------
def login(request):
    if request.method == "POST":
        signin_form = SigninForm(request.POST, prefix="signin")
        signup_form = SignupForm(request.POST, prefix="signup")
        if signin_form.is_valid():
            user = authenticate(username=signin_form.cleaned_data['username'], password=signin_form.cleaned_data['password'])
            if user:
                django_login(request, user)
                return HttpResponseRedirect("/home")
        elif signup_form.is_valid():
            username = signup_form.cleaned_data["username"]
            password = signup_form.cleaned_data["password"]
            # process the data in signup_form.cleaned_data as required
            signup_form.save()
            user = User.objects.get(username=username)
            user.set_password(password)
            user = authenticate(username=username, password=password)
            # A backend authenticated the credentials
            if user is not None:
                django_login(request, user)
                return HttpResponseRedirect("/home/")
    else:
        signin_form = SigninForm(prefix="signin")
        signup_form = SignupForm(prefix="signup")
    return render(request, "core/login.html", {
        "signin_form": signin_form,
        "signup_form": signup_form,
    })

def logout(request):
        django_logout(request)
        return redirect('login')  # If user is not authenticated, redirect to home

# ---- <home.html> ----------------------
@login_required
def home(request):
    user = request.user
    return render(request, "core/home.html", {"user": user})

@login_required
@never_cache
def profile(request):
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
    return render(request, "core/profile.html", {
        "avatar_form": avatar_form,
        "username_form": username_form,
        "avatar": avatar_url,
        "avatar_is_valid": avatar_is_valid,
        "userprofile": request.user.userprofile
    })


# ---- <social.html> ---------------------------
def search_user(request):
    all_users = User.objects.all()  # Get all users
    allfriendrequest = FriendRequest.objects.all()
    sent_friend_requests = request.user.from_user.values_list('to_user', flat=True)
    user_without_friend_request = all_users.exclude(id__in=sent_friend_requests).exclude(id=request.user.id).exclude(is_superuser=True)
    if request.method == "POST":
        search_user_form = SearchUser(request.POST, prefix="search")
        if search_user_form.is_valid():
            user_search = search_user_form.cleaned_data["username"]
            print(f"user search : {user_search}")
            user_list = User.objects.filter(username__contains=user_search)
            print(f"user_list {user_list}")
            return HttpResponseRedirect("/social/")
    search_user_form = SearchUser(prefix="search")
    return render(request, "core/social.html", {
        "search_form": search_user_form,
        "all_users": all_users,
        "allfriendrequest": allfriendrequest,
        "user_without_friend_request": user_without_friend_request
    })


def social(request):
    return (search_user(request))
    # return render(request, "core/social.html")

@login_required
def send_friend_request(request, userID):
    from_user = request.user
    to_user   = User.objects.get(id=userID)
    friend_request, created = FriendRequest.objects.get_or_create(
        from_user=from_user, to_user=to_user)
    if created:
        return HttpResponse('friend request sent')
    else:
        return HttpResponse('friend request was already sent')

@login_required
def accept_friend_request(request, requestID):
    friend = FriendRequest.objects.get(id=requestID)
    if friend.to_user == request.user:
        friend_request.to_user.friends.add(friend_request.from_user)
        friend_request.from_user.friends.add(friends.request.to_user)
        friend_request.delete()
        return HttpResponseRedirect('/social/')
    else:
        return HttpResponse('friend request not accepted')

# ------------- Test Purpose ---------------

def test(request):
    return render(request, 'core/test.html')
