import { useEffect, useState } from 'react';
import ProtectedRoute from '../../components/ProtectedRoute';
import api from '../../utils/api';
import Link from 'next/link';

export default function ManageDoctors() {
  const [doctors, setDoctors] = useState([]);
  const [loading, setLoading] = useState(true);
  const [message, setMessage] = useState('');
  const [deletingDoctorId, setDeletingDoctorId] = useState('');

  useEffect(() => {
    fetchDoctors();
  }, []);

  const fetchDoctors = async () => {
    setLoading(true);
    try {
      const res = await api.get('/doctors/');
      setDoctors(res.data);
    } catch (err) {
      const detail = err?.response?.data?.detail || 'Failed to load doctors.';
      setMessage(Array.isArray(detail) ? detail[0] : detail);
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (id) => {
    if (!confirm('Are you sure you want to remove this doctor?')) return;
    setMessage('');
    setDeletingDoctorId(id);
    try {
      await api.delete(`/doctors/${id}/`);
      setMessage('Doctor removed successfully.');
      await fetchDoctors();
    } catch (err) {
      const detail = err?.response?.data?.detail || 'Error removing doctor.';
      setMessage(Array.isArray(detail) ? detail[0] : detail);
    } finally {
      setDeletingDoctorId('');
    }
  };

  return (
    <ProtectedRoute allowedRoles={['hospital']}>
      <div className="min-h-screen bg-gray-50 p-8">
        <div className="max-w-6xl mx-auto">
          <div className="flex items-center space-x-4 mb-8">
            <Link href="/hospital/dashboard" className="text-blue-600 hover:underline">← Back to Dashboard</Link>
            <h1 className="text-3xl font-bold text-gray-800">Manage Doctors</h1>
          </div>

          {message && (
            <div className={`mb-6 p-4 rounded-lg text-sm ${message.includes('successfully') ? 'bg-green-50 text-green-700' : 'bg-red-50 text-red-700'}`}>
              {message}
            </div>
          )}

          <div className="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
            <div className="p-6 border-b border-gray-100 flex justify-between items-center">
              <h2 className="text-xl font-semibold text-gray-800">Registered Doctors</h2>
              {/* Note: Registration logic usually happens on the Auth register page. 
                  Admin can create new users there, or we redirect them to a special admin creation page */}
            </div>

            {loading ? (
              <div className="text-center py-10 text-gray-500">Loading Staff...</div>
            ) : doctors.length === 0 ? (
              <div className="p-10 text-center text-gray-500">No doctors registered yet.</div>
            ) : (
              <div className="overflow-x-auto">
                <table className="w-full text-left border-collapse">
                  <thead>
                    <tr className="bg-gray-50 border-b border-gray-100">
                      <th className="py-3 px-6 font-semibold text-gray-600">ID</th>
                      <th className="py-3 px-6 font-semibold text-gray-600">Username/Name</th>
                      <th className="py-3 px-6 font-semibold text-gray-600">Email</th>
                      <th className="py-3 px-6 font-semibold text-gray-600">Specialization</th>
                      <th className="py-3 px-6 font-semibold text-gray-600">Experience</th>
                      <th className="py-3 px-6 font-semibold text-gray-600 text-right">Actions</th>
                    </tr>
                  </thead>
                  <tbody>
                    {doctors.map(doc => (
                      <tr key={doc.id} className="border-b border-gray-50 hover:bg-gray-50 transition">
                        <td className="py-3 px-6 text-sm text-gray-500">{doc.id.substring(0, 8)}...</td>
                        <td className="py-3 px-6 font-medium text-gray-900">{doc.user_username || 'N/A'}</td>
                        <td className="py-3 px-6 text-gray-600">{doc.user_email || 'N/A'}</td>
                        <td className="py-3 px-6 text-gray-600">{doc.specialization}</td>
                        <td className="py-3 px-6 text-gray-600">{doc.experience_years} Yrs</td>
                        <td className="py-3 px-6 text-right space-x-2">
                          <button
                            onClick={() => handleDelete(doc.id)}
                            disabled={deletingDoctorId === doc.id}
                            className="text-red-500 hover:text-red-700 font-medium text-sm transition disabled:text-red-300"
                          >
                            {deletingDoctorId === doc.id ? 'Deleting...' : 'Delete'}
                          </button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        </div>
      </div>
    </ProtectedRoute>
  );
}
