from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

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
		serializer = ChatMessageSerializer(messages, many=True)
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

		user_message = ChatMessage.objects.create(
			conversation=conversation,
			sender_type="USER",
			message_text=input_serializer.validated_data["message_text"],
		)

		assistant_text = input_serializer.validated_data.get(
			"assistant_message_text",
			"Thanks for sharing. I have recorded your symptoms.",
		)

		assistant_message = ChatMessage.objects.create(
			conversation=conversation,
			sender_type="ASSISTANT",
			message_text=assistant_text,
		)

		return Response(
			{
				"user_message": ChatMessageSerializer(user_message).data,
				"assistant_message": ChatMessageSerializer(assistant_message).data,
			},
			status=status.HTTP_201_CREATED,
		)
