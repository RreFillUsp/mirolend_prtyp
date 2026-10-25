// frontend/src/pages/Payments.jsx
import { Link } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth';
import { ArrowLeft, CreditCard, Calendar, Clock } from 'lucide-react';

export default function Payments() {
  const { user } = useAuth();

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white border-b border-gray-200 sticky top-0 z-50 shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center gap-2">
              <Link to="/dashboard" className="p-2 hover:bg-gray-100 rounded-xl transition-colors">
                <ArrowLeft size={20} className="text-gray-600" />
              </Link>
              <div className="w-10 h-10 bg-gradient-to-br from-blue-600 to-blue-700 rounded-xl flex items-center justify-center shadow-lg">
                <span className="text-white font-bold text-lg">ML</span>
              </div>
              <div>
                <span className="text-xl font-bold text-gray-800">MicroLend</span>
                <span className="ml-2 text-xs bg-blue-50 text-blue-600 px-2 py-0.5 rounded-full font-medium">Payments</span>
              </div>
            </div>
            <span className="text-sm text-gray-600 hidden sm:block">
              {user?.firstName} {user?.lastName}
            </span>
          </div>
        </div>
      </header>

      <main className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="bg-white rounded-2xl shadow-sm border border-gray-100 p-12 text-center">
          <CreditCard className="mx-auto text-gray-300" size={64} />
          <h3 className="text-lg font-semibold text-gray-800 mt-4">Payments</h3>
          <p className="text-gray-500 mt-2 max-w-sm mx-auto">
            View your payment history and make payments for active loans.
          </p>
          <p className="text-gray-400 text-sm mt-4">Coming soon...</p>
          <Link
            to="/dashboard"
            className="inline-block mt-6 px-6 py-2 bg-blue-600 text-white rounded-xl hover:bg-blue-700 transition-colors"
          >
            Back to Dashboard
          </Link>
        </div>
      </main>
    </div>
  );
}