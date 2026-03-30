import { useEffect, useState } from 'react';
import ProtectedRoute from '../../components/ProtectedRoute';
import api from '../../utils/api';
import Link from 'next/link';
import { useRouter } from 'next/router';

export default function PatientHistory() {
  const router = useRouter();
  const { patientId: patientIdFromQuery } = router.query;

  const [patients, setPatients] = useState([]);
  const [selectedPatient, setSelectedPatient] = useState('');
  const [records, setRecords] = useState([]);
  const [appointments, setAppointments] = useState([]);
  const [loading, setLoading] = useState(false);
  const [bootLoading, setBootLoading] = useState(true);

  const activeSelectedPatient = selectedPatient || patientIdFromQuery || '';

  useEffect(() => {
    let mounted = true;
    Promise.all([api.get('/patients/'), api.get('/records/'), api.get('/appointments/')])
      .then(([patientsRes, recordsRes, appointmentsRes]) => {
        if (!mounted) return;
        setPatients(patientsRes.data || []);
        setRecords(recordsRes.data || []);
        setAppointments(appointmentsRes.data || []);
      })
      .catch(console.error)
      .finally(() => {
        if (mounted) setBootLoading(false);
      });

    return () => {
      mounted = false;
    };
  }, []);

  const selectedPatientProfile = patients.find(
    (p) => p.id === activeSelectedPatient || p.user?.id === activeSelectedPatient
  );

  const filteredRecords = records.filter(
    (r) => r.patient === activeSelectedPatient || r.patient?.id === activeSelectedPatient
  );

  const filteredAppointments = appointments.filter(
    (a) => a.patient === activeSelectedPatient || a.patient?.id === activeSelectedPatient
  );

  const handleSelectPatient = (patientId) => {
    setLoading(true);
    setSelectedPatient(patientId);
    setTimeout(() => setLoading(false), 100);
  };

  return (
    <ProtectedRoute allowedRoles={['doctor']}>
      <div className="min-h-screen bg-gray-50 p-8">
        <div className="max-w-4xl mx-auto">
          <div className="flex items-center space-x-4 mb-8">
            <Link href="/doctor/dashboard" className="text-blue-600 hover:underline">← Back to Dashboard</Link>
            <h1 className="text-3xl font-bold text-gray-800">Patient History</h1>
          </div>

          <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-100 mb-8">
            <label className="block text-gray-700 font-medium mb-2">Select Patient to View History</label>
            <select
              value={activeSelectedPatient}
              onChange={e => handleSelectPatient(e.target.value)}
              className="w-full max-w-md border px-4 py-2 rounded-lg focus:ring-2 focus:ring-blue-200"
            >
              <option value="">Choose Patient...</option>
              {patients.map(p => <option key={p.id} value={p.id}>{p.user?.username || `Patient ${p.id.substring(0, 4)}`}</option>)}
            </select>
          </div>

          {bootLoading || loading ? (
            <div className="text-center py-10 text-gray-500">Loading History...</div>
          ) : activeSelectedPatient && filteredRecords.length === 0 && filteredAppointments.length === 0 ? (
            <div className="bg-white p-10 text-center rounded-xl border border-dashed border-gray-300">
              <p className="text-gray-500">No previous records or appointments found for this patient.</p>
            </div>
          ) : activeSelectedPatient ? (
            <div className="space-y-4">
              {selectedPatientProfile && (
                <div className="bg-white p-5 rounded-xl shadow-sm border border-gray-100">
                  <h2 className="text-xl font-bold text-gray-900">Patient Details</h2>
                  <p className="text-sm text-gray-600 mt-2"><span className="font-semibold">Name:</span> {selectedPatientProfile.user?.username || 'N/A'}</p>
                  <p className="text-sm text-gray-600"><span className="font-semibold">Email:</span> {selectedPatientProfile.user?.email || 'N/A'}</p>
                  <p className="text-sm text-gray-600"><span className="font-semibold">Patient ID:</span> {selectedPatientProfile.id}</p>
                </div>
              )}

              <div className="bg-white p-5 rounded-xl shadow-sm border border-gray-100">
                <h3 className="text-lg font-bold text-gray-900 mb-3">Past Appointments</h3>
                {filteredAppointments.length === 0 ? (
                  <p className="text-sm text-gray-500">No appointments found.</p>
                ) : (
                  <div className="space-y-3">
                    {filteredAppointments.map((appt) => (
                      <div key={appt.id} className="border border-gray-100 rounded-lg p-3">
                        <p className="text-sm text-gray-700"><span className="font-semibold">Date:</span> {appt.date}</p>
                        <p className="text-sm text-gray-700"><span className="font-semibold">Time:</span> {appt.time}</p>
                        <p className="text-sm text-gray-700"><span className="font-semibold">Reason:</span> {appt.reason}</p>
                        <p className="text-sm text-gray-700"><span className="font-semibold">Status:</span> {appt.status}</p>
                      </div>
                    ))}
                  </div>
                )}
              </div>

              <div className="bg-white p-5 rounded-xl shadow-sm border border-gray-100">
                <h3 className="text-lg font-bold text-gray-900 mb-3">Medical Records</h3>
                {filteredRecords.length === 0 ? (
                  <p className="text-sm text-gray-500">No medical records found.</p>
                ) : (
                  <div className="space-y-3">
                    {filteredRecords.map(rec => (
                      <div key={rec.id} className="border border-gray-100 rounded-lg p-3">
                        <div className="flex justify-between items-start mb-2">
                          <h4 className="font-bold text-gray-900">{rec.diagnosis}</h4>
                          <span className="text-xs font-semibold text-gray-500 bg-gray-100 px-2 py-1 rounded-full">
                            {new Date(rec.created_at).toLocaleDateString()}
                          </span>
                        </div>
                        <p className="text-sm text-gray-700"><span className="font-semibold">Prescription:</span> {rec.prescription || 'N/A'}</p>
                        {rec.report_file && (
                          <a href={rec.report_file} target="_blank" rel="noopener noreferrer" className="text-sm font-semibold text-blue-600 hover:underline inline-flex mt-2">
                            View Attached Report
                          </a>
                        )}
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </div>
          ) : null}
        </div>
      </div>
    </ProtectedRoute>
  );
}
