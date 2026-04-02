import { useCallback, useEffect, useMemo, useState } from 'react';
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
    const [showCreateForm, setShowCreateForm] = useState(false);
    const [createForm, setCreateForm] = useState({
        email: '',
        username: '',
        password: '',
        specialization: '',
        licence_number: '',
        qualifications: '',
        experience_years: '',
        consultation_fee: '',
    });

    const hospitalId = useMemo(() => hospital?.id, [hospital]);

    const formatApiError = (error, fallback) => {
        const data = error?.response?.data;
        if (!data) return fallback;

        if (typeof data === 'string') return data;
        if (data.detail) return Array.isArray(data.detail) ? data.detail[0] : data.detail;

        const firstField = Object.values(data).find(Boolean);
        if (Array.isArray(firstField)) return firstField[0];
        if (typeof firstField === 'string') return firstField;
        return fallback;
    };

    const loadDoctorData = useCallback(async () => {
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
            setMessage(formatApiError(err, 'Failed to load doctors.'));
        } finally {
            setLoading(false);
        }
    }, []);

    const handleCreateChange = (e) => {
        const { name, value } = e.target;
        setCreateForm((prev) => ({ ...prev, [name]: value }));
    };

    const createDoctor = async (e) => {
        e.preventDefault();
        if (!hospitalId) return;

        setBusyDoctorId('create');
        setMessage('');
        try {
            await api.post('/admin/users/', {
                email: createForm.email,
                username: createForm.username,
                password: createForm.password,
                role: 'DOCTOR',
                hospital_id: hospitalId,
                specialization: createForm.specialization,
                licence_number: createForm.licence_number,
                qualifications: createForm.qualifications,
                experience_years: Number(createForm.experience_years),
                consultation_fee: createForm.consultation_fee,
            });

            setMessage('Doctor account created and linked successfully.');
            setCreateForm({
                email: '',
                username: '',
                password: '',
                specialization: '',
                licence_number: '',
                qualifications: '',
                experience_years: '',
                consultation_fee: '',
            });
            setShowCreateForm(false);
            await loadDoctorData();
        } catch (err) {
            setMessage(`Failed to create doctor: ${formatApiError(err, err.message)}`);
        } finally {
            setBusyDoctorId('');
        }
    };

    useEffect(() => {
        loadDoctorData();
    }, [loadDoctorData]);

    const linkDoctor = async (doctorId) => {
        if (!hospitalId) return;
        setBusyDoctorId(doctorId);
        setMessage('');
        try {
            await api.post(`/hospitals/${hospitalId}/link-doctor/`, { doctor_id: doctorId });
            setMessage('Doctor linked successfully.');
            await loadDoctorData();
        } catch (err) {
            setMessage(formatApiError(err, 'Failed to link doctor.'));
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
            setMessage(formatApiError(err, 'Failed to unlink doctor.'));
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
                        <div className={`mb-6 p-4 rounded-lg text-sm ${message.toLowerCase().includes('success') || message.toLowerCase().includes('linked') || message.toLowerCase().includes('created') ? 'bg-green-50 text-green-700' : 'bg-red-50 text-red-700'}`}>
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
                        <>
                            <div className="mb-6 bg-white rounded-xl border border-gray-100 p-5 shadow-sm">
                                <div className="flex items-center justify-between gap-4 flex-wrap">
                                    <div>
                                        <h2 className="text-lg font-semibold text-gray-800">Add Doctor Account</h2>
                                        <p className="text-sm text-gray-600 mt-1">Create a doctor for this hospital and link them automatically.</p>
                                        <p className="text-xs text-gray-500 mt-1">Use this for a brand-new doctor account. If the doctor already exists, use the Link Doctor list on the right.</p>
                                    </div>
                                    <button
                                        onClick={() => setShowCreateForm(!showCreateForm)}
                                        className="px-4 py-2 rounded bg-blue-600 text-white hover:bg-blue-700"
                                    >
                                        {showCreateForm ? 'Cancel' : 'Add Doctor'}
                                    </button>
                                </div>

                                {showCreateForm && (
                                    <form onSubmit={createDoctor} className="mt-5 grid grid-cols-1 md:grid-cols-2 gap-4">
                                        <input name="email" value={createForm.email} onChange={handleCreateChange} type="email" placeholder="Doctor email" className="px-3 py-2 border rounded bg-white text-gray-900" required />
                                        <input name="username" value={createForm.username} onChange={handleCreateChange} type="text" placeholder="Doctor username" className="px-3 py-2 border rounded bg-white text-gray-900" required />
                                        <input name="password" value={createForm.password} onChange={handleCreateChange} type="password" placeholder="Password" className="px-3 py-2 border rounded bg-white text-gray-900" required />
                                        <input name="specialization" value={createForm.specialization} onChange={handleCreateChange} type="text" placeholder="Specialization" className="px-3 py-2 border rounded bg-white text-gray-900" required />
                                        <input name="licence_number" value={createForm.licence_number} onChange={handleCreateChange} type="text" placeholder="Licence number" className="px-3 py-2 border rounded bg-white text-gray-900" required />
                                        <input name="qualifications" value={createForm.qualifications} onChange={handleCreateChange} type="text" placeholder="Qualifications" className="px-3 py-2 border rounded bg-white text-gray-900" required />
                                        <input name="experience_years" value={createForm.experience_years} onChange={handleCreateChange} type="number" min="0" placeholder="Experience years" className="px-3 py-2 border rounded bg-white text-gray-900" required />
                                        <input name="consultation_fee" value={createForm.consultation_fee} onChange={handleCreateChange} type="number" step="0.01" min="0" placeholder="Consultation fee" className="px-3 py-2 border rounded bg-white text-gray-900" required />
                                        <div className="md:col-span-2 flex justify-end">
                                            <button
                                                type="submit"
                                                disabled={busyDoctorId === 'create'}
                                                className="px-4 py-2 rounded bg-green-600 text-white hover:bg-green-700 disabled:bg-green-300"
                                            >
                                                {busyDoctorId === 'create' ? 'Creating...' : 'Create Doctor'}
                                            </button>
                                        </div>
                                    </form>
                                )}
                            </div>

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
                        </>
                    )}
                </div>
            </div>
        </ProtectedRoute>
    );
}
