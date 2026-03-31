import { useEffect, useMemo, useState } from 'react';
import ProtectedRoute from '../../components/ProtectedRoute';
import api from '../../utils/api';
import { useRouter } from 'next/router';
import Link from 'next/link';

export default function BookAppointment() {
  const router = useRouter();
  const { doctorId } = router.query;
  const [formData, setFormData] = useState({ date: '', time: '', reason: '', doctor: '' });
  const [status, setStatus] = useState('');
  const [submitting, setSubmitting] = useState(false);
  const [loadingDoctors, setLoadingDoctors] = useState(true);
  const [doctors, setDoctors] = useState([]);

  useEffect(() => {
    let mounted = true;
    api.get('/doctors/')
      .then((res) => {
        if (mounted) {
          setDoctors(res.data || []);
        }
      })
      .catch(() => {
        if (mounted) {
          setDoctors([]);
        }
      })
      .finally(() => {
        if (mounted) {
          setLoadingDoctors(false);
        }
      });

    return () => {
      mounted = false;
    };
  }, []);

  useEffect(() => {
    if (doctorId) {
      setFormData((prev) => ({ ...prev, doctor: doctorId }));
    }
  }, [doctorId]);

  const minDate = useMemo(() => {
    const d = new Date();
    d.setHours(0, 0, 0, 0);
    return d.toISOString().split('T')[0];
  }, []);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setStatus('');

    if (!formData.doctor) {
      setStatus('Please select a doctor first.');
      return;
    }

    const selectedDateTime = new Date(`${formData.date}T${formData.time}`);
    if (Number.isNaN(selectedDateTime.getTime()) || selectedDateTime <= new Date()) {
      setStatus('Please choose a future date and time.');
      return;
    }

    setSubmitting(true);

    try {
      await api.post('/appointments/', {
        doctor: formData.doctor,
        date: formData.date,
        time: formData.time,
        reason: formData.reason,
      });
      setStatus('Success! Your appointment has been requested.');
      setTimeout(() => router.push('/patient/appointments'), 2000);
    } catch (err) {
      setStatus(
        err?.response?.data?.appointment_datetime ||
        err?.response?.data?.detail ||
        'Failed to book appointment. Please verify your inputs.'
      );
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <ProtectedRoute allowedRoles={['patient']}>
      <div className="min-h-screen bg-gray-50 flex items-center justify-center p-8">
        <div className="bg-white p-8 rounded-xl shadow-lg w-full max-w-lg">
          <Link href="/patient/doctor_list" className="text-blue-600 text-sm mb-4 block hover:underline">← Back to Doctors</Link>
          <h2 className="text-2xl font-bold text-gray-800 mb-6">Book Appointment</h2>

          {status && <div className={`p-4 mb-6 text-sm rounded ${status.includes('Success') ? 'bg-green-50 text-green-700' : 'bg-red-50 text-red-700'}`}>{status}</div>}

          <form onSubmit={handleSubmit} className="space-y-5">
            <div>
              <label className="block text-gray-700 font-medium mb-1">Doctor</label>
              <select
                required
                value={formData.doctor}
                onChange={e => setFormData({ ...formData, doctor: e.target.value })}
                className="w-full border px-4 py-2 rounded-lg text-gray-900 bg-white"
                disabled={loadingDoctors || submitting}
              >
                <option value="">Select a doctor</option>
                {doctors.map((doc) => (
                  <option key={doc.id} value={doc.id}>
                    Dr. {doc.user_username || 'Unknown Doctor'} - {doc.specialization || 'General'}
                  </option>
                ))}
              </select>
            </div>
            <div>
              <label className="block text-gray-700 font-medium mb-1">Date</label>
              <input type="date" required min={minDate} value={formData.date} onChange={e => setFormData({ ...formData, date: e.target.value })} className="w-full border px-4 py-2 rounded-lg" />
            </div>
            <div>
              <label className="block text-gray-700 font-medium mb-1">Time</label>
              <input type="time" required value={formData.time} onChange={e => setFormData({ ...formData, time: e.target.value })} className="w-full border px-4 py-2 rounded-lg" />
            </div>
            <div>
              <label className="block text-gray-700 font-medium mb-1">Reason for Visit</label>
              <textarea required rows="3" value={formData.reason} onChange={e => setFormData({ ...formData, reason: e.target.value })} className="w-full border px-4 py-2 rounded-lg" placeholder="Briefly describe your symptoms..."></textarea>
            </div>
            <button type="submit" disabled={submitting || loadingDoctors} className="w-full bg-blue-600 text-white font-bold py-3 rounded-lg hover:bg-blue-700 disabled:bg-blue-300 disabled:cursor-not-allowed transition">
              {submitting ? 'Booking...' : 'Confirm Booking'}
            </button>
          </form>
        </div>
      </div>
    </ProtectedRoute>
  );
}
