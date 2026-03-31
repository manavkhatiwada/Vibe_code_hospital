from rest_framework import serializers

from .models import ChatConversation, ChatMessage


class ChatMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatMessage
        fields = ["id", "conversation", "sender_type", "message_text", "timestamp"]
        read_only_fields = ["id", "conversation", "timestamp"]


class ChatConversationSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatConversation
        fields = ["id", "user", "created_at", "updated_at"]
        read_only_fields = ["id", "user", "created_at", "updated_at"]


class CreateChatMessageSerializer(serializers.Serializer):
    message_text = serializers.CharField(allow_blank=False, trim_whitespace=True)
    assistant_message_text = serializers.CharField(
        allow_blank=False, trim_whitespace=True, required=False
    )
