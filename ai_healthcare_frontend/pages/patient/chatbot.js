import ProtectedRoute from '../../components/ProtectedRoute';
import Chatbot from '../../components/Chatbot';
import Link from 'next/link';

export default function ChatbotPage() {
  return (
    <ProtectedRoute allowedRoles={['patient']}>
      <div className="min-h-screen bg-gray-50 p-8 flex flex-col items-center">
        <div className="w-full max-w-2xl flex items-center mb-6">
          <Link href="/patient/dashboard" className="text-blue-600 hover:underline">← Back to Dashboard</Link>
        </div>
        <Chatbot />
      </div>
    </ProtectedRoute>
  );
}
