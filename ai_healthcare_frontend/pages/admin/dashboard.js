import { useState, useEffect } from 'react';
import { useRouter } from 'next/router';
import api from '../../utils/api';
import ProtectedRoute from '../../components/ProtectedRoute';

function AdminDashboardContent() {
    const router = useRouter();
    const [hospitals, setHospitals] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState('');
    const [activeTab, setActiveTab] = useState('hospitals');
    const [showCreateForm, setShowCreateForm] = useState(false);
    const [formData, setFormData] = useState({
        name: '',
        registration_number: '',
        address: '',
        city: '',
        state: '',
        country: '',
        contact_email: '',
        contact_phone: '',
        admin_id: '',
        admin_email: '',
        admin_username: '',
        admin_password: '',
    });

    useEffect(() => {
        fetchData();
    }, []);

    const fetchData = async () => {
        try {
            setLoading(true);
            const hospitalRes = await api.get('/hospitals/');
            setHospitals(hospitalRes.data || []);
        } catch (err) {
            setError('Failed to fetch data: ' + (err.response?.data?.detail || err.message));
        } finally {
            setLoading(false);
        }
    };

    const handleInputChange = (e) => {
        const { name, value } = e.target;
        setFormData(prev => ({ ...prev, [name]: value }));
    };

    const handleCreateHospital = async (e) => {
        e.preventDefault();
        try {
            let adminId = formData.admin_id;

            if (!adminId) {
                if (!formData.admin_email || !formData.admin_username || !formData.admin_password) {
                    throw new Error('Provide an existing admin ID or fill all hospital-admin creation fields.');
                }

                const adminResponse = await api.post('/admin/users/', {
                    email: formData.admin_email,
                    username: formData.admin_username,
                    password: formData.admin_password,
                    role: 'ADMIN',
                });
                adminId = adminResponse.data.id;
            }

            await api.post('/hospitals/', {
                name: formData.name,
                registration_number: formData.registration_number,
                address: formData.address,
                city: formData.city,
                state: formData.state,
                country: formData.country,
                contact_email: formData.contact_email,
                contact_phone: formData.contact_phone,
                admin_id: adminId,
            });
            setFormData({
                name: '',
                registration_number: '',
                address: '',
                city: '',
                state: '',
                country: '',
                contact_email: '',
                contact_phone: '',
                admin_id: '',
                admin_email: '',
                admin_username: '',
                admin_password: '',
            });
            setShowCreateForm(false);
            await fetchData();
            setError('');
        } catch (err) {
            const detail = err.response?.data?.detail || err.response?.data?.admin_id || err.message;
            setError('Failed to create hospital: ' + (Array.isArray(detail) ? detail[0] : detail));
        }
    };

    const handleDeleteHospital = async (hospitalId) => {
        if (!window.confirm('Are you sure you want to delete this hospital?')) return;
        try {
            await api.delete(`/hospitals/${hospitalId}/`);
            await fetchData();
        } catch (err) {
            setError('Failed to delete hospital: ' + (err.response?.data?.detail || err.message));
        }
    };

    const handleLogout = () => {
        localStorage.removeItem('token');
        router.push('/auth/login');
    };

    return (
        <div className="min-h-screen bg-gray-50">
            {/* Header */}
            <div className="bg-blue-600 text-white p-6 shadow">
                <div className="flex justify-between items-center">
                    <h1 className="text-3xl font-bold">Super-Admin Dashboard</h1>
                    <button
                        onClick={handleLogout}
                        className="bg-red-500 hover:bg-red-600 px-4 py-2 rounded"
                    >
                        Logout
                    </button>
                </div>
            </div>

            {/* Tabs */}
            <div className="bg-white border-b">
                <div className="flex max-w-6xl mx-auto">
                    <button
                        onClick={() => setActiveTab('hospitals')}
                        className={`px-6 py-4 font-medium border-b-2 ${activeTab === 'hospitals'
                            ? 'border-blue-600 text-blue-600'
                            : 'border-transparent text-gray-600 hover:text-gray-900'
                            }`}
                    >
                        Hospitals
                    </button>
                    <button
                        onClick={() => setActiveTab('users')}
                        className={`px-6 py-4 font-medium border-b-2 ${activeTab === 'users'
                            ? 'border-blue-600 text-blue-600'
                            : 'border-transparent text-gray-600 hover:text-gray-900'
                            }`}
                    >
                        Users
                    </button>
                </div>
            </div>

            {/* Main Content */}
            <div className="max-w-6xl mx-auto p-6">
                {error && (
                    <div className="mb-4 p-4 bg-red-50 border border-red-200 rounded text-red-700 text-sm">
                        {error}
                    </div>
                )}

                {/* Hospitals Tab */}
                {activeTab === 'hospitals' && (
                    <div>
                        <div className="flex justify-between items-center mb-6">
                            <h2 className="text-2xl font-bold">Manage Hospitals</h2>
                            <button
                                onClick={() => setShowCreateForm(!showCreateForm)}
                                className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded"
                            >
                                {showCreateForm ? 'Cancel' : 'Create Hospital'}
                            </button>
                        </div>

                        {showCreateForm && (
                            <form onSubmit={handleCreateHospital} className="mb-6 p-6 bg-white rounded-lg shadow">
                                <h3 className="text-lg font-bold mb-4">New Hospital</h3>
                                <div className="grid grid-cols-2 gap-4">
                                    <input type="text" name="name" placeholder="Name" value={formData.name} onChange={handleInputChange} className="px-3 py-2 border rounded bg-white text-gray-900" required />
                                    <input type="text" name="registration_number" placeholder="Reg Number" value={formData.registration_number} onChange={handleInputChange} className="px-3 py-2 border rounded bg-white text-gray-900" required />
                                    <input type="text" name="address" placeholder="Address" value={formData.address} onChange={handleInputChange} className="px-3 py-2 border rounded bg-white text-gray-900" required />
                                    <input type="text" name="city" placeholder="City" value={formData.city} onChange={handleInputChange} className="px-3 py-2 border rounded bg-white text-gray-900" required />
                                    <input type="text" name="state" placeholder="State" value={formData.state} onChange={handleInputChange} className="px-3 py-2 border rounded bg-white text-gray-900" required />
                                    <input type="text" name="country" placeholder="Country" value={formData.country} onChange={handleInputChange} className="px-3 py-2 border rounded bg-white text-gray-900" required />
                                    <input type="email" name="contact_email" placeholder="Email" value={formData.contact_email} onChange={handleInputChange} className="px-3 py-2 border rounded bg-white text-gray-900" required />
                                    <input type="tel" name="contact_phone" placeholder="Phone" value={formData.contact_phone} onChange={handleInputChange} className="px-3 py-2 border rounded bg-white text-gray-900" required />
                                    <input type="text" name="admin_id" placeholder="Hospital Admin ID (optional if creating a new one below)" value={formData.admin_id} onChange={handleInputChange} className="col-span-2 px-3 py-2 border rounded bg-white text-gray-900" />
                                    <input type="email" name="admin_email" placeholder="Or create hospital-admin email" value={formData.admin_email} onChange={handleInputChange} className="px-3 py-2 border rounded bg-white text-gray-900" />
                                    <input type="text" name="admin_username" placeholder="Hospital-admin username" value={formData.admin_username} onChange={handleInputChange} className="px-3 py-2 border rounded bg-white text-gray-900" />
                                    <input type="password" name="admin_password" placeholder="Hospital-admin password" value={formData.admin_password} onChange={handleInputChange} className="px-3 py-2 border rounded bg-white text-gray-900" />
                                </div>
                                <p className="mt-3 text-xs text-gray-500">
                                    Fill the admin ID to reuse an existing hospital-admin, or leave it blank and provide the three admin creation fields to create one automatically.
                                </p>
                                <button type="submit" className="mt-4 bg-green-600 hover:bg-green-700 text-white px-4 py-2 rounded">Create Hospital</button>
                            </form>
                        )}

                        {loading ? (
                            <p className="text-center py-8">Loading hospitals...</p>
                        ) : (
                            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                                {hospitals.map(hospital => (
                                    <div key={hospital.id} className="bg-white p-6 rounded-lg shadow">
                                        <h3 className="text-lg font-bold text-blue-600">{hospital.name}</h3>
                                        <p className="text-sm text-gray-600 mt-2"><strong>Reg:</strong> {hospital.registration_number}</p>
                                        <p className="text-sm text-gray-600"><strong>Location:</strong> {hospital.city}, {hospital.state}</p>
                                        <p className="text-sm text-gray-600"><strong>Email:</strong> {hospital.contact_email}</p>
                                        <div className="mt-4 flex gap-2">
                                            <button onClick={() => navigator.clipboard.writeText(hospital.id)} className="flex-1 bg-blue-600 hover:bg-blue-700 text-white px-3 py-2 rounded text-sm">Copy Hospital ID</button>
                                            <button onClick={() => handleDeleteHospital(hospital.id)} className="flex-1 bg-red-600 hover:bg-red-700 text-white px-3 py-2 rounded text-sm">Delete</button>
                                        </div>
                                    </div>
                                ))}
                            </div>
                        )}
                    </div>
                )}

                {/* Users Tab */}
                {activeTab === 'users' && (
                    <div>
                        <h2 className="text-2xl font-bold mb-6">Manage Users</h2>
                        <div className="p-4 bg-blue-50 border border-blue-200 rounded">
                            <p className="text-sm text-blue-800"><strong>Super-Admin Controls:</strong></p>
                            <ul className="text-sm text-blue-800 mt-2 list-disc list-inside">
                                <li>Create hospital-admin accounts via /api/admin/users/ endpoint</li>
                                <li>Create doctor accounts for any hospital</li>
                                <li>Manage all hospitals and system configuration</li>
                            </ul>
                        </div>
                    </div>
                )}
            </div>
        </div>
    );
}

export default function AdminDashboard() {
    return (
        <ProtectedRoute allowedRoles={['admin']} requireSuperAdmin={true}>
            <AdminDashboardContent />
        </ProtectedRoute>
    );
}
