import ProtectedRoute from '../../components/ProtectedRoute';
import Link from 'next/link';

export default function PatientDashboard() {
  return (
    <ProtectedRoute allowedRoles={['patient']}>
      <div className="min-h-screen bg-gray-50 p-8">
        <div className="max-w-6xl mx-auto">
          <header className="flex justify-between items-center mb-10">
            <h1 className="text-4xl font-extrabold text-blue-900 tracking-tight">Patient Dashboard</h1>
            <button className="text-sm font-medium text-red-600 hover:text-red-800" onClick={() => { localStorage.clear(); window.location.href='/auth/login'; }}>Logout</button>
          </header>
          
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
            <DashboardCard title="Find a Doctor" desc="Browse specialists and book slots" link="/patient/doctor_list" icon="👨‍⚕️" />
            <DashboardCard title="My Appointments" desc="View upcoming and past appointments" link="/patient/appointments" icon="📅" />
            <DashboardCard title="Medical Records" desc="Upload and view your test reports" link="/patient/records" icon="📂" />
            <DashboardCard title="AI Chatbot" desc="Check your symptoms instantly" link="/patient/chatbot" icon="🤖" />
          </div>
        </div>
      </div>
    </ProtectedRoute>
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
