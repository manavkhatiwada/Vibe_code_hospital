import { useEffect, useState } from 'react';
import ProtectedRoute from '../../components/ProtectedRoute';
import api from '../../utils/api';
import Link from 'next/link';

export default function DoctorAppointments() {
  const [appointments, setAppointments] = useState([]);
  const [patients, setPatients] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    let mounted = true;
    Promise.all([api.get('/appointments/'), api.get('/patients/')])
      .then(([appointmentsRes, patientsRes]) => {
        if (!mounted) return;
        setAppointments(appointmentsRes.data || []);
        setPatients(patientsRes.data || []);
      })
      .catch(() => {
        if (!mounted) return;
        setError('Failed to load appointments. Please refresh the page.');
      })
      .finally(() => {
        if (mounted) setLoading(false);
      });

    return () => {
      mounted = false;
    };
  }, []);

  const patientName = (patientId) => {
    const patient = patients.find((p) => p.id === patientId || p.user?.id === patientId);
    if (!patient) return 'Unknown Patient';
    return patient.user?.username || 'Unknown Patient';
  };

  return (
    <ProtectedRoute allowedRoles={['doctor']}>
      <div className="min-h-screen bg-gray-50 p-8">
        <div className="max-w-5xl mx-auto">
          <div className="flex items-center space-x-4 mb-8">
            <Link href="/doctor/dashboard" className="text-blue-600 hover:underline">← Back to Dashboard</Link>
            <h1 className="text-3xl font-bold text-gray-800">My Schedule</h1>
          </div>

          {loading ? (
            <div className="text-center py-20 text-gray-500">Loading Appointments...</div>
          ) : error ? (
            <div className="text-center py-20 text-red-600">{error}</div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {appointments.length === 0 ? (
                <p className="text-gray-500">No upcoming appointments.</p>
              ) : (
                appointments.map(appt => (
                  <div key={appt.id} className="bg-white p-6 rounded-xl shadow-sm border border-gray-100 hover:shadow-md transition">
                    <div className="flex justify-between items-start mb-4">
                      <div>
                        <h3 className="text-xl font-semibold text-gray-900">{patientName(appt.patient)}</h3>
                      </div>
                      <span className={`px-3 py-1 text-xs font-bold rounded-full ${appt.status?.toLowerCase() === 'completed' ? 'bg-green-100 text-green-700' :
                        appt.status?.toLowerCase() === 'pending' ? 'bg-yellow-100 text-yellow-700' :
                          'bg-gray-100 text-gray-700'
                        }`}>
                        {appt.status?.toUpperCase() || 'PENDING'}
                      </span>
                    </div>
                    <div className="space-y-2 mb-6">
                      <p className="text-sm text-gray-600"><span className="font-semibold">Date:</span> {appt.date}</p>
                      <p className="text-sm text-gray-600"><span className="font-semibold">Time:</span> {appt.time}</p>
                      <p className="text-sm text-gray-600 line-clamp-2"><span className="font-semibold">Reason:</span> {appt.reason}</p>
                    </div>
                    <div className="grid grid-cols-2 gap-2">
                      <Link href={`/doctor/patient_history?patientId=${appt.patient}`} className="block text-center border font-semibold border-gray-400 text-gray-700 py-2 rounded-lg hover:bg-gray-50 transition">
                        View History
                      </Link>
                      <Link href={`/doctor/add_record?patientId=${appt.patient}&appointmentId=${appt.id}`} className="block text-center border font-semibold border-blue-600 text-blue-600 py-2 rounded-lg hover:bg-blue-50 transition">
                        Add Record
                      </Link>
                    </div>
                  </div>
                ))
              )}
            </div>
          )}
        </div>
      </div>
    </ProtectedRoute>
  );
}
