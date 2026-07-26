from rest_framework import serializers

from medical_records.models import MedicalRecord

from .models import ChatConversation, ChatMessage


class AttachedMedicalRecordSerializer(serializers.ModelSerializer):
    report_file = serializers.FileField(use_url=True, read_only=True)

    class Meta:
        model = MedicalRecord
        fields = ["id", "folder_name", "notes", "report_file"]


class ChatMessageSerializer(serializers.ModelSerializer):
    medical_record = AttachedMedicalRecordSerializer(read_only=True)

    class Meta:
        model = ChatMessage
        fields = ["id", "conversation", "sender_type", "message_text", "timestamp", "medical_record"]
        read_only_fields = ["id", "conversation", "timestamp", "medical_record"]


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
    medical_record_id = serializers.UUIDField(required=False, allow_null=True)
