import { useState } from 'react';
import { useRouter } from 'next/router';
import api from '../../utils/api';
import { jwtDecode } from 'jwt-decode';
import Link from 'next/link';

export default function Login() {
  const router = useRouter();
  const [formData, setFormData] = useState({ email: '', password: '' });
  const [error, setError] = useState('');

  const handleChange = (e) => setFormData({ ...formData, [e.target.name]: e.target.value });

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const { data } = await api.post('/login/', formData);
      const token = data.access || data.token; // Handle standard or SimpleJWT shapes

      if (!token) throw new Error("No token returned from server.");

      localStorage.setItem('token', token);

      const decoded = jwtDecode(token);
      const role = (decoded.role || data.role || 'patient').toLowerCase();

      if (role === 'doctor') {
        router.push('/doctor/dashboard');
      } else if (role === 'admin' || role === 'hospital') {
        router.push('/hospital/dashboard');
      } else {
        router.push('/patient/dashboard');
      }

    } catch (err) {
      setError(err.response?.data?.detail || err.response?.data?.error || err.message || 'Invalid credentials');
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50">
      <div className="max-w-md w-full p-8 bg-white rounded-lg shadow-lg">
        <h2 className="text-3xl font-extrabold text-center text-blue-600 mb-6">Welcome Back</h2>
        {error && <p className="text-red-500 text-sm mb-4 text-center">{error}</p>}
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700">Email</label>
            <input name="email" type="email" required onChange={handleChange} className="mt-1 w-full px-4 py-2 border rounded-lg text-gray-900 bg-white focus:ring-blue-500 focus:border-blue-500" />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700">Password</label>
            <input name="password" type="password" required onChange={handleChange} className="mt-1 w-full px-4 py-2 border rounded-lg text-gray-900 bg-white focus:ring-blue-500 focus:border-blue-500" />
          </div>
          <button type="submit" className="w-full py-2 px-4 bg-blue-600 text-white font-semibold rounded-lg shadow-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-opacity-75 transition duration-150">
            Login
          </button>
        </form>
        <p className="mt-6 text-center text-sm text-gray-600">
          Don&apos;t have an account? <Link href="/auth/register" className="text-blue-600 font-medium hover:underline">Register here</Link>
        </p>
      </div>
    </div>
  );
}
