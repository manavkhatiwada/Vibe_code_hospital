import { useEffect, useState } from 'react';
import ProtectedRoute from '../../components/ProtectedRoute';
import api from '../../utils/api';
import Link from 'next/link';

export default function PatientAppointments() {
  const [appointments, setAppointments] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.get('/appointments/')
      .then(res => {
        setAppointments(res.data);
        setLoading(false);
      })
      .catch(err => {
        console.error("Failed to load appointments", err);
        setLoading(false);
      });
  }, []);

  return (
    <ProtectedRoute allowedRoles={['patient']}>
      <div className="min-h-screen bg-gray-50 p-8">
        <div className="max-w-5xl mx-auto">
          <div className="flex items-center space-x-4 mb-8">
            <Link href="/patient/dashboard" className="text-blue-600 hover:underline">← Back to Dashboard</Link>
            <h1 className="text-3xl font-bold text-gray-800">My Appointments</h1>
          </div>

          {loading ? (
            <div className="text-center py-20 text-gray-500">Loading Appointments...</div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {appointments.length === 0 ? (
                <p className="text-gray-500">You have no appointments booked.</p>
              ) : (
                appointments.map(appt => (
                  <div key={appt.id} className="bg-white p-6 rounded-xl shadow-sm border border-gray-100 hover:shadow-md transition">
                    <div className="flex justify-between items-start mb-4">
                      <div>
                        <h3 className="text-xl font-semibold text-gray-900">
                          Dr. {appt.doctor?.user?.username || appt.doctor || 'Unknown'}
                        </h3>
                      </div>
                      <span className={`px-3 py-1 text-xs font-bold rounded-full ${
                        appt.status?.toLowerCase() === 'completed' ? 'bg-green-100 text-green-700' :
                        appt.status?.toLowerCase() === 'pending' ? 'bg-yellow-100 text-yellow-700' :
                        'bg-gray-100 text-gray-700'
                      }`}>
                        {appt.status?.toUpperCase() || 'PENDING'}
                      </span>
                    </div>
                    <div className="space-y-2 mb-4">
                      <p className="text-sm text-gray-600"><span className="font-semibold">Date:</span> {appt.date}</p>
                      <p className="text-sm text-gray-600"><span className="font-semibold">Time:</span> {appt.time}</p>
                      <p className="text-sm text-gray-600 line-clamp-2"><span className="font-semibold">Reason:</span> {appt.reason}</p>
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
