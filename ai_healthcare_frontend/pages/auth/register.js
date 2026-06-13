import { useState } from 'react';
import { useRouter } from 'next/router';
import api from '../../utils/api';
import Link from 'next/link';
import { jwtDecode } from 'jwt-decode';

export default function Register() {
  const router = useRouter();
  const [selectedRole, setSelectedRole] = useState('PATIENT');
  const [formData, setFormData] = useState({ username: '', email: '', password: '', role: 'PATIENT' });
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleChange = (e) => setFormData({ ...formData, [e.target.name]: e.target.value });

  const handleRoleSelect = (role) => {
    setSelectedRole(role);
    setError('');
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      await api.post('/register/', { ...formData, role: 'PATIENT' });

      // Auto-login after successful registration for smoother onboarding.
      const { data } = await api.post('/login/', {
        email: formData.email,
        password: formData.password,
      });

      const token = data.access || data.token;
      if (!token) throw new Error('No token returned from server.');

      localStorage.setItem('token', token);

      const decoded = jwtDecode(token);
      const role = (decoded.role || data.role || formData.role).toLowerCase();

      if (role === 'doctor') {
        router.push('/doctor/dashboard');
      } else if (role === 'admin' || role === 'hospital') {
        router.push('/hospital/dashboard');
      } else {
        router.push('/patient/dashboard');
      }
    } catch (err) {
      let errMsg = 'Registration failed. Please check your details.';
      const resData = err.response?.data;
      if (resData) {
        if (typeof resData === 'string') errMsg = resData;
        else if (resData.detail) errMsg = resData.detail;
        else if (resData.error) errMsg = resData.error;
        else {
          const firstKey = Object.keys(resData)[0];
          const firstError = resData[firstKey];
          errMsg = `${firstKey.charAt(0).toUpperCase() + firstKey.slice(1)}: ${Array.isArray(firstError) ? firstError[0] : firstError}`;
        }
      }
      setError(errMsg);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50">
      <div className="max-w-md w-full p-8 bg-white rounded-lg shadow-lg">
        <h2 className="text-3xl font-extrabold text-center text-blue-600 mb-6">Create Account</h2>

        {/* Role selector */}
        <div className="flex rounded-lg border border-gray-200 overflow-hidden mb-6">
          <button
            type="button"
            onClick={() => handleRoleSelect('PATIENT')}
            className={`flex-1 py-2 text-sm font-semibold transition-colors duration-150 ${
              selectedRole === 'PATIENT'
                ? 'bg-blue-600 text-white'
                : 'bg-white text-gray-600 hover:bg-gray-50'
            }`}
          >
            Patient
          </button>
          <button
            type="button"
            onClick={() => handleRoleSelect('DOCTOR')}
            className={`flex-1 py-2 text-sm font-semibold transition-colors duration-150 ${
              selectedRole === 'DOCTOR'
                ? 'bg-blue-600 text-white'
                : 'bg-white text-gray-600 hover:bg-gray-50'
            }`}
          >
            Doctor
          </button>
        </div>

        {selectedRole === 'DOCTOR' ? (
          <div className="rounded-lg bg-blue-50 border border-blue-200 p-5 text-center space-y-2">
            <p className="text-blue-800 font-semibold text-sm">Doctor accounts are created by your hospital admin.</p>
            <p className="text-blue-700 text-xs">
              Ask your hospital administrator to add you to Open Care. Once created, you can log in directly.
            </p>
            <Link href="/auth/login" className="inline-block mt-2 text-blue-600 text-sm font-medium hover:underline">
              Already have an account? Login here
            </Link>
          </div>
        ) : (
          <>
            {error && <p className="text-red-500 text-sm mb-4 text-center">{error}</p>}
            <form onSubmit={handleSubmit} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700">Username</label>
                <input name="username" type="text" required value={formData.username} onChange={handleChange} className="mt-1 w-full px-4 py-2 border rounded-lg text-gray-900 bg-white focus:ring-blue-500 focus:border-blue-500" />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700">Email</label>
                <input name="email" type="email" required value={formData.email} onChange={handleChange} className="mt-1 w-full px-4 py-2 border rounded-lg text-gray-900 bg-white focus:ring-blue-500 focus:border-blue-500" />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700">Password</label>
                <input name="password" type="password" required value={formData.password} onChange={handleChange} className="mt-1 w-full px-4 py-2 border rounded-lg text-gray-900 bg-white focus:ring-blue-500 focus:border-blue-500" />
              </div>
              <button
                type="submit"
                disabled={loading}
                className="w-full py-2 px-4 bg-blue-600 text-white font-semibold rounded-lg shadow-md hover:bg-blue-700 disabled:bg-blue-300 disabled:cursor-not-allowed focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-opacity-75 transition duration-150"
              >
                {loading ? 'Creating account...' : 'Register'}
              </button>
            </form>
            <p className="mt-6 text-center text-sm text-gray-600">
              Already have an account? <Link href="/auth/login" className="text-blue-600 font-medium hover:underline">Login here</Link>
            </p>
          </>
        )}
      </div>
    </div>
  );
}
