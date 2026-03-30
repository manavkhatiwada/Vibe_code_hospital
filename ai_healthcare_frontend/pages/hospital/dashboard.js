import { useEffect, useState } from 'react';
import ProtectedRoute from '../../components/ProtectedRoute';
import api from '../../utils/api';
import Link from 'next/link';

export default function HospitalDashboard() {
  const [stats, setStats] = useState({
    doctors: 0,
    appointments: 0,
    patients: 0,
    pending: 0,
    completed: 0,
  });
  const [recentAppointments, setRecentAppointments] = useState([]);
  const [doctors, setDoctors] = useState([]);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let mounted = true;
    Promise.all([api.get('/doctors/'), api.get('/appointments/')])
      .then(([doctorsRes, appointmentsRes]) => {
        if (!mounted) return;

        const doctorsData = doctorsRes.data || [];
        const appointmentsData = appointmentsRes.data || [];

        const uniquePatients = new Set(
          appointmentsData
            .map((appt) => appt.patient)
            .filter(Boolean)
        );

        const pendingCount = appointmentsData.filter(
          (appt) => String(appt.status || '').toUpperCase() === 'PENDING'
        ).length;
        const completedCount = appointmentsData.filter(
          (appt) => String(appt.status || '').toUpperCase() === 'COMPLETED'
        ).length;

        setDoctors(doctorsData);
        setStats({
          doctors: doctorsData.length,
          appointments: appointmentsData.length,
          patients: uniquePatients.size,
          pending: pendingCount,
          completed: completedCount,
        });

        setRecentAppointments(appointmentsData.slice(0, 5));
      })
      .catch(() => {
        if (!mounted) return;
        setError('Failed to load hospital metrics. Please refresh.');
      })
      .finally(() => {
        if (mounted) setLoading(false);
      });

    return () => {
      mounted = false;
    };
  }, []);

  const doctorName = (doctorId) => {
    const doctor = doctors.find((d) => d.id === doctorId);
    if (!doctor) return `Doctor ${String(doctorId || 'N/A').slice(0, 4)}`;
    return doctor.user_username || `Doctor ${doctor.id.slice(0, 4)}`;
  };

  return (
    <ProtectedRoute allowedRoles={['hospital']}>
      <div className="min-h-screen bg-gray-50 p-8">
        <div className="max-w-6xl mx-auto">
          <header className="flex justify-between items-center mb-10">
            <h1 className="text-4xl font-extrabold text-blue-900 tracking-tight">Hospital Admin Console</h1>
            <button className="text-sm font-medium text-red-600 hover:text-red-800" onClick={() => { localStorage.clear(); window.location.href = '/auth/login'; }}>Logout</button>
          </header>

          {error && (
            <div className="mb-6 p-4 rounded-lg bg-red-50 text-red-700 text-sm">
              {error}
            </div>
          )}

          {loading ? (
            <div className="text-center py-10 text-gray-500">Loading Metrics...</div>
          ) : (
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-6 mb-10">
              <StatCard title="Total Doctors" value={stats.doctors} color="bg-blue-100 text-blue-800" />
              <StatCard title="Total Patients" value={stats.patients} color="bg-green-100 text-green-800" />
              <StatCard title="Appointments" value={stats.appointments} color="bg-yellow-100 text-yellow-800" />
              <StatCard title="Pending" value={stats.pending} color="bg-orange-100 text-orange-800" />
              <StatCard title="Completed" value={stats.completed} color="bg-emerald-100 text-emerald-800" />
            </div>
          )}

          <div className="bg-white p-6 rounded-2xl shadow-sm border border-gray-100">
            <h2 className="text-xl font-bold text-gray-800 mb-4">Quick Actions</h2>
            <div className="flex space-x-4">
              <Link href="/hospital/manage_doctors" className="px-6 py-3 bg-blue-600 text-white font-semibold rounded-lg shadow hover:bg-blue-700 transition">
                Manage Doctors
              </Link>
            </div>
          </div>

          <div className="bg-white p-6 rounded-2xl shadow-sm border border-gray-100 mt-8">
            <h2 className="text-xl font-bold text-gray-800 mb-4">Recent Appointments</h2>
            {loading ? (
              <div className="text-gray-500">Loading...</div>
            ) : recentAppointments.length === 0 ? (
              <div className="text-gray-500">No appointments found.</div>
            ) : (
              <div className="space-y-3">
                {recentAppointments.map((appt) => (
                  <div key={appt.id} className="border border-gray-100 rounded-lg p-3">
                    <p className="text-sm text-gray-700">
                      <span className="font-semibold">Doctor:</span> {doctorName(appt.doctor)}
                    </p>
                    <p className="text-sm text-gray-700">
                      <span className="font-semibold">Patient ID:</span> {appt.patient}
                    </p>
                    <p className="text-sm text-gray-700">
                      <span className="font-semibold">Date:</span> {appt.date} {appt.time ? `at ${appt.time}` : ''}
                    </p>
                    <p className="text-sm text-gray-700">
                      <span className="font-semibold">Status:</span> {appt.status}
                    </p>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>
    </ProtectedRoute>
  );
}

function StatCard({ title, value, color }) {
  return (
    <div className={`p-6 rounded-2xl shadow-sm border border-gray-100 flex flex-col items-center justify-center ${color}`}>
      <h3 className="text-lg font-medium opacity-80 mb-2">{title}</h3>
      <div className="text-5xl font-black">{value}</div>
    </div>
  );
}
