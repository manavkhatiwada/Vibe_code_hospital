from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from django.db.models import Q

from appointments.models import Appointment
from doctors.models import Doctor
from hospitals.models import Hospital
from medical_records.models import MedicalRecord
from patients.models import Patient


class DashboardStatsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        role = getattr(user, "role", None)

        if role == "ADMIN":
            hospitals = Hospital.objects.filter(admin=user)
            doctors_qs = Doctor.objects.filter(
                Q(hospital__in=hospitals)
                | Q(hospital_memberships__hospital__in=hospitals, hospital_memberships__is_active=True)
            ).distinct()
            appointments_qs = Appointment.objects.filter(
                Q(hospital__in=hospitals)
                | Q(doctor__hospital_memberships__hospital__in=hospitals, doctor__hospital_memberships__is_active=True)
            ).distinct()
            records_qs = MedicalRecord.objects.filter(
                Q(doctor__hospital__in=hospitals)
                | Q(doctor__hospital_memberships__hospital__in=hospitals, doctor__hospital_memberships__is_active=True)
            ).distinct()

            unique_patient_ids = set(
                appointments_qs.values_list("patient_id", flat=True)
            )

            recent = (
                appointments_qs.select_related("doctor__user", "patient__user")
                .order_by("-appointment_datetime")[:5]
            )

            return Response(
                {
                    "role": "ADMIN",
                    "total_doctors": doctors_qs.count(),
                    "total_patients": len([pid for pid in unique_patient_ids if pid]),
                    "total_appointments": appointments_qs.count(),
                    "pending_appointments": appointments_qs.filter(status="PENDING").count(),
                    "completed_appointments": appointments_qs.filter(status="COMPLETED").count(),
                    "total_records": records_qs.count(),
                    "recent_appointments": [
                        {
                            "id": str(appt.id),
                            "doctor_name": appt.doctor.user.username,
                            "patient_name": appt.patient.user.username,
                            "status": appt.status,
                            "date": appt.appointment_datetime.date().isoformat(),
                            "time": appt.appointment_datetime.time().isoformat(timespec="seconds"),
                        }
                        for appt in recent
                    ],
                }
            )

        if role == "DOCTOR" and hasattr(user, "doctor"):
            appointments_qs = Appointment.objects.filter(doctor=user.doctor)
            records_qs = MedicalRecord.objects.filter(doctor=user.doctor)
            assigned_patient_ids = set(
                list(appointments_qs.values_list("patient_id", flat=True))
                + list(records_qs.values_list("patient_id", flat=True))
            )

            return Response(
                {
                    "role": "DOCTOR",
                    "assigned_patients": len([pid for pid in assigned_patient_ids if pid]),
                    "my_appointments": appointments_qs.count(),
                    "pending_appointments": appointments_qs.filter(status="PENDING").count(),
                    "completed_appointments": appointments_qs.filter(status="COMPLETED").count(),
                    "my_records": records_qs.count(),
                }
            )

        if role == "PATIENT":
            patient_profile, _ = Patient.objects.get_or_create(user=user)
            appointments_qs = Appointment.objects.filter(patient=patient_profile)
            records_qs = MedicalRecord.objects.filter(patient=patient_profile)

            return Response(
                {
                    "role": "PATIENT",
                    "available_doctors": Doctor.objects.count(),
                    "my_appointments": appointments_qs.count(),
                    "pending_appointments": appointments_qs.filter(status="PENDING").count(),
                    "completed_appointments": appointments_qs.filter(status="COMPLETED").count(),
                    "my_records": records_qs.count(),
                }
            )

        return Response(
            {
                "role": role,
                "detail": "No dashboard stats available for this user.",
            },
            status=403,
        )
