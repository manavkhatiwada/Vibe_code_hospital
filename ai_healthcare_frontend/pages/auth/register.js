import { useState } from 'react';
import { useRouter } from 'next/router';
import api from '../../utils/api';
import Link from 'next/link';
import { jwtDecode } from 'jwt-decode';

export default function Register() {
  const router = useRouter();
  const [formData, setFormData] = useState({ username: '', email: '', password: '', role: 'PATIENT' });
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleChange = (e) => setFormData({ ...formData, [e.target.name]: e.target.value });

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      await api.post('/register/', formData);

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
      } else if (role === 'hospital') {
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
          <div>
            <label className="block text-sm font-medium text-gray-700">Role</label>
            <select
              name="role"
              value={formData.role}
              onChange={handleChange}
              className="mt-1 w-full px-4 py-2 border rounded-lg text-gray-900 bg-white focus:ring-blue-500 focus:border-blue-500"
            >
              <option value="PATIENT">Patient</option>
              <option value="DOCTOR">Doctor</option>
              <option value="HOSPITAL">Hospital Admin</option>
            </select>
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
      </div>
    </div>
  );
}
