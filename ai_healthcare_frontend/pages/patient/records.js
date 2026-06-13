import { useEffect, useState } from 'react';
import ProtectedRoute from '../../components/ProtectedRoute';
import api from '../../utils/api';
import Link from 'next/link';

export default function MedicalRecords() {
  const [records, setRecords] = useState([]);
  const [loading, setLoading] = useState(true);
  const [uploading, setUploading] = useState(false);
  const [formData, setFormData] = useState({ doctor: '', notes: '', folderName: 'General', isPrivate: true });
  const [folderMode, setFolderMode] = useState('preset');
  const [customFolderName, setCustomFolderName] = useState('');
  const [file, setFile] = useState(null);
  const [doctors, setDoctors] = useState([]);
  const [doctorsError, setDoctorsError] = useState(null);
  const [filters, setFilters] = useState({ doctor: '', dateFrom: '', dateTo: '' });
  const [selectedFolder, setSelectedFolder] = useState('All Records');
  const reportFolders = ['General', 'Blood Report', 'Kidney Report', 'Lab Report', 'Imaging Report'];

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    setLoading(true);
    setDoctorsError(null);
    try {
      const recordsRes = await api.get('/records/');
      setRecords(recordsRes.data);
      try {
        const docsRes = await api.get('/doctors/');
        setDoctors(docsRes.data || []);
        if (!docsRes.data || docsRes.data.length === 0) {
          setDoctorsError('No doctors available. Please contact an administrator.');
        }
      } catch (docErr) {
        console.error('Error fetching doctors:', docErr);
        setDoctorsError('Unable to load doctors. Please try again.');
      }
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleUpload = async (e) => {
    e.preventDefault();
    const resolvedFolderName = folderMode === 'custom' ? customFolderName.trim() : formData.folderName;
    if (!file || !formData.notes) return alert('Please fill in required fields');
    if (folderMode === 'custom' && !resolvedFolderName) return alert('Please provide a folder name');

    setUploading(true);
    const data = new FormData();
    if (formData.doctor) {
      data.append('doctor', formData.doctor);
    }
    data.append('notes', formData.notes);
    data.append('folder_name', resolvedFolderName);
    data.append('is_private', formData.isPrivate ? 'true' : 'false');
    data.append('report_file', file);

    try {
      await api.post('/records/', data, { headers: { 'Content-Type': 'multipart/form-data' } });
      alert('Record uploaded successfully!');
      fetchData();
      setFormData({ doctor: '', notes: '', folderName: 'General', isPrivate: true });
      setFolderMode('preset');
      setCustomFolderName('');
      setFile(null);
    } catch (err) {
      console.error(err);
      alert('Upload failed: ' + (err.response?.data?.detail || 'Verify your inputs.'));
    } finally {
      setUploading(false);
    }
  };

  const doctorLabel = (doctorId) => {
    if (!doctorId) {
      return 'Private record';
    }
    const doctor = doctors.find((d) => d.id === doctorId);
    return doctor ? `Dr. ${doctor.user_username || 'Unknown Doctor'}` : 'Unknown Doctor';
  };

  const folderList = ['All Records', ...Array.from(new Set(records.map((rec) => rec.folder_name || 'General'))).sort()];

  const filteredRecords = records.filter((rec) => {
    if (selectedFolder !== 'All Records' && (rec.folder_name || 'General') !== selectedFolder) {
      return false;
    }

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
                {doctorsError && (
                  <div className="p-3 rounded-lg bg-yellow-50 text-yellow-700 text-sm">
                    {doctorsError}
                  </div>
                )}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Select Doctor</label>
                  <select value={formData.doctor} onChange={e => setFormData({ ...formData, doctor: e.target.value })} className="w-full border px-3 py-2 rounded-lg text-gray-900 bg-white">
                    <option value="">{doctors.length === 0 ? 'No doctors available' : 'Choose Doctor...'}</option>
                    {doctors.map(d => <option key={d.id} value={d.id}>Dr. {d.user_username || 'Unknown Doctor'}</option>)}
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Report Folder</label>
                  <select
                    value={folderMode}
                    onChange={(e) => setFolderMode(e.target.value)}
                    className="w-full border px-3 py-2 rounded-lg text-gray-900 bg-white"
                  >
                    <option value="preset">Choose Existing Folder</option>
                    <option value="custom">Create New Folder</option>
                  </select>
                  {folderMode === 'preset' ? (
                    <select
                      value={formData.folderName}
                      onChange={(e) => setFormData({ ...formData, folderName: e.target.value })}
                      className="w-full border px-3 py-2 rounded-lg text-gray-900 bg-white mt-2"
                    >
                      {reportFolders.map((folder) => (
                        <option key={folder} value={folder}>{folder}</option>
                      ))}
                    </select>
                  ) : (
                    <input
                      type="text"
                      value={customFolderName}
                      onChange={(e) => setCustomFolderName(e.target.value)}
                      className="w-full border px-3 py-2 rounded-lg text-gray-900 bg-white mt-2"
                      placeholder="e.g. Blood Report"
                    />
                  )}
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Notes</label>
                  <textarea
                    rows="3"
                    required
                    value={formData.notes}
                    onChange={e => setFormData({ ...formData, notes: e.target.value })}
                    className="w-full border px-3 py-2 rounded-lg text-gray-900 bg-white placeholder:text-gray-400"
                    placeholder="Add your report notes here"
                  ></textarea>
                </div>
                <div className="border-t pt-4">
                  <label className="flex items-center gap-2 cursor-pointer">
                    <input
                      type="checkbox"
                      checked={formData.isPrivate}
                      onChange={e => setFormData({ ...formData, isPrivate: e.target.checked })}
                      className="w-4 h-4 rounded border-gray-300"
                    />
                    <span className="text-sm font-medium text-gray-700">Keep reports private (only visible to me)</span>
                  </label>
                  <p className="text-xs text-gray-500 mt-2">📋 When checked, only you can see these reports. You can grant doctor access later.</p>
                </div>
                <p className="text-xs text-gray-500 -mt-2">Doctor selection is optional for private uploads.</p>
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
              <div className="mb-4">
                <h2 className="text-xl font-bold text-gray-800">My Records</h2>
                <p className="text-sm text-gray-500 mt-1">Browse everything you own with All Records, or focus on a single folder.</p>
              </div>
              <div className="bg-white p-4 rounded-xl border border-gray-100 mb-4">
                <div className="flex flex-wrap gap-2">
                  {folderList.map((folder) => (
                    <button
                      key={folder}
                      type="button"
                      onClick={() => setSelectedFolder(folder)}
                      className={`px-3 py-2 rounded-full text-sm font-semibold border transition ${selectedFolder === folder ? 'bg-blue-600 text-white border-blue-600' : 'bg-white text-gray-700 border-gray-200 hover:border-blue-300 hover:text-blue-700'}`}
                    >
                      {folder}
                    </button>
                  ))}
                </div>
              </div>
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
                        <div className="flex items-center gap-2 mb-2">
                          <h3 className="font-bold text-gray-900">{rec.folder_name || 'General'}</h3>
                          <span className="text-xs font-semibold text-blue-700 bg-blue-50 px-2 py-1 rounded-full">Folder</span>
                        </div>
                        <p className="text-sm text-gray-600 mb-2 whitespace-pre-wrap"><span className="font-medium">Notes:</span> {rec.notes || 'N/A'}</p>
                        <p className="text-sm text-gray-600 mb-1"><span className="font-medium">Doctor:</span> {doctorLabel(rec.doctor)}</p>
                        <p className="text-sm text-gray-600 mb-1"><span className="font-medium">Access:</span> {rec.is_private ? 'Private to you' : 'Shared'}</p>
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
