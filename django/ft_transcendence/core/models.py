from django.db import models
from django.contrib.auth.models import User
from django.dispatch import receiver
from django.db.models.signals import post_save
from django import forms
from django.contrib import admin
from django.contrib.auth.models import User
from chat.models import Chat, Message
from game.models import Game, Invitation

# Tips :
#  -Django can't have two reverse query names that are the same \
#   To prevent this behavior we use <related_name> to have unique "reverse query name" \
class UserProfile(models.Model):
    user                = models.OneToOneField(User, on_delete=models.CASCADE) # Here
    avatar              = models.ImageField(upload_to="avatars/", default="avatar.png")
    victory             = models.IntegerField(default=0)
    defeat              = models.IntegerField(default=0)
    friends             = models.ManyToManyField(User, blank=True, related_name="userprofile_friends") # And here
    blocked_by_them     = models.ManyToManyField(User, blank=True, related_name="blocked_by_them")
    blocked_by_me       = models.ManyToManyField(User, blank=True, related_name="blocked_by_me")
    list_display        = ['user', 'avatar']  # Customize fields to display

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.userprofile.save()

# Many-to-One (ForeignKey)
class FriendRequest(models.Model):
    # Who sent the request
    sender      = models.ForeignKey(User, related_name="sender", on_delete=models.CASCADE)
    # Who receive the request
    receiver    = models.ForeignKey(User, related_name= "receiver", on_delete=models.CASCADE)

    # def __str__(self):
    #     return f"FriendRequest from {self.sender.username} to {self.receiver.username}"

# One Notification per User.
class Notification(models.Model):
    receiver        = models.ForeignKey(User, null=True, related_name="notification_receiver", on_delete=models.CASCADE)
    friend_request  = models.ForeignKey(FriendRequest, null=True, related_name="notification_friend_request", on_delete=models.CASCADE)
    message         = models.ForeignKey(Message, null=True, related_name="message_notification", on_delete=models.CASCADE)
    game_invitation = models.ForeignKey(Invitation, null=True, related_name="game_invitation", on_delete=models.CASCADE)
    total_notifs    = models.IntegerField(default=0)
