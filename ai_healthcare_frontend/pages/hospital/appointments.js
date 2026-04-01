import { useEffect, useState } from 'react';
import Link from 'next/link';
import ProtectedRoute from '../../components/ProtectedRoute';
import api from '../../utils/api';

export default function HospitalAppointmentsPage() {
    const [appointments, setAppointments] = useState([]);
    const [loading, setLoading] = useState(true);
    const [message, setMessage] = useState('');
    const [busyId, setBusyId] = useState('');

    const loadAppointments = async () => {
        setLoading(true);
        setMessage('');
        try {
            const res = await api.get('/appointments/');
            setAppointments(res.data || []);
        } catch (err) {
            const detail = err?.response?.data?.detail || 'Failed to load appointments.';
            setMessage(Array.isArray(detail) ? detail[0] : detail);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        loadAppointments();
    }, []);

    const confirmAppointment = async (id) => {
        setBusyId(id);
        setMessage('');
        try {
            await api.put(`/appointments/${id}/confirm/`, {});
            setMessage('Appointment confirmed.');
            await loadAppointments();
        } catch (err) {
            const detail = err?.response?.data?.detail || 'Failed to confirm appointment.';
            setMessage(Array.isArray(detail) ? detail[0] : detail);
        } finally {
            setBusyId('');
        }
    };

    const cancelAppointment = async (id) => {
        setBusyId(id);
        setMessage('');
        try {
            await api.put(`/appointments/${id}/cancel/`, {});
            setMessage('Appointment cancelled.');
            await loadAppointments();
        } catch (err) {
            const detail = err?.response?.data?.detail || 'Failed to cancel appointment.';
            setMessage(Array.isArray(detail) ? detail[0] : detail);
        } finally {
            setBusyId('');
        }
    };

    const rescheduleAppointment = async (id, currentDatetime) => {
        const nextDate = prompt(
            'Enter new appointment datetime (ISO, e.g. 2031-01-11T11:00:00Z):',
            currentDatetime || ''
        );
        if (!nextDate) return;

        setBusyId(id);
        setMessage('');
        try {
            await api.put(`/appointments/${id}/reschedule/`, { appointment_datetime: nextDate });
            setMessage('Appointment rescheduled.');
            await loadAppointments();
        } catch (err) {
            const detail = err?.response?.data?.detail || 'Failed to reschedule appointment.';
            setMessage(Array.isArray(detail) ? detail[0] : detail);
        } finally {
            setBusyId('');
        }
    };

    return (
        <ProtectedRoute allowedRoles={['admin']} forbidSuperAdmin={true}>
            <div className="min-h-screen bg-gray-50 p-8">
                <div className="max-w-6xl mx-auto">
                    <div className="flex items-center space-x-4 mb-8">
                        <Link href="/hospital/dashboard" className="text-blue-600 hover:underline">Back to Dashboard</Link>
                        <h1 className="text-3xl font-bold text-gray-800">Hospital Appointments</h1>
                    </div>

                    {message && (
                        <div className={`mb-6 p-4 rounded-lg text-sm ${message.toLowerCase().includes('failed') ? 'bg-red-50 text-red-700' : 'bg-green-50 text-green-700'}`}>
                            {message}
                        </div>
                    )}

                    {loading ? (
                        <div className="text-center py-10 text-gray-500">Loading appointments...</div>
                    ) : appointments.length === 0 ? (
                        <div className="bg-white p-6 rounded-xl border border-gray-100 text-gray-500">No appointments found for your hospital.</div>
                    ) : (
                        <div className="bg-white rounded-xl border border-gray-100 overflow-hidden">
                            <div className="overflow-x-auto">
                                <table className="w-full text-left">
                                    <thead className="bg-gray-50 border-b border-gray-100">
                                        <tr>
                                            <th className="px-4 py-3 text-sm font-semibold text-gray-700">Patient</th>
                                            <th className="px-4 py-3 text-sm font-semibold text-gray-700">Doctor</th>
                                            <th className="px-4 py-3 text-sm font-semibold text-gray-700">Datetime</th>
                                            <th className="px-4 py-3 text-sm font-semibold text-gray-700">Status</th>
                                            <th className="px-4 py-3 text-sm font-semibold text-gray-700">Actions</th>
                                        </tr>
                                    </thead>
                                    <tbody>
                                        {appointments.map((appt) => (
                                            <tr key={appt.id} className="border-b border-gray-100">
                                                <td className="px-4 py-3 text-sm text-gray-900">{appt.patient_name || 'N/A'}</td>
                                                <td className="px-4 py-3 text-sm text-gray-900">{appt.doctor_name || 'N/A'}</td>
                                                <td className="px-4 py-3 text-sm text-gray-700">{appt.appointment_datetime || `${appt.date || ''} ${appt.time || ''}`}</td>
                                                <td className="px-4 py-3 text-sm font-medium text-gray-800">{appt.status}</td>
                                                <td className="px-4 py-3 text-sm space-x-2">
                                                    <button
                                                        disabled={busyId === appt.id || appt.status !== 'PENDING'}
                                                        onClick={() => confirmAppointment(appt.id)}
                                                        className="px-2 py-1 rounded bg-green-600 text-white disabled:bg-gray-300"
                                                    >
                                                        Confirm
                                                    </button>
                                                    <button
                                                        disabled={busyId === appt.id || appt.status === 'CANCELLED' || appt.status === 'COMPLETED'}
                                                        onClick={() => rescheduleAppointment(appt.id, appt.appointment_datetime)}
                                                        className="px-2 py-1 rounded bg-indigo-600 text-white disabled:bg-gray-300"
                                                    >
                                                        Reschedule
                                                    </button>
                                                    <button
                                                        disabled={busyId === appt.id || appt.status === 'CANCELLED' || appt.status === 'COMPLETED'}
                                                        onClick={() => cancelAppointment(appt.id)}
                                                        className="px-2 py-1 rounded bg-red-600 text-white disabled:bg-gray-300"
                                                    >
                                                        Cancel
                                                    </button>
                                                </td>
                                            </tr>
                                        ))}
                                    </tbody>
                                </table>
                            </div>
                        </div>
                    )}
                </div>
            </div>
        </ProtectedRoute>
    );
}
