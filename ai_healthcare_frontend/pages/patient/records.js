import { useEffect, useState } from 'react';
import ProtectedRoute from '../../components/ProtectedRoute';
import api from '../../utils/api';
import Link from 'next/link';

export default function MedicalRecords() {
  const [records, setRecords] = useState([]);
  const [loading, setLoading] = useState(true);
  const [uploading, setUploading] = useState(false);
  const [formData, setFormData] = useState({ doctor: '', diagnosis: '', prescription: '' });
  const [file, setFile] = useState(null);
  const [doctors, setDoctors] = useState([]);
  const [filters, setFilters] = useState({ doctor: '', dateFrom: '', dateTo: '' });

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    setLoading(true);
    try {
      const recordsRes = await api.get('/records/');
      setRecords(recordsRes.data);
      const docsRes = await api.get('/doctors/');
      setDoctors(docsRes.data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleUpload = async (e) => {
    e.preventDefault();
    if (!file || !formData.doctor || !formData.diagnosis) return alert('Please fill in required fields');

    setUploading(true);
    const data = new FormData();
    data.append('doctor', formData.doctor);
    data.append('diagnosis', formData.diagnosis);
    data.append('prescription', formData.prescription);
    data.append('report_file', file);

    try {
      await api.post('/records/', data, { headers: { 'Content-Type': 'multipart/form-data' } });
      alert('Record uploaded successfully!');
      fetchData();
      setFormData({ doctor: '', diagnosis: '', prescription: '' });
      setFile(null);
    } catch (err) {
      console.error(err);
      alert('Upload failed: ' + (err.response?.data?.detail || 'Verify your inputs.'));
    } finally {
      setUploading(false);
    }
  };

  const doctorLabel = (doctorId) => {
    const doctor = doctors.find((d) => d.id === doctorId);
    return doctor ? `Dr. ${doctor.user_username || 'Unknown Doctor'}` : 'Unknown Doctor';
  };

  const filteredRecords = records.filter((rec) => {
    if (filters.doctor && rec.doctor !== filters.doctor) {
      return false;
    }

    if (filters.dateFrom) {
      const from = new Date(filters.dateFrom);
      const created = new Date(rec.created_at);
      if (created < from) {
        return false;
      }
    }

    if (filters.dateTo) {
      const to = new Date(filters.dateTo);
      to.setHours(23, 59, 59, 999);
      const created = new Date(rec.created_at);
      if (created > to) {
        return false;
      }
    }

    return true;
  });

  return (
    <ProtectedRoute allowedRoles={['patient']}>
      <div className="min-h-screen bg-gray-50 p-8">
        <div className="max-w-6xl mx-auto">
          <div className="flex items-center space-x-4 mb-8">
            <Link href="/patient/dashboard" className="text-blue-600 hover:underline">← Back to Dashboard</Link>
            <h1 className="text-3xl font-bold text-gray-800">Medical Records</h1>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
            {/* Upload Section */}
            <div className="lg:col-span-1 bg-white p-6 rounded-xl shadow-sm border border-gray-100 h-fit">
              <h2 className="text-xl font-bold text-gray-800 mb-4">Upload New Record</h2>
              <form onSubmit={handleUpload} className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Select Doctor</label>
                  <select required value={formData.doctor} onChange={e => setFormData({ ...formData, doctor: e.target.value })} className="w-full border px-3 py-2 rounded-lg text-gray-900 bg-white">
                    <option value="">Choose Doctor...</option>
                    {doctors.map(d => <option key={d.id} value={d.id}>Dr. {d.user_username || 'Unknown Doctor'}</option>)}
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Diagnosis</label>
                  <input type="text" required value={formData.diagnosis} onChange={e => setFormData({ ...formData, diagnosis: e.target.value })} className="w-full border px-3 py-2 rounded-lg" />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Prescription Notes</label>
                  <textarea rows="2" value={formData.prescription} onChange={e => setFormData({ ...formData, prescription: e.target.value })} className="w-full border px-3 py-2 rounded-lg"></textarea>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Report File (PDF/Image)</label>
                  <input type="file" required onChange={e => setFile(e.target.files[0])} className="w-full text-sm" />
                </div>
                <button type="submit" disabled={uploading} className="w-full bg-blue-600 text-white py-2 rounded-lg font-bold hover:bg-blue-700 disabled:bg-blue-300">
                  {uploading ? 'Uploading...' : 'Upload Record'}
                </button>
              </form>
            </div>

            {/* List Section */}
            <div className="lg:col-span-2">
              <h2 className="text-xl font-bold text-gray-800 mb-4">My Records</h2>
              <div className="bg-white p-4 rounded-xl border border-gray-100 mb-4 grid grid-cols-1 md:grid-cols-3 gap-3">
                <select
                  value={filters.doctor}
                  onChange={(e) => setFilters({ ...filters, doctor: e.target.value })}
                  className="w-full border px-3 py-2 rounded-lg text-gray-900 bg-white"
                >
                  <option value="">All Doctors</option>
                  {doctors.map((d) => (
                    <option key={d.id} value={d.id}>Dr. {d.user_username || 'Unknown Doctor'}</option>
                  ))}
                </select>
                <input
                  type="date"
                  value={filters.dateFrom}
                  onChange={(e) => setFilters({ ...filters, dateFrom: e.target.value })}
                  className="w-full border px-3 py-2 rounded-lg"
                />
                <input
                  type="date"
                  value={filters.dateTo}
                  onChange={(e) => setFilters({ ...filters, dateTo: e.target.value })}
                  className="w-full border px-3 py-2 rounded-lg"
                />
              </div>
              {loading ? (
                <div className="text-center py-10 text-gray-500">Loading Records...</div>
              ) : filteredRecords.length === 0 ? (
                <div className="bg-white p-10 text-center rounded-xl border border-dashed border-gray-300">
                  <p className="text-gray-500">No medical records found for the selected filters.</p>
                </div>
              ) : (
                <div className="space-y-4">
                  {filteredRecords.map(rec => (
                    <div key={rec.id} className="bg-white p-5 rounded-xl shadow-sm border border-gray-100 flex justify-between items-center group hover:shadow-md transition">
                      <div>
                        <h3 className="font-bold text-gray-900 mb-1">{rec.diagnosis}</h3>
                        <p className="text-sm text-gray-600 mb-1"><span className="font-medium">Prescription:</span> {rec.prescription || 'N/A'}</p>
                        <p className="text-sm text-gray-600 mb-1"><span className="font-medium">Doctor:</span> {doctorLabel(rec.doctor)}</p>
                        <p className="text-xs text-gray-400">Date: {new Date(rec.created_at).toLocaleDateString()}</p>
                      </div>
                      {rec.report_file && (
                        <a href={rec.report_file} target="_blank" rel="noopener noreferrer" className="bg-gray-100 text-blue-600 px-4 py-2 rounded-lg text-sm font-semibold hover:bg-blue-50 transition">
                          View File
                        </a>
                      )}
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </ProtectedRoute>
  );
}
