import { useEffect, useState } from 'react';
import ProtectedRoute from '../../components/ProtectedRoute';
import Link from 'next/link';
import api from '../../utils/api';

export default function DoctorDashboard() {
  const [stats, setStats] = useState({
    assignedPatients: 0,
    appointments: 0,
    pending: 0,
    completed: 0,
    records: 0,
  });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let mounted = true;
    api.get('/dashboard/stats/')
      .then((res) => {
        if (!mounted) return;
        const data = res.data || {};
        setStats({
          assignedPatients: data.assigned_patients || 0,
          appointments: data.my_appointments || 0,
          pending: data.pending_appointments || 0,
          completed: data.completed_appointments || 0,
          records: data.my_records || 0,
        });
      })
      .catch(() => {
        if (!mounted) return;
      })
      .finally(() => {
        if (mounted) setLoading(false);
      });

    return () => {
      mounted = false;
    };
  }, []);

  return (
    <ProtectedRoute allowedRoles={['doctor']}>
      <div className="min-h-screen bg-gray-50 p-8">
        <div className="max-w-6xl mx-auto">
          <header className="flex justify-between items-center mb-10">
            <h1 className="text-4xl font-extrabold text-blue-900 tracking-tight">Doctor Dashboard</h1>
            <button className="text-sm font-medium text-red-600 hover:text-red-800" onClick={() => { localStorage.clear(); window.location.href = '/auth/login'; }}>Logout</button>
          </header>

          {loading ? (
            <div className="text-center py-8 text-gray-500">Loading stats...</div>
          ) : (
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-4 mb-8">
              <StatCard title="Assigned Patients" value={stats.assignedPatients} />
              <StatCard title="Appointments" value={stats.appointments} />
              <StatCard title="Pending" value={stats.pending} />
              <StatCard title="Completed" value={stats.completed} />
              <StatCard title="Records" value={stats.records} />
            </div>
          )}

          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
            <DashboardCard title="My Appointments" desc="View your schedule and patients" link="/doctor/appointments" icon="📅" />
            <DashboardCard title="Add Medical Record" desc="Add diagnosis and prescriptions" link="/doctor/add_record" icon="📝" />
            <DashboardCard title="Patient History" desc="View previous records of patients" link="/doctor/patient_history" icon="🏥" />
          </div>
        </div>
      </div>
    </ProtectedRoute>
  );
}

function StatCard({ title, value }) {
  return (
    <div className="bg-white p-4 rounded-xl border border-gray-100 shadow-sm">
      <p className="text-sm text-gray-500">{title}</p>
      <p className="text-2xl font-bold text-gray-900 mt-1">{value}</p>
    </div>
  );
}

function DashboardCard({ title, desc, link, icon }) {
  return (
    <Link href={link}>
      <div className="bg-white p-6 rounded-2xl shadow-sm hover:shadow-xl border border-gray-100 cursor-pointer transition-all duration-300 transform hover:-translate-y-2 group">
        <div className="text-5xl mb-4 group-hover:scale-110 transition-transform">{icon}</div>
        <h3 className="text-xl font-bold text-gray-800 mb-2">{title}</h3>
        <p className="text-gray-500 text-sm leading-relaxed">{desc}</p>
      </div>
    </Link>
  );
}
