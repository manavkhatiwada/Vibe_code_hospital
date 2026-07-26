from unittest import mock

from rest_framework.test import APITestCase

from medical_records.models import MedicalRecord
from patients.models import Patient
from users.models import User

from . import services


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

	def test_doctor_cannot_access_chatbot_endpoints(self):
		doctor = User.objects.create_user(
			username="chatdoctor",
			email="chatdoctor@example.com",
			password=self.password,
			role="DOCTOR",
		)
		login = self.client.post(
			"/api/login/",
			{"email": doctor.email, "password": self.password},
			format="json",
		)
		self.assertEqual(login.status_code, 200, login.data)
		self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {login.data['access']}")

		response = self.client.get("/api/chatbot/conversations/")
		self.assertEqual(response.status_code, 403)

	def test_admin_cannot_access_chatbot_endpoints(self):
		admin = User.objects.create_user(
			username="chatadmin",
			email="chatadmin@example.com",
			password=self.password,
			role="ADMIN",
		)
		login = self.client.post(
			"/api/login/",
			{"email": admin.email, "password": self.password},
			format="json",
		)
		self.assertEqual(login.status_code, 200, login.data)
		self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {login.data['access']}")

		response = self.client.post("/api/chatbot/conversations/", {}, format="json")
		self.assertEqual(response.status_code, 403)


class ChatbotRecordAttachmentTests(APITestCase):
	def setUp(self):
		self.password = "S3cretPass!123"
		self.user = User.objects.create_user(
			username="chatuser2",
			email="chatuser2@example.com",
			password=self.password,
			role="PATIENT",
		)
		self.other_user = User.objects.create_user(
			username="otherpatient",
			email="other@example.com",
			password=self.password,
			role="PATIENT",
		)

	def _auth(self, user):
		login = self.client.post(
			"/api/login/", {"email": user.email, "password": self.password}, format="json"
		)
		self.assertEqual(login.status_code, 200, login.data)
		self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {login.data['access']}")

	def test_cannot_attach_another_patients_record(self):
		self._auth(self.user)
		other_patient, _ = Patient.objects.get_or_create(user=self.other_user)
		other_record = MedicalRecord.objects.create(
			patient=other_patient, notes="not yours", folder_name="General"
		)

		conv = self.client.post("/api/chatbot/conversations/", {}, format="json")
		response = self.client.post(
			f"/api/chatbot/conversations/{conv.data['id']}/messages/",
			{"message_text": "explain this", "medical_record_id": str(other_record.id)},
			format="json",
		)
		self.assertEqual(response.status_code, 404)

	@mock.patch("chatbot.views.services.generate_record_explanation")
	def test_attach_own_record_calls_service_and_ignores_client_assistant_text(self, mock_generate):
		mock_generate.return_value = "Plain language explanation. See a doctor if concerned."
		self._auth(self.user)
		patient, _ = Patient.objects.get_or_create(user=self.user)
		record = MedicalRecord.objects.create(patient=patient, notes="CBC results", folder_name="Lab Report")

		conv = self.client.post("/api/chatbot/conversations/", {}, format="json")
		response = self.client.post(
			f"/api/chatbot/conversations/{conv.data['id']}/messages/",
			{
				"message_text": "what does this mean?",
				"medical_record_id": str(record.id),
				"assistant_message_text": "IGNORE ME - client should not control this",
			},
			format="json",
		)
		self.assertEqual(response.status_code, 201, response.data)
		self.assertEqual(
			response.data["assistant_message"]["message_text"],
			"Plain language explanation. See a doctor if concerned.",
		)
		self.assertEqual(
			response.data["user_message"]["medical_record"]["id"], str(record.id)
		)
		mock_generate.assert_called_once()


class ChatbotServicesTests(APITestCase):
	@mock.patch("chatbot.services.requests.post")
	def test_gemini_payload_uses_correct_field_casing(self, mock_post):
		mock_post.return_value.status_code = 200
		mock_post.return_value.json.return_value = {
			"candidates": [{"content": {"parts": [{"text": "ok"}]}}]
		}

		with mock.patch("chatbot.services._get_gemini_api_key", return_value="fake-key"):
			record = MedicalRecord(notes="n", folder_name="f")
			result = services.generate_record_explanation(record, "hi")

		self.assertEqual(result, "ok")
		sent_json = mock_post.call_args.kwargs["json"]
		self.assertIn("system_instruction", sent_json)
		self.assertIn("contents", sent_json)
		self.assertNotIn("systemInstruction", sent_json)
