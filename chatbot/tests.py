from rest_framework.test import APITestCase

from users.models import User


class ChatbotApiTests(APITestCase):
	def setUp(self):
		self.password = "S3cretPass!123"
		self.user = User.objects.create_user(
			username="chatuser",
			email="chatuser@example.com",
			password=self.password,
			role="PATIENT",
		)

	def _auth(self):
		login = self.client.post(
			"/api/login/",
			{"email": self.user.email, "password": self.password},
			format="json",
		)
		self.assertEqual(login.status_code, 200, login.data)
		self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {login.data['access']}")

	def test_requires_auth_for_conversation_list(self):
		response = self.client.get("/api/chatbot/conversations/")
		self.assertEqual(response.status_code, 401)

	def test_create_list_and_message_flow(self):
		self._auth()

		created = self.client.post("/api/chatbot/conversations/", {}, format="json")
		self.assertEqual(created.status_code, 201, created.data)
		conversation_id = created.data["id"]

		listed = self.client.get("/api/chatbot/conversations/")
		self.assertEqual(listed.status_code, 200, listed.data)
		self.assertGreaterEqual(len(listed.data), 1)

		sent = self.client.post(
			f"/api/chatbot/conversations/{conversation_id}/messages/",
			{"message_text": "I have a headache"},
			format="json",
		)
		self.assertEqual(sent.status_code, 201, sent.data)
		self.assertEqual(sent.data["user_message"]["sender_type"], "USER")
		self.assertEqual(sent.data["assistant_message"]["sender_type"], "ASSISTANT")

		history = self.client.get(
			f"/api/chatbot/conversations/{conversation_id}/messages/"
		)
		self.assertEqual(history.status_code, 200, history.data)
		self.assertEqual(len(history.data), 2)
