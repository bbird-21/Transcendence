from django.db import models
import uuid
from django.contrib.auth.models import User
from django.db.models import Subquery, OuterRef

class Chat(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    fromUser = models.ForeignKey(User, db_index=True,on_delete=models.SET_NULL, null=True,related_name="fromuser")
    toUser = models.ForeignKey(User, db_index=True,on_delete=models.SET_NULL, null=True,related_name="toUser")
    createdAt = models.DateTimeField(auto_now_add=True)
    updatedAt = models.DateTimeField(auto_now=True)
    unique_together = (("fromUser", "toUser"),)
    # last_message = models.TextField(null=True, blank=True)

    class Meta:
        unique_together = (("fromUser", "toUser"),)

    def __str__(self):
        return u'%s - %s' % (self.fromUser,self.toUser)

    def get_all_chat(fromUser):
        return Chat.objects.filter(fromUser=fromUser)

    def get_last_message(fromUser):
        return Chat.message_set.last()

    def get_user_chats(user):
        return Chat.objects.filter(
            fromUser=user
        ).annotate(
            last_message=Subquery(
                Message.objects.filter(refChat=OuterRef('pk'))
                .order_by('-createdAt')
                .values('message')[:1]
            ),
            last_message_time=Subquery(
                Message.objects.filter(refChat=OuterRef('pk'))
                .order_by('-createdAt')
                .values('createdAt')[:1]
            )
        ).order_by('-last_message_time')



class Message(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    refChat = models.ForeignKey(Chat, db_index=True,on_delete=models.CASCADE)
    message = models.TextField()
    msg_type = (
        (0, "TEXT"),
        (1, "GEOLOC"),
        (2, "PHOTO"),
    )
    type = models.IntegerField(choices=msg_type, default=0)
    extraData = models.CharField(default='', null=True, blank=True, max_length=255)
    author = models.ForeignKey(User, db_index=True, related_name='author', on_delete=models.SET_NULL,null=True)
    isRead = models.BooleanField(default=False)
    createdAt = models.DateTimeField(auto_now_add=True)
    updatedAt = models.DateTimeField(auto_now=True)

    def __str__(self):
        return u'%s - %d' % (self.refChat,self.type)

    def get_all_messages_from_chat(chat):
        return Message.objects.filter(refChat=chat).order_by('createdAt')

    def get_last_message(chat):
        return Message.objects.filter(refChat=chat).last()

    # def save(self, *args, **kwargs):
    #     super().save(*args, **kwargs)
    #     # Update last_message in Chat model
    #     self.refChat.last_message = self.message
    #     self.refChat.save()
