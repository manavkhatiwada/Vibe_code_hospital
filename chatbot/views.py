from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from medical_records.models import MedicalRecord
from patients.models import Patient

from . import services
from .models import ChatConversation, ChatMessage
from .serializers import (
	ChatConversationSerializer,
	ChatMessageSerializer,
	CreateChatMessageSerializer,
)
from users.permissions import IsPatientRole


class ChatConversationListCreateView(APIView):
	permission_classes = [IsAuthenticated, IsPatientRole]

	def get(self, request):
		conversations = ChatConversation.objects.filter(user=request.user)
		serializer = ChatConversationSerializer(conversations, many=True)
		return Response(serializer.data, status=status.HTTP_200_OK)

	def post(self, request):
		conversation = ChatConversation.objects.create(user=request.user)
		serializer = ChatConversationSerializer(conversation)
		return Response(serializer.data, status=status.HTTP_201_CREATED)


class ChatConversationMessageListCreateView(APIView):
	permission_classes = [IsAuthenticated, IsPatientRole]

	def get(self, request, conversation_id):
		conversation = ChatConversation.objects.filter(
			id=conversation_id, user=request.user
		).first()
		if not conversation:
			return Response(
				{"detail": "Conversation not found."},
				status=status.HTTP_404_NOT_FOUND,
			)

		messages = ChatMessage.objects.filter(conversation=conversation)
		serializer = ChatMessageSerializer(messages, many=True, context={"request": request})
		return Response(serializer.data, status=status.HTTP_200_OK)

	def post(self, request, conversation_id):
		conversation = ChatConversation.objects.filter(
			id=conversation_id, user=request.user
		).first()
		if not conversation:
			return Response(
				{"detail": "Conversation not found."},
				status=status.HTTP_404_NOT_FOUND,
			)

		input_serializer = CreateChatMessageSerializer(data=request.data)
		input_serializer.is_valid(raise_exception=True)

		medical_record_id = input_serializer.validated_data.get("medical_record_id")
		record = None
		if medical_record_id:
			patient_profile, _ = Patient.objects.get_or_create(user=request.user)
			record = MedicalRecord.objects.filter(
				patient=patient_profile, id=medical_record_id
			).first()
			if not record:
				return Response(
					{"detail": "Medical record not found."},
					status=status.HTTP_404_NOT_FOUND,
				)

		user_message = ChatMessage.objects.create(
			conversation=conversation,
			sender_type="USER",
			message_text=input_serializer.validated_data["message_text"],
			medical_record=record,
		)

		if record is not None:
			assistant_text = services.generate_record_explanation(
				record, input_serializer.validated_data["message_text"]
			)
		else:
			assistant_text = input_serializer.validated_data.get(
				"assistant_message_text",
				"Thanks for sharing. I have recorded your symptoms.",
			)

		assistant_message = ChatMessage.objects.create(
			conversation=conversation,
			sender_type="ASSISTANT",
			message_text=assistant_text,
		)

		ctx = {"request": request}
		return Response(
			{
				"user_message": ChatMessageSerializer(user_message, context=ctx).data,
				"assistant_message": ChatMessageSerializer(assistant_message, context=ctx).data,
			},
			status=status.HTTP_201_CREATED,
		)
