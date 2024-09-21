from django.db import models
from django.contrib.auth.models import User
from django.dispatch import receiver
from django.db.models.signals import post_save
from django import forms
from django.contrib import admin
from django.contrib.auth.models import User


# Tips :
#  -Django can't have two reverse query names that are the same \
#   To prevent this behavior we use <related_name> to have unique "reverse query name" \
class UserProfile(models.Model):
    user   = models.OneToOneField(User, on_delete=models.CASCADE) # Here
    avatar = models.ImageField(upload_to="avatars/", default="avatar.png")
    victory = models.IntegerField(default=0)
    defeat = models.IntegerField(default=0)
    friends = models.ManyToManyField(User, blank=True, related_name="userprofile_friends") # And here
    list_display = ['user', 'avatar']  # Customize fields to display

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
    from_user = models.ForeignKey(User, related_name="from_user", on_delete=models.CASCADE)
    # Who receive the request
    to_user   = models.ForeignKey(User, related_name= "to_user", on_delete=models.CASCADE)

    def __str__(self):
        return f"FriendRequest from {self.from_user.username} to {self.to_user.username}"
