from django.db import models
import uuid

from django.conf import settings


class ChatConversation(models.Model):
	id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
	user = models.ForeignKey(
		settings.AUTH_USER_MODEL,
		on_delete=models.CASCADE,
		related_name="chat_conversations",
	)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	class Meta:
		ordering = ["-updated_at"]

	def __str__(self):
		return f"Conversation {self.id} ({self.user_id})"


class ChatMessage(models.Model):
	SENDER_CHOICES = [
		("USER", "User"),
		("ASSISTANT", "Assistant"),
		("SYSTEM", "System"),
	]

	id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
	conversation = models.ForeignKey(
		ChatConversation,
		on_delete=models.CASCADE,
		related_name="messages",
	)
	sender_type = models.CharField(max_length=20, choices=SENDER_CHOICES)
	message_text = models.TextField()
	timestamp = models.DateTimeField(auto_now_add=True)

	class Meta:
		ordering = ["timestamp"]

	def __str__(self):
		return f"{self.sender_type} @ {self.timestamp}"
