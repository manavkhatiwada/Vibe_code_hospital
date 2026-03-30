import Link from 'next/link';

export default function Home() {
  return (
    <div className="min-h-screen bg-linear-to-br from-blue-50 to-white flex flex-col items-center justify-center p-8">
      <div className="max-w-3xl text-center">
        <div className="text-6xl mb-6">🏥</div>
        <h1 className="text-5xl font-extrabold text-blue-900 mb-6 tracking-tight drop-shadow-sm">
          Welcome to <span className="text-blue-600">AI Healthcare</span>
        </h1>
        <p className="text-xl text-gray-600 mb-12 leading-relaxed max-w-2xl mx-auto">
          The future of patient management and symptom analysis. Accessible dashboards for doctors, patients, and hospital administrators.
        </p>

        <div className="flex flex-col sm:flex-row justify-center gap-4 sm:gap-6">
          <Link
            href="/auth/login"
            className="px-8 py-4 bg-blue-600 text-white text-lg font-bold rounded-xl shadow-lg hover:bg-blue-700 hover:shadow-xl transition transform hover:-translate-y-1"
          >
            Login to Dashboard
          </Link>
          <Link
            href="/auth/register"
            className="px-8 py-4 bg-white text-blue-600 text-lg font-bold rounded-xl shadow-md border border-gray-100 hover:bg-blue-50 transition transform hover:-translate-y-1"
          >
            Create an Account
          </Link>
        </div>
      </div>
    </div>
  );
}
