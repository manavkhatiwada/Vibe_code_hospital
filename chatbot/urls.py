from django.urls import path

from .views import ChatConversationListCreateView, ChatConversationMessageListCreateView


urlpatterns = [
    path("chatbot/conversations/", ChatConversationListCreateView.as_view()),
    path(
        "chatbot/conversations/<uuid:conversation_id>/messages/",
        ChatConversationMessageListCreateView.as_view(),
    ),
]
