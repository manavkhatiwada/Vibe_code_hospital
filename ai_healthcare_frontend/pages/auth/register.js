import { useState } from 'react';
import { useRouter } from 'next/router';
import api from '../../utils/api';
import Link from 'next/link';
import { jwtDecode } from 'jwt-decode';

export default function Register() {
  const router = useRouter();
  const [selectedRole, setSelectedRole] = useState('PATIENT');
  const [formData, setFormData] = useState({
    username: '', email: '', password: '',
    specialization: '', licence_number: '', qualifications: '', experience_years: '', consultation_fee: '',
  });
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
      const payload = selectedRole === 'DOCTOR'
        ? { ...formData, role: 'DOCTOR' }
        : { username: formData.username, email: formData.email, password: formData.password, role: 'PATIENT' };
      await api.post('/register/', payload);

      // Auto-login after successful registration for smoother onboarding.
      const { data } = await api.post('/login/', {
        email: formData.email,
        password: formData.password,
      });

      const token = data.access || data.token;
      if (!token) throw new Error('No token returned from server.');

      localStorage.setItem('token', token);

      const decoded = jwtDecode(token);
      const role = (decoded.role || data.role || selectedRole).toLowerCase();

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

          {selectedRole === 'DOCTOR' && (
            <>
              <div className="border-t pt-4">
                <p className="text-xs text-gray-500 mb-3 font-medium uppercase tracking-wide">Professional Details</p>
                <div className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700">Specialization</label>
                    <input name="specialization" type="text" value={formData.specialization} onChange={handleChange} placeholder="e.g. Cardiology" className="mt-1 w-full px-4 py-2 border rounded-lg text-gray-900 bg-white focus:ring-blue-500 focus:border-blue-500" />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700">Licence Number</label>
                    <input name="licence_number" type="text" required value={formData.licence_number} onChange={handleChange} className="mt-1 w-full px-4 py-2 border rounded-lg text-gray-900 bg-white focus:ring-blue-500 focus:border-blue-500" />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700">Qualifications</label>
                    <input name="qualifications" type="text" required value={formData.qualifications} onChange={handleChange} placeholder="e.g. MBBS, MD" className="mt-1 w-full px-4 py-2 border rounded-lg text-gray-900 bg-white focus:ring-blue-500 focus:border-blue-500" />
                  </div>
                  <div className="grid grid-cols-2 gap-3">
                    <div>
                      <label className="block text-sm font-medium text-gray-700">Experience (years)</label>
                      <input name="experience_years" type="number" min="0" required value={formData.experience_years} onChange={handleChange} className="mt-1 w-full px-4 py-2 border rounded-lg text-gray-900 bg-white focus:ring-blue-500 focus:border-blue-500" />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700">Consultation Fee ($)</label>
                      <input name="consultation_fee" type="number" min="0" step="0.01" required value={formData.consultation_fee} onChange={handleChange} className="mt-1 w-full px-4 py-2 border rounded-lg text-gray-900 bg-white focus:ring-blue-500 focus:border-blue-500" />
                    </div>
                  </div>
                </div>
              </div>
            </>
          )}

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
