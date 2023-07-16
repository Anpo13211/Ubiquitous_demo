from django.db import models

class ChatSession(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)

class ChatMessage(models.Model):
    session = models.ForeignKey(ChatSession, related_name='messages', on_delete=models.CASCADE)
    content = models.TextField()
    by_user = models.BooleanField()
    created_at = models.DateTimeField(auto_now_add=True)
