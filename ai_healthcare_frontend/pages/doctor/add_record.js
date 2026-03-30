import { useEffect, useState } from 'react';
import ProtectedRoute from '../../components/ProtectedRoute';
import api from '../../utils/api';
import Link from 'next/link';
import { useRouter } from 'next/router';

export default function AddRecord() {
  const router = useRouter();
  const { patientId, appointmentId } = router.query;
  const [patients, setPatients] = useState([]);
  const [appointments, setAppointments] = useState([]);
  const [formData, setFormData] = useState({
    patient: '',
    appointment: '',
    diagnosis: '',
    prescription: '',
  });
  const [file, setFile] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [status, setStatus] = useState('');

  useEffect(() => {
    let mounted = true;
    Promise.all([api.get('/patients/'), api.get('/appointments/')])
      .then(([patientsRes, appointmentsRes]) => {
        if (!mounted) return;
        setPatients(patientsRes.data || []);
        setAppointments(appointmentsRes.data || []);
      })
      .catch(console.error);

    return () => {
      mounted = false;
    };
  }, []);

  useEffect(() => {
    setFormData((prev) => ({
      ...prev,
      patient: patientId || prev.patient,
      appointment: appointmentId || prev.appointment,
    }));
  }, [patientId, appointmentId]);

  const patientAppointments = appointments.filter(
    (appt) => !formData.patient || appt.patient === formData.patient || appt.patient?.id === formData.patient
  );

  const handleUpload = async (e) => {
    e.preventDefault();
    setStatus('');
    if (!formData.patient || !formData.diagnosis) {
      setStatus('Patient and diagnosis are required.');
      return;
    }

    setUploading(true);
    const data = new FormData();
    data.append('patient', formData.patient);
    if (formData.appointment) data.append('appointment', formData.appointment);
    data.append('diagnosis', formData.diagnosis);
    data.append('prescription', formData.prescription);
    if (file) data.append('report_file', file);

    try {
      await api.post('/records/', data, { headers: { 'Content-Type': 'multipart/form-data' } });
      setStatus('Record saved successfully. Redirecting...');
      setTimeout(() => {
        router.push(`/doctor/patient_history?patientId=${formData.patient}`);
      }, 1200);
    } catch (err) {
      setStatus(
        err.response?.data?.detail ||
        err.response?.data?.patient ||
        err.response?.data?.appointment ||
        'Upload failed. Verify your inputs.'
      );
    } finally {
      setUploading(false);
    }
  };

  return (
    <ProtectedRoute allowedRoles={['doctor']}>
      <div className="min-h-screen bg-gray-50 flex items-center justify-center p-8">
        <div className="bg-white p-8 rounded-xl shadow-lg w-full max-w-lg border border-gray-100">
          <Link href="/doctor/dashboard" className="text-blue-600 text-sm mb-4 block hover:underline">← Back to Dashboard</Link>
          <h2 className="text-2xl font-bold text-gray-800 mb-6">Add Medical Record</h2>
          {status && <div className={`p-3 rounded-lg text-sm mb-4 ${status.includes('successfully') ? 'bg-green-50 text-green-700' : 'bg-red-50 text-red-700'}`}>{status}</div>}

          <form onSubmit={handleUpload} className="space-y-5">
            <div>
              <label className="block text-gray-700 font-medium mb-1">Select Patient</label>
              <select required value={formData.patient} onChange={e => setFormData({ ...formData, patient: e.target.value })} className="w-full border px-4 py-2 rounded-lg focus:ring-2 focus:ring-blue-200 focus:border-blue-400">
                <option value="">Choose Patient...</option>
                {patients.map(p => <option key={p.id} value={p.id}>{p.user?.username || `Patient ${p.id.substring(0, 4)}`}</option>)}
              </select>
            </div>
            <div>
              <label className="block text-gray-700 font-medium mb-1">Link Appointment (Optional)</label>
              <select value={formData.appointment} onChange={e => setFormData({ ...formData, appointment: e.target.value })} className="w-full border px-4 py-2 rounded-lg focus:ring-2 focus:ring-blue-200 focus:border-blue-400">
                <option value="">No appointment</option>
                {patientAppointments.map((appt) => (
                  <option key={appt.id} value={appt.id}>
                    {appt.date} {appt.time ? `at ${appt.time}` : ''} - {appt.reason || 'Consultation'}
                  </option>
                ))}
              </select>
            </div>
            <div>
              <label className="block text-gray-700 font-medium mb-1">Diagnosis</label>
              <input type="text" required value={formData.diagnosis} onChange={e => setFormData({ ...formData, diagnosis: e.target.value })} className="w-full border px-4 py-2 rounded-lg focus:ring-2 focus:ring-blue-200 focus:border-blue-400" placeholder="e.g. Viral Fever" />
            </div>
            <div>
              <label className="block text-gray-700 font-medium mb-1">Prescription Notes</label>
              <textarea rows="3" value={formData.prescription} onChange={e => setFormData({ ...formData, prescription: e.target.value })} className="w-full border px-4 py-2 rounded-lg focus:ring-2 focus:ring-blue-200 focus:border-blue-400" placeholder="Medications, rest details..."></textarea>
            </div>
            <div>
              <label className="block text-gray-700 font-medium mb-1">Attach Final Report (Optional)</label>
              <input type="file" onChange={e => setFile(e.target.files[0])} className="w-full text-sm py-2 px-1 text-gray-600" />
            </div>
            <button type="submit" disabled={uploading} className="w-full bg-blue-600 text-white font-bold py-3 rounded-lg hover:bg-blue-700 transition disabled:bg-blue-300">
              {uploading ? 'Saving...' : 'Save Record'}
            </button>
          </form>
        </div>
      </div>
    </ProtectedRoute>
  );
}
