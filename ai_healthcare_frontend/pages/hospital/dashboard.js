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
    records: 0,
  });
  const [recentAppointments, setRecentAppointments] = useState([]);
  const [hospitalName, setHospitalName] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let mounted = true;
    Promise.all([api.get('/dashboard/stats/'), api.get('/hospitals/')])
      .then(([statsRes, hospitalsRes]) => {
        if (!mounted) return;

        const data = statsRes.data || {};
        setStats({
          doctors: data.total_doctors || 0,
          appointments: data.total_appointments || 0,
          patients: data.total_patients || 0,
          pending: data.pending_appointments || 0,
          completed: data.completed_appointments || 0,
          records: data.total_records || 0,
        });
        setRecentAppointments(data.recent_appointments || []);

        const hospitals = hospitalsRes.data || [];
        setHospitalName(hospitals[0]?.name || 'Assigned Hospital');
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

  return (
    <ProtectedRoute allowedRoles={['admin']} forbidSuperAdmin={true}>
      <div className="min-h-screen bg-gray-50 p-8">
        <div className="max-w-6xl mx-auto">
          <header className="flex justify-between items-center mb-10">
            <div>
              <h1 className="text-4xl font-extrabold text-blue-900 tracking-tight">Hospital Admin Console</h1>
              <p className="text-sm text-gray-600 mt-2">{hospitalName}</p>
            </div>
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
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-6 gap-6 mb-10">
              <StatCard title="Total Doctors" value={stats.doctors} color="bg-blue-100 text-blue-800" />
              <StatCard title="Total Patients" value={stats.patients} color="bg-green-100 text-green-800" />
              <StatCard title="Appointments" value={stats.appointments} color="bg-yellow-100 text-yellow-800" />
              <StatCard title="Pending" value={stats.pending} color="bg-orange-100 text-orange-800" />
              <StatCard title="Completed" value={stats.completed} color="bg-emerald-100 text-emerald-800" />
              <StatCard title="Records" value={stats.records} color="bg-indigo-100 text-indigo-800" />
            </div>
          )}

          <div className="bg-white p-6 rounded-2xl shadow-sm border border-gray-100">
            <h2 className="text-xl font-bold text-gray-800 mb-4">Quick Actions</h2>
            <div className="flex space-x-4">
              <Link href="/hospital/manage_doctors" className="px-6 py-3 bg-blue-600 text-white font-semibold rounded-lg shadow hover:bg-blue-700 transition">
                Manage Doctors
              </Link>
              <Link href="/hospital/appointments" className="px-6 py-3 bg-indigo-600 text-white font-semibold rounded-lg shadow hover:bg-indigo-700 transition">
                Manage Appointments
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
                      <span className="font-semibold">Doctor:</span> {appt.doctor_name || 'N/A'}
                    </p>
                    <p className="text-sm text-gray-700">
                      <span className="font-semibold">Patient:</span> {appt.patient_name || 'N/A'}
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
