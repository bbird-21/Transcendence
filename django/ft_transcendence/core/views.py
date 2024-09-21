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
from django.db.models import Q

@login_required
@never_cache
def search_user(request):
    # Get all users
    all_users = User.objects.all()
    all_friend_request = FriendRequest.objects.filter(receiver_id=request.user)
    # Get all friend request that has been sent
    sent_friend_requests = request.user.sender.values_list('receiver', flat=True)
    # Get all friend request that has been received
    received_friend_requests = request.user.receiver.values_list('sender', flat=True)
    # Get all friends from the current user
    all_friends = request.user.userprofile.friends.all()

    # Try to implement this query for a code easier and maintain and modify.
    # It will be (in theory) the value of sent/received_friend_requests
    # friend_requests = FriendRequest.objects.filter(
    #     Q(sender=request.user) | Q(receiver=request.user)
    # )


    # Exclude received and sent request
    available_friend_request = (
        all_users
        .exclude(id__in=sent_friend_requests)
        .exclude(id__in=received_friend_requests)
        .exclude(id=request.user.id)
        .exclude(is_superuser=True)
        .exclude(id__in=all_friends)
    )
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
        "all_friend_request": all_friend_request,
        "available_friend_request": available_friend_request,
        "all_friends": all_friends
    })

@login_required
@never_cache
def social(request):
    return (search_user(request))
    # return render(request, "core/social.html")

@login_required
@never_cache
def send_friend_request(request, userID):
    sender = request.user
    receiver   = User.objects.get(id=userID)
    friend_request, created = FriendRequest.objects.get_or_create(
        sender=sender, receiver=receiver)
    if created:
        return redirect('/social/')
    else:
        return redirect('/social/')


@login_required
@never_cache
def accept_friend_request(request, requestID):
    friend_request = FriendRequest.objects.get(id=requestID)
    if friend_request.receiver == request.user:

        # Get UserProfile objects for both sender and receiver
        receiver_profile = friend_request.receiver.userprofile
        sender_profile = friend_request.sender.userprofile

        # Add each other as friends
        receiver_profile.friends.add(friend_request.sender)  # Add User instance
        sender_profile.friends.add(friend_request.receiver)  # Add User instance

        # Optionally delete the friend request after accepting
        friend_request.delete()
        return search_user(request)
    else:
        return HttpResponse('friend request not accepted')

# ------------- Test Purpose ---------------

def test(request):
    return render(request, 'core/test.html')
