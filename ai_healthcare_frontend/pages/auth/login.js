import { useState } from 'react';
import { useRouter } from 'next/router';
import api from '../../utils/api';
import { jwtDecode } from 'jwt-decode';
import Link from 'next/link';

const FEATURES = [
  { icon: '🤖', title: 'AI Symptom Checker', desc: 'Describe your symptoms and get instant preliminary analysis powered by Gemini AI.' },
  { icon: '📅', title: 'Appointment Booking', desc: 'Browse verified doctors and book appointments in seconds.' },
  { icon: '📂', title: 'Private Medical Records', desc: 'Upload, manage, and securely share your health records with chosen doctors.' },
  { icon: '🏥', title: 'Hospital Network', desc: 'Access a growing network of hospitals and specialists across Nepal.' },
];

export default function Login() {
  const router = useRouter();
  const [formData, setFormData] = useState({ email: '', password: '' });
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleChange = (e) => setFormData({ ...formData, [e.target.name]: e.target.value });

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);
    try {
      const { data } = await api.post('/login/', formData);
      const token = data.access || data.token;
      if (!token) throw new Error('No token returned from server.');
      localStorage.setItem('token', token);
      const decoded = jwtDecode(token);
      const role = (decoded.role || data.role || 'patient').toLowerCase();
      const isSuper = decoded.is_superuser || data.is_superuser || false;
      if (role === 'admin' && isSuper) router.push('/admin/dashboard');
      else if (role === 'doctor') router.push('/doctor/dashboard');
      else if (role === 'admin') router.push('/hospital/dashboard');
      else router.push('/patient/dashboard');
    } catch (err) {
      setError(err.response?.data?.detail || err.response?.data?.error || err.message || 'Invalid credentials');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex">
      {/* ── Left brand panel ── */}
      <div className="hidden lg:flex lg:w-[55%] bg-linear-to-br from-blue-600 via-blue-700 to-indigo-900 flex-col justify-between p-14 text-white relative overflow-hidden">
        {/* decorative circles */}
        <div className="absolute -top-24 -right-24 w-96 h-96 bg-white/5 rounded-full" />
        <div className="absolute -bottom-20 -left-20 w-80 h-80 bg-white/5 rounded-full" />
        <div className="absolute top-1/2 right-12 w-48 h-48 bg-white/5 rounded-full -translate-y-1/2" />

        <div className="relative z-10">
          {/* Logo */}
          <div className="flex items-center gap-3 mb-14">
            <div className="w-11 h-11 bg-white rounded-2xl flex items-center justify-center shadow-lg">
              <span className="text-blue-600 font-black text-xl">+</span>
            </div>
            <span className="text-2xl font-bold tracking-tight">Open Care</span>
          </div>

          <h1 className="text-5xl font-extrabold leading-tight mb-4">
            Nepal&apos;s First<br />AI-Powered<br />Healthcare Platform
          </h1>
          <p className="text-blue-200 text-lg mb-12 max-w-sm">
            Smart diagnostics, verified doctors, and private health records — all in one place.
          </p>

          <div className="space-y-5">
            {FEATURES.map((f) => (
              <div key={f.title} className="flex items-start gap-4">
                <div className="w-11 h-11 bg-white/15 backdrop-blur rounded-xl flex items-center justify-center text-xl shrink-0">
                  {f.icon}
                </div>
                <div>
                  <p className="font-semibold text-white">{f.title}</p>
                  <p className="text-blue-200 text-sm leading-relaxed">{f.desc}</p>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Stats bar */}
        <div className="relative z-10 flex gap-10 pt-8 border-t border-white/20">
          <div>
            <p className="text-3xl font-extrabold">24/7</p>
            <p className="text-blue-200 text-sm">AI Support</p>
          </div>
          <div>
            <p className="text-3xl font-extrabold">Free</p>
            <p className="text-blue-200 text-sm">For Patients</p>
          </div>
          <div>
            <p className="text-3xl font-extrabold">100%</p>
            <p className="text-blue-200 text-sm">Private Records</p>
          </div>
        </div>
      </div>

      {/* ── Right form panel ── */}
      <div className="flex-1 flex items-center justify-center bg-gray-50 p-8">
        <div className="w-full max-w-md">
          {/* Mobile logo */}
          <div className="lg:hidden flex items-center justify-center gap-2 mb-8">
            <div className="w-9 h-9 bg-blue-600 rounded-xl flex items-center justify-center">
              <span className="text-white font-black text-lg">+</span>
            </div>
            <span className="text-xl font-bold text-blue-700">Open Care</span>
          </div>

          <h2 className="text-3xl font-extrabold text-gray-900 mb-1">Welcome back</h2>
          <p className="text-gray-500 mb-8">Sign in to your Open Care account</p>

          {error && (
            <div className="mb-5 px-4 py-3 bg-red-50 border border-red-200 rounded-xl text-red-600 text-sm">
              {error}
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-5">
            <div>
              <label className="block text-sm font-semibold text-gray-700 mb-1.5">Email address</label>
              <input
                name="email"
                type="email"
                required
                onChange={handleChange}
                placeholder="you@example.com"
                className="w-full px-4 py-3 border border-gray-200 rounded-xl text-gray-900 bg-white focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent placeholder:text-gray-400 transition"
              />
            </div>
            <div>
              <label className="block text-sm font-semibold text-gray-700 mb-1.5">Password</label>
              <input
                name="password"
                type="password"
                required
                onChange={handleChange}
                placeholder="••••••••"
                className="w-full px-4 py-3 border border-gray-200 rounded-xl text-gray-900 bg-white focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent placeholder:text-gray-400 transition"
              />
            </div>
            <button
              type="submit"
              disabled={loading}
              className="w-full py-3 bg-blue-600 text-white font-bold rounded-xl shadow-md hover:bg-blue-700 disabled:bg-blue-300 disabled:cursor-not-allowed focus:outline-none focus:ring-2 focus:ring-blue-500 transition"
            >
              {loading ? 'Signing in…' : 'Sign In'}
            </button>
          </form>

          <p className="mt-6 text-center text-sm text-gray-500">
            Don&apos;t have an account?{' '}
            <Link href="/auth/register" className="text-blue-600 font-semibold hover:underline">
              Create one free
            </Link>
          </p>

          <p className="mt-8 text-center text-xs text-gray-400">
            By signing in you agree to Open Care&apos;s Terms of Service and Privacy Policy.
          </p>
        </div>
      </div>
    </div>
  );
}
