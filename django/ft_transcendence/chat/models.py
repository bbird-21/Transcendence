from django.db import models
import uuid
from django.contrib.auth.models import User
from django.db.models import Subquery, OuterRef
from django.db.models import Q
from django.db.models.functions import Coalesce
from django.db.models import Case, When, Value, DateTimeField, F

class Chat(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    fromUser = models.ForeignKey(User, db_index=True,on_delete=models.CASCADE, null=True,related_name="fromuser")
    toUser = models.ForeignKey(User, db_index=True,on_delete=models.CASCADE, null=True,related_name="toUser")
    createdAt = models.DateTimeField(auto_now_add=True)
    updatedAt = models.DateTimeField(auto_now=True)
    # last_message = models.TextField(null=True, blank=True)

    class Meta:
        unique_together = (("fromUser", "toUser"),)

    def __str__(self):
        return u'%s - %s' % (self.fromUser,self.toUser)

    def get_all_chats(user):
        return Chat.objects.filter(Q(fromUser=user) | Q(toUser=user))

    # @classmethod
    def get_last_message(chat):
        return chat.message_set.last()

    @classmethod
    def reverse_query_set(cls, user, querySet):
        reverse_query = querySet.all()
        for query in reverse_query:
            if ( query.toUser == user ):
                query.toUser = query.fromUser
                query.fromUser = user
                query.save()
        return reverse_query

    @classmethod
    def get_user_chats(cls, user):
        base_query = Chat.objects.filter(Q(fromUser=user) | Q(toUser=user))

        reverse_query = cls.reverse_query_set(user, base_query)
        return reverse_query.annotate(
            last_message_time=Subquery(
                Message.objects.filter(refChat=OuterRef('id'))
                .order_by('-createdAt')
                .values('createdAt')[:1]
            ),
            last_message=Subquery(
                Message.objects.filter(refChat=OuterRef('id'))
                .order_by('-createdAt')
                .values('message')[:1]
            )
        ).annotate(
            # If last_message_time is null, use createdAt of the chat
            last_message_sort=Case(
                When(last_message_time__isnull=False, then=F('last_message_time')),
                default=F('createdAt'),
                output_field=DateTimeField()
            )
        ).order_by('-last_message_sort')



class Message(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    author = models.ForeignKey(User, db_index=True, related_name='author', on_delete=models.CASCADE,null=True)
    message_receiver = models.ForeignKey(User, db_index=True, related_name='message_receiver', on_delete=models.CASCADE,null=True)
    refChat = models.ForeignKey(Chat, db_index=True,on_delete=models.CASCADE)
    message = models.TextField()
    msg_type = (
        (0, "TEXT"),
        (1, "GEOLOC"),
        (2, "PHOTO"),
    )
    type = models.IntegerField(choices=msg_type, default=0)
    extraData = models.CharField(default='', null=True, blank=True, max_length=255)
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
