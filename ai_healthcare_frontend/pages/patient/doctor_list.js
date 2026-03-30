import { useEffect, useState } from 'react';
import ProtectedRoute from '../../components/ProtectedRoute';
import api from '../../utils/api';
import Link from 'next/link';

export default function DoctorList() {
  const [doctors, setDoctors] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.get('/doctors/')
      .then(res => {
        setDoctors(res.data);
        setLoading(false);
      })
      .catch(err => {
        console.error("Failed to load doctors", err);
        setLoading(false);
      });
  }, []);

  return (
    <ProtectedRoute allowedRoles={['patient']}>
      <div className="min-h-screen bg-gray-50 p-8">
        <div className="max-w-5xl mx-auto">
          <div className="flex items-center space-x-4 mb-8">
            <Link href="/patient/dashboard" className="text-blue-600 hover:underline">← Back</Link>
            <h1 className="text-3xl font-bold text-gray-800">Available Doctors</h1>
          </div>

          {loading ? (
            <div className="text-center py-20 text-gray-500">Loading Doctors...</div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {doctors.length === 0 ? (
                <p className="text-gray-500">No doctors currently available.</p>
              ) : (
                doctors.map(doc => (
                  <div key={doc.id} className="bg-white p-6 rounded-xl shadow-sm border border-gray-100 flex flex-col justify-between hover:shadow-lg transition">
                    <div>
                      <h3 className="text-xl font-semibold text-gray-900">{doc.user?.username || `Dr. ${doc.id.substring(0, 4)}`}</h3>
                      <p className="text-blue-600 text-sm font-medium mb-2">{doc.specialization}</p>
                      <p className="text-gray-500 text-sm mb-4">Experience: {doc.experience_years} years</p>
                      <p className="text-gray-700 font-bold mb-4">Fee: ${doc.consultation_fee}</p>
                    </div>
                    <Link href={`/patient/book_appointment?doctorId=${doc.id}`} className="block text-center bg-blue-600 text-white py-2 rounded-lg hover:bg-blue-700 transition">
                      Book Appointment
                    </Link>
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
