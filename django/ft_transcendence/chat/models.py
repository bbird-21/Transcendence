from django.db import models
import uuid
from django.contrib.auth.models import User


class Chat(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    fromUser = models.ForeignKey(User, db_index=True,on_delete=models.SET_NULL, null=True,related_name="fromuser")
    toUser = models.ForeignKey(User, db_index=True,on_delete=models.SET_NULL, null=True,related_name="toUser")
    createdAt = models.DateTimeField(auto_now_add=True)
    updatedAt = models.DateTimeField(auto_now=True)
    unique_together = (("fromUser", "toUser"),)

    class Meta:
        unique_together = (("fromUser", "toUser"),)

    def __str__(self):
        return u'%s - %s' % (self.fromUser,self.toUser)

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
