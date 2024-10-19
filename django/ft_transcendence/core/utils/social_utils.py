from django.http import HttpResponseRedirect
from django.shortcuts import redirect
from core.models import FriendRequest
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import never_cache
from django.shortcuts import render

def	user_profile(request, search_user_form):
	searched_username = search_user_form.cleaned_data["username"]
	try:
		searched_user = User.objects.get(username=searched_username)
	except User.DoesNotExist:
		return render(request, 'core/social.html', {
			"searched_username": searched_username,
			"user_found": False,
			"search_form": search_user_form
		})
	return redirect(f'/profile/{searched_user.username}')

def get_social_data(request):
    blocked_users = request.user.userprofile.blocked_user.all()
    all_users = User.objects.all()
    sent_friend_requests = request.user.sender.values_list('receiver', flat=True)
    received_friend_requests = request.user.receiver.values_list('sender', flat=True)
    all_friends = request.user.userprofile.friends.all()
    all_friend_request = FriendRequest.objects.filter(receiver_id=request.user)

    available_friend_requests = (
        all_users
        .exclude(id__in=sent_friend_requests)
        .exclude(id__in=received_friend_requests)
        .exclude(id=request.user.id)
        .exclude(is_superuser=True)
        .exclude(id__in=all_friends)
        .exclude(id__in=blocked_users)
    )

    return {
        'blocked_users': blocked_users,
        'sent_friend_requests': sent_friend_requests,
        'received_friend_requests': received_friend_requests,
        'all_friends': all_friends,
        'available_friend_requests': available_friend_requests,
		'all_users': all_users,
        'all_friend_request': all_friend_request
    }


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
