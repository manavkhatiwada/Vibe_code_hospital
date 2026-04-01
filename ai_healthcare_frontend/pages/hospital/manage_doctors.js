import { useEffect, useMemo, useState } from 'react';
import Link from 'next/link';
import ProtectedRoute from '../../components/ProtectedRoute';
import api from '../../utils/api';

export default function ManageDoctorsPage() {
    const [hospital, setHospital] = useState(null);
    const [linkedDoctors, setLinkedDoctors] = useState([]);
    const [availableDoctors, setAvailableDoctors] = useState([]);
    const [loading, setLoading] = useState(true);
    const [message, setMessage] = useState('');
    const [busyDoctorId, setBusyDoctorId] = useState('');

    const hospitalId = useMemo(() => hospital?.id, [hospital]);

    const loadDoctorData = async () => {
        setLoading(true);
        setMessage('');
        try {
            const hospitalsRes = await api.get('/hospitals/');
            const hospitals = hospitalsRes.data || [];
            const currentHospital = hospitals[0] || null;
            setHospital(currentHospital);

            if (!currentHospital) {
                setLinkedDoctors([]);
                setAvailableDoctors([]);
                return;
            }

            const [linkedRes, availableRes] = await Promise.all([
                api.get(`/hospitals/${currentHospital.id}/linked-doctors/`),
                api.get(`/hospitals/${currentHospital.id}/available-doctors/`),
            ]);

            setLinkedDoctors(linkedRes.data || []);
            setAvailableDoctors(availableRes.data || []);
        } catch (err) {
            const detail = err?.response?.data?.detail || 'Failed to load doctors.';
            setMessage(Array.isArray(detail) ? detail[0] : detail);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        loadDoctorData();
    }, []);

    const linkDoctor = async (doctorId) => {
        if (!hospitalId) return;
        setBusyDoctorId(doctorId);
        setMessage('');
        try {
            await api.post(`/hospitals/${hospitalId}/link-doctor/`, { doctor_id: doctorId });
            setMessage('Doctor linked successfully.');
            await loadDoctorData();
        } catch (err) {
            const detail = err?.response?.data?.detail || 'Failed to link doctor.';
            setMessage(Array.isArray(detail) ? detail[0] : detail);
        } finally {
            setBusyDoctorId('');
        }
    };

    const unlinkDoctor = async (doctorId) => {
        if (!hospitalId) return;
        setBusyDoctorId(doctorId);
        setMessage('');
        try {
            await api.delete(`/hospitals/${hospitalId}/unlink-doctor/`, { data: { doctor_id: doctorId } });
            setMessage('Doctor unlinked successfully.');
            await loadDoctorData();
        } catch (err) {
            const detail = err?.response?.data?.detail || 'Failed to unlink doctor.';
            setMessage(Array.isArray(detail) ? detail[0] : detail);
        } finally {
            setBusyDoctorId('');
        }
    };

    return (
        <ProtectedRoute allowedRoles={['admin']} forbidSuperAdmin={true}>
            <div className="min-h-screen bg-gray-50 p-8">
                <div className="max-w-6xl mx-auto">
                    <div className="flex items-center space-x-4 mb-8">
                        <Link href="/hospital/dashboard" className="text-blue-600 hover:underline">Back to Dashboard</Link>
                        <h1 className="text-3xl font-bold text-gray-800">Doctor Membership Management</h1>
                    </div>

                    {hospital && (
                        <p className="mb-6 text-sm text-gray-600">
                            Hospital: <span className="font-semibold text-gray-800">{hospital.name}</span>
                        </p>
                    )}

                    {message && (
                        <div className={`mb-6 p-4 rounded-lg text-sm ${message.toLowerCase().includes('success') || message.toLowerCase().includes('linked') ? 'bg-green-50 text-green-700' : 'bg-red-50 text-red-700'}`}>
                            {message}
                        </div>
                    )}

                    {!hospital && !loading && (
                        <div className="bg-white rounded-xl border border-gray-100 p-6 text-gray-600">
                            No hospital is assigned to your admin account.
                        </div>
                    )}

                    {loading ? (
                        <div className="text-center py-10 text-gray-500">Loading doctors...</div>
                    ) : (
                        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                            <section className="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
                                <div className="p-4 border-b border-gray-100">
                                    <h2 className="text-lg font-semibold text-gray-800">Linked Doctors</h2>
                                </div>
                                {linkedDoctors.length === 0 ? (
                                    <div className="p-6 text-sm text-gray-500">No doctors are currently linked.</div>
                                ) : (
                                    <div className="divide-y divide-gray-100">
                                        {linkedDoctors.map((doctor) => (
                                            <div key={doctor.id} className="p-4 flex justify-between items-center gap-3">
                                                <div>
                                                    <p className="font-semibold text-gray-900">{doctor.user_username || 'Unknown Doctor'}</p>
                                                    <p className="text-sm text-gray-600">{doctor.specialization || 'General'}</p>
                                                </div>
                                                <button
                                                    onClick={() => unlinkDoctor(doctor.id)}
                                                    disabled={busyDoctorId === doctor.id}
                                                    className="px-3 py-2 text-sm rounded bg-red-600 text-white hover:bg-red-700 disabled:bg-red-300"
                                                >
                                                    {busyDoctorId === doctor.id ? 'Working...' : 'Unlink'}
                                                </button>
                                            </div>
                                        ))}
                                    </div>
                                )}
                            </section>

                            <section className="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
                                <div className="p-4 border-b border-gray-100">
                                    <h2 className="text-lg font-semibold text-gray-800">Available Doctors</h2>
                                </div>
                                {availableDoctors.length === 0 ? (
                                    <div className="p-6 text-sm text-gray-500">No available doctors to link right now.</div>
                                ) : (
                                    <div className="divide-y divide-gray-100">
                                        {availableDoctors.map((doctor) => (
                                            <div key={doctor.id} className="p-4 flex justify-between items-center gap-3">
                                                <div>
                                                    <p className="font-semibold text-gray-900">{doctor.user_username || 'Unknown Doctor'}</p>
                                                    <p className="text-sm text-gray-600">{doctor.specialization || 'General'}</p>
                                                </div>
                                                <button
                                                    onClick={() => linkDoctor(doctor.id)}
                                                    disabled={busyDoctorId === doctor.id}
                                                    className="px-3 py-2 text-sm rounded bg-blue-600 text-white hover:bg-blue-700 disabled:bg-blue-300"
                                                >
                                                    {busyDoctorId === doctor.id ? 'Working...' : 'Link'}
                                                </button>
                                            </div>
                                        ))}
                                    </div>
                                )}
                            </section>
                        </div>
                    )}
                </div>
            </div>
        </ProtectedRoute>
    );
}
