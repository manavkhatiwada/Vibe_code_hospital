import { useEffect, useState } from 'react';
import ProtectedRoute from '../../components/ProtectedRoute';
import Link from 'next/link';
import api from '../../utils/api';

const STAT_CONFIG = [
  { key: 'assignedPatients', label: 'Assigned Patients', icon: '🧑‍🤝‍🧑', color: 'bg-teal-50 text-teal-700 border-teal-200',     dot: 'bg-teal-500' },
  { key: 'appointments',     label: 'Appointments',      icon: '📅',          color: 'bg-blue-50 text-blue-700 border-blue-200',     dot: 'bg-blue-500' },
  { key: 'pending',          label: 'Pending',            icon: '⏳',          color: 'bg-amber-50 text-amber-700 border-amber-200',  dot: 'bg-amber-500' },
  { key: 'completed',        label: 'Completed',          icon: '✅',          color: 'bg-emerald-50 text-emerald-700 border-emerald-200', dot: 'bg-emerald-500' },
  { key: 'records',          label: 'Records',            icon: '📋',          color: 'bg-indigo-50 text-indigo-700 border-indigo-200', dot: 'bg-indigo-500' },
];

const ACTIONS = [
  { title: 'My Appointments',    desc: 'View your schedule and patient bookings',                    link: '/doctor/appointments',    icon: '📅', from: 'from-blue-500',    to: 'to-blue-700' },
  { title: 'Add Medical Record', desc: 'Create notes, prescriptions and upload patient reports',     link: '/doctor/add_record',      icon: '📝', from: 'from-teal-500',    to: 'to-teal-700' },
  { title: 'Patient History',    desc: 'Browse previous diagnoses and records for your patients',   link: '/doctor/patient_history', icon: '🏥', from: 'from-indigo-500',  to: 'to-indigo-700' },
];

export default function DoctorDashboard() {
  const [stats, setStats]     = useState({ assignedPatients: 0, appointments: 0, pending: 0, completed: 0, records: 0 });
  const [profile, setProfile] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let mounted = true;
    Promise.all([
      api.get('/dashboard/stats/').catch(() => ({ data: {} })),
      api.get('/profile/').catch(() => ({ data: {} })),
    ]).then(([statsRes, profileRes]) => {
      if (!mounted) return;
      const d = statsRes.data || {};
      setStats({
        assignedPatients: d.assigned_patients       || 0,
        appointments:     d.my_appointments         || 0,
        pending:          d.pending_appointments    || 0,
        completed:        d.completed_appointments  || 0,
        records:          d.my_records              || 0,
      });
      setProfile(profileRes.data || null);
    }).finally(() => { if (mounted) setLoading(false); });
    return () => { mounted = false; };
  }, []);

  const name = profile?.username || 'Doctor';
  const hour = new Date().getHours();
  const greeting = hour < 12 ? 'Good morning' : hour < 17 ? 'Good afternoon' : 'Good evening';

  return (
    <ProtectedRoute allowedRoles={['doctor']}>
      <div className="min-h-screen bg-gray-50">
        {/* ── Navbar ── */}
        <nav className="bg-white border-b border-gray-100 px-6 py-4 flex items-center justify-between sticky top-0 z-20 shadow-sm">
          <div className="flex items-center gap-2.5">
            <div className="w-9 h-9 bg-teal-600 rounded-xl flex items-center justify-center shadow">
              <span className="text-white font-black text-base">+</span>
            </div>
            <span className="text-lg font-bold text-teal-700 tracking-tight">Open Care</span>
            <span className="ml-2 text-xs font-semibold bg-teal-100 text-teal-700 px-2 py-0.5 rounded-full">Doctor</span>
          </div>
          <div className="flex items-center gap-4">
            <div className="w-9 h-9 rounded-full bg-teal-100 flex items-center justify-center text-teal-700 font-bold text-sm uppercase">
              {name.charAt(0)}
            </div>
            <span className="text-sm font-medium text-gray-700 hidden sm:block">Dr. {name}</span>
            <button
              onClick={() => { localStorage.clear(); window.location.href = '/auth/login'; }}
              className="text-sm font-semibold text-red-500 hover:text-red-700 transition"
            >
              Logout
            </button>
          </div>
        </nav>

        <div className="max-w-6xl mx-auto px-6 py-10">
          {/* ── Welcome banner ── */}
          <div className="bg-linear-to-br from-teal-600 via-teal-700 to-emerald-800 rounded-2xl p-8 mb-8 text-white relative overflow-hidden shadow-lg">
            <div className="absolute -top-10 -right-10 w-52 h-52 bg-white/10 rounded-full" />
            <div className="absolute bottom-0 right-32 w-32 h-32 bg-white/5 rounded-full" />
            <div className="relative z-10">
              <p className="text-teal-200 text-sm font-medium mb-1">{greeting}, Doctor</p>
              <h1 className="text-3xl font-extrabold mb-1 capitalize">Dr. {name} 🩺</h1>
              <p className="text-teal-100 text-sm">Manage your patients, appointments, and medical records below.</p>
            </div>
          </div>

          {/* ── Stat cards ── */}
          {loading ? (
            <div className="grid grid-cols-2 sm:grid-cols-5 gap-4 mb-8">
              {[...Array(5)].map((_, i) => (
                <div key={i} className="h-24 bg-gray-200 rounded-xl animate-pulse" />
              ))}
            </div>
          ) : (
            <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-4 mb-8">
              {STAT_CONFIG.map(({ key, label, icon, color, dot }) => (
                <div key={key} className={`bg-white border rounded-xl p-4 flex flex-col gap-2 shadow-sm hover:shadow-md transition ${color}`}>
                  <div className="flex items-center justify-between">
                    <span className="text-xl">{icon}</span>
                    <span className={`w-2 h-2 rounded-full ${dot}`} />
                  </div>
                  <p className="text-2xl font-extrabold">{stats[key]}</p>
                  <p className="text-xs font-medium leading-tight">{label}</p>
                </div>
              ))}
            </div>
          )}

          {/* ── Section title ── */}
          <h2 className="text-lg font-bold text-gray-800 mb-4">Quick Actions</h2>

          {/* ── Action cards ── */}
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-5">
            {ACTIONS.map(({ title, desc, link, icon, from, to }) => (
              <Link key={title} href={link}>
                <div className="group bg-white rounded-2xl shadow-sm hover:shadow-xl border border-gray-100 overflow-hidden transition-all duration-300 hover:-translate-y-1 cursor-pointer">
                  <div className={`bg-linear-to-br ${from} ${to} h-28 flex items-center justify-center text-6xl`}>
                    {icon}
                  </div>
                  <div className="p-5">
                    <h3 className="font-bold text-gray-900 mb-1">{title}</h3>
                    <p className="text-sm text-gray-500 leading-relaxed">{desc}</p>
                    <span className="inline-block mt-3 text-xs font-semibold text-teal-600 group-hover:underline">Go →</span>
                  </div>
                </div>
              </Link>
            ))}
          </div>

          {/* ── Info callout ── */}
          <div className="mt-8 bg-blue-50 border border-blue-100 rounded-2xl p-5 flex items-start gap-4">
            <span className="text-2xl shrink-0">💡</span>
            <div>
              <p className="font-semibold text-blue-900 mb-0.5">No hospital assigned yet?</p>
              <p className="text-sm text-blue-700">Your account is active. A hospital admin can link you to their facility so patients can find and book you.</p>
            </div>
          </div>
        </div>
      </div>
    </ProtectedRoute>
  );
}
