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
from chat.models import Chat

# ---- <login.html> ---------------------
def login(request):
    if request.method == "POST":
        if "signin-username" in request.POST:
            signin_form = SigninForm(request.POST, prefix="signin")
            if signin_form.is_valid():
                user = authenticate(username=signin_form.cleaned_data['username'], password=signin_form.cleaned_data['password'])
                if user:
                    django_login(request, user)
                    return HttpResponseRedirect("/home/")
            else:
                return render(request, "core/login.html", {
                    "signin_invalid_credentials": True,
                    "signin_form": signin_form
                })
        elif "signup-username" in request.POST:
            signup_form = SignupForm(request.POST, prefix="signup")
            if not signup_form.is_valid():
                return render(request, "core/login.html", {
                    "signup_invalid_credentials": True,
                    "signup_form": signup_form
                })
            else:
                username = signup_form.cleaned_data["username"]
                password = signup_form.cleaned_data["password"]
                signup_form.save()
                user = User.objects.get(username=username)
                user.set_password(password)
                user = authenticate(username=username, password=password)
                if user is not None:
                    django_login(request, user)
                    return HttpResponseRedirect("/home/")
        else:
            return HttpResponseRedirect('/login/')
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
    is_friend = False
    has_friend_request = False
    friend_request_receiver = request.user.receiver.all()
    friend_request_sender   = request.user.sender.all()
    # room_name = f"{user_profile.id}{request.user.id}"
    from_user = request.user.id
    to_user = user_profile.id

    # chat, created = Chat.objects.filter(Q(fromUser_id=13, toUser_id=25) | Q(fromUser_id=25, toUser_id=13)).get_or_create(fromUser_id=13,toUser_id=25)
    chat = get_or_create_chat(request, user_profile)
    room_name = chat.id

    # Is userprofile a friend
    for friend in request.user.userprofile.friends.all():
        if friend.id == user_profile.id:
            is_friend = True
    # Is there friend request that the user has received from user_profile
    for received in friend_request_receiver:
        if received.sender == user_profile:
            has_friend_request = True
            break
    # Is there friend request that the user has send to user_profile
    for send in friend_request_sender:
        if send.receiver == user_profile:
            has_friend_request = True
            break

    context = {
        "user_profile": user_profile,
        "has_friend_request": has_friend_request,
        "is_friend": is_friend,
        "room_name": room_name
    }

    return render(request, "core/profile.html", context)


@login_required
def get_or_create_chat(request, chatWithUser):
    refUser = request.user

    chat = Chat.objects.filter(
            Q(fromUser=refUser, toUser=chatWithUser) |
            Q(fromUser=chatWithUser, toUser=refUser)
        ).first()

    if not chat:
        Chat.objects.create(fromUser=request.user, toUser=chatWithUser)

    return chat


@login_required
@never_cache
def social(request, searched_username="", user_found=True):
    blocked_users = request.user.userprofile.blocked_user.all()
    all_users = User.objects.all().exclude(id__in=blocked_users)
    all_friend_request = FriendRequest.objects.filter(receiver_id=request.user)
    sent_friend_requests = request.user.sender.values_list('receiver', flat=True)
    received_friend_requests = request.user.receiver.values_list('sender', flat=True)
    all_friends = request.user.userprofile.friends.all()
    available_friend_request = (
        all_users
        .exclude(id__in=sent_friend_requests)
        .exclude(id__in=received_friend_requests)
        .exclude(id=request.user.id)
        .exclude(is_superuser=True)
        .exclude(id__in=all_friends)
        .exclude(id__in=blocked_users)
    )

    search_user_form = SearchUser(prefix="search")
    if request.method == "POST":
        search_user_form = SearchUser(request.POST, prefix="search")
        if search_user_form.is_valid():
            searched_username = search_user_form.cleaned_data["username"]
            try:
                searched_user = User.objects.get(username=searched_username)
            except User.DoesNotExist:
                user_found = False
                return redirect('/social/', searched_username=searched_username, user_found=user_found)
            if user_found:
                return redirect(f'/profile/{searched_user.username}')
    return render(request, "core/social.html", {
        "search_form": search_user_form,
        "all_users": all_users,
        "all_friend_request": all_friend_request,
        "available_friend_request": available_friend_request,
        "blocked_users": blocked_users,
        "all_friends": all_friends,
        "searched_username": searched_username,
        "user_found": user_found
    })

# ---- Friend Request ---------------------------
@login_required
@never_cache
def send_friend_request(request, userID):
    sender = request.user
    receiver   = User.objects.get(id=userID)
    friend_request, created = FriendRequest.objects.get_or_create(
        sender=sender, receiver=receiver)
    if created:
        previous_url = request.META.get('HTTP_REFERER', '/')
        return HttpResponseRedirect(previous_url)
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
        previous_url = request.META.get('HTTP_REFERER', '/')
        return HttpResponseRedirect(previous_url)

@login_required
@never_cache
def denied_friend_request(request, requestID):
    friend_request = FriendRequest.objects.get(id=requestID)
    if friend_request.receiver == request.user:
        friend_request.delete()
    previous_url = request.META.get('HTTP_REFERER', '/')
    return HttpResponseRedirect(previous_url)

@login_required
@never_cache
def remove_friend(request, friendID):
    all_friends = request.user.userprofile.friends.all()

    for friend in all_friends:
        if friend.id == friendID:
            # Remove the friend from the request user
            request.user.userprofile.friends.remove(friendID)
            friend = User.objects.get(id=friendID)
            # Remove the request user from the friend
            friend.userprofile.friends.remove(request.user)
            return redirect('/social/')
    return HttpResponse("Can't remove this friend")

def user_is_friend(request, userID):
    all_friends = request.user.userprofile.friends.all()

    for friend in all_friends:
        if friend.id == userID:
            return True
    return False

def delete_pending_friend_request(request, userID):
    friend_request_receiver = friend_request_sender = FriendRequest.objects.filter(receiver_id=request.user.id, sender_id=userID).first()
    friend_request_sender   = friend_request_sender = FriendRequest.objects.filter(receiver_id=userID, sender_id=request.user.id).first()

    if friend_request_receiver:
        friend_request_receiver.delete()
    elif friend_request_sender:
        friend_request_sender.delete()

def delete_current_user_friend_request(request):
    friend_request = FriendRequest.objects.get(sender__id=request.user.id)
    friend_request.delete()

    return redirect('/social/')

@login_required
@never_cache
def block_user(request, userID):
    # Check if the user is a friend or not : None, RemoveFriend
    if user_is_friend(request, userID):
        remove_friend(request, userID)

    # Check if a friend request exist for this userID : None, Delete FriendRequest
    delete_pending_friend_request(request, userID)

    # Retrieve the blocked user
    user_to_block = User.objects.get(id=userID)

    # Set this user in blocked_user for the both
    request.user.userprofile.blocked_user.add(userID)
    user_to_block.userprofile.blocked_user.add(request.user.id)

    return redirect('/social/')

@login_required
@never_cache
def unblock_user(request, userID):
    # Retrieve the blocked user
    user_to_block = User.objects.get(id=userID)

    # Remove block from user
    request.user.userprofile.blocked_user.remove(userID)
    user_to_block.userprofile.blocked_user.remove(request.user.id)

    return redirect('/social/')

# ---- Test Purpose ---------------------

def test(request):
    return render(request, 'core/test.html')
