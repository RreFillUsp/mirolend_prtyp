// frontend/src/pages/MyLoans.jsx
import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth';
import { 
  ArrowLeft, 
  FileText, 
  CheckCircle, 
  Clock, 
  AlertCircle,
  Plus,
  Eye
} from 'lucide-react';
import toast from 'react-hot-toast';
import api from '../api/client';

export default function MyLoans() {
  const { user } = useAuth();
  const [loans, setLoans] = useState([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const fetchLoans = async () => {
      try {
        const response = await api.get('/loans/applications');
        setLoans(response.data || []);
      } catch (error) {
        console.error('Error fetching loans:', error);
        toast.error('Failed to load loans');
      } finally {
        setIsLoading(false);
      }
    };
    fetchLoans();
  }, []);

  const getStatusColor = (status) => {
    const colors = {
      pending: 'bg-yellow-100 text-yellow-800',
      under_review: 'bg-blue-100 text-blue-800',
      approved: 'bg-green-100 text-green-800',
      rejected: 'bg-red-100 text-red-800',
      disbursed: 'bg-purple-100 text-purple-800',
      completed: 'bg-green-100 text-green-800',
      defaulted: 'bg-red-100 text-red-800',
    };
    return colors[status] || 'bg-gray-100 text-gray-800';
  };

  const getStatusIcon = (status) => {
    switch(status) {
      case 'pending':
      case 'under_review':
        return <Clock size={16} />;
      case 'approved':
      case 'disbursed':
        return <CheckCircle size={16} />;
      case 'rejected':
      case 'defaulted':
        return <AlertCircle size={16} />;
      default:
        return <FileText size={16} />;
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white border-b border-gray-200 sticky top-0 z-50 shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center gap-2">
              <div className="w-10 h-10 bg-gradient-to-br from-blue-600 to-blue-700 rounded-xl flex items-center justify-center shadow-lg">
                <span className="text-white font-bold text-lg">ML</span>
              </div>
              <span className="text-xl font-bold text-gray-800">MicroLend</span>
              <span className="ml-2 text-xs bg-blue-50 text-blue-600 px-2 py-0.5 rounded-full font-medium">My Loans</span>
            </div>
          </div>
        </div>
      </header>

      <main className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="flex items-center justify-between mb-6">
          <div>
            <h1 className="text-3xl font-bold text-gray-800">My Loans</h1>
            <p className="text-gray-500 mt-1">Track all your loan applications</p>
          </div>
          <Link
            to="/loans/apply"
            className="inline-flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-xl hover:bg-blue-700 transition-colors"
          >
            <Plus size={20} />
            Apply for Loan
          </Link>
        </div>

        {isLoading ? (
          <div className="text-center py-12">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
            <p className="text-gray-500 mt-4">Loading your loans...</p>
          </div>
        ) : loans.length === 0 ? (
          <div className="bg-white rounded-2xl shadow-sm border border-gray-100 p-12 text-center">
            <FileText className="mx-auto text-gray-300" size={64} />
            <h3 className="text-lg font-semibold text-gray-800 mt-4">No Loans Yet</h3>
            <p className="text-gray-500 mt-2">You haven't applied for any loans yet</p>
            <Link
              to="/loans/apply"
              className="inline-block mt-4 px-6 py-2 bg-blue-600 text-white rounded-xl hover:bg-blue-700 transition-colors"
            >
              Apply for Your First Loan
            </Link>
          </div>
        ) : (
          <div className="space-y-4">
            {loans.map((loan) => (
              <div key={loan.id} className="bg-white rounded-2xl shadow-sm border border-gray-100 p-6 hover:shadow-md transition-shadow">
                <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
                  <div>
                    <div className="flex items-center gap-3">
                      <h3 className="text-lg font-semibold text-gray-800">
                        P{loan.amount.toLocaleString()}
                      </h3>
                      <span className={`px-2 py-1 rounded-full text-xs font-medium flex items-center gap-1 ${getStatusColor(loan.status)}`}>
                        {getStatusIcon(loan.status)}
                        {loan.status.replace('_', ' ')}
                      </span>
                    </div>
                    <div className="flex flex-wrap gap-4 mt-2 text-sm text-gray-500">
                      <span>Term: {loan.term_months} months</span>
                      <span>Interest: {loan.interest_rate}%</span>
                      <span>Monthly: P{loan.monthly_installment?.toFixed(2) || 'N/A'}</span>
                      <span>Total: P{loan.total_repayment?.toFixed(2) || 'N/A'}</span>
                    </div>
                  </div>
                  <Link
                    to={`/loans/${loan.id}`}
                    className="inline-flex items-center gap-1 text-blue-600 hover:text-blue-700 font-medium"
                  >
                    View Details <Eye size={16} />
                  </Link>
                </div>
              </div>
            ))}
          </div>
        )}
      </main>
    </div>
  );
}