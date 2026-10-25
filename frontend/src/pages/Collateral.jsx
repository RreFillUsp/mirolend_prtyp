import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth';
import { 
  Package, 
  Plus, 
  Eye, 
  Calendar, 
  CheckCircle, 
  Clock, 
  AlertCircle,
  ArrowLeft,
  Loader2
} from 'lucide-react';
import toast from 'react-hot-toast';
import api from '../api/client';

export default function Collateral() {
  const { user } = useAuth();
  const [collaterals, setCollaterals] = useState([]);
  const [loans, setLoans] = useState([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    setIsLoading(true);
    try {
      // Fetch collateral
      const collatResponse = await api.get('/collateral');
      setCollaterals(collatResponse.data || []);
      
      // Fetch loans to determine redemption dates
      const loansResponse = await api.get('/loans/applications');
      setLoans(loansResponse.data || []);
    } catch (error) {
      console.error('Error fetching data:', error);
      toast.error('Failed to load collateral');
    } finally {
      setIsLoading(false);
    }
  };

  // Find loan associated with collateral
  const getLoanForCollateral = (collateralId) => {
    return loans.find(loan => loan.collateral_id === collateralId);
  };

  // Format date
  const formatDate = (dateString) => {
    if (!dateString) return 'N/A';
    try {
      return new Date(dateString).toLocaleDateString('en-BW', {
        year: 'numeric',
        month: 'short',
        day: 'numeric'
      });
    } catch {
      return dateString;
    }
  };

  // Get status badge
  const getStatusBadge = (collateral) => {
    if (collateral.is_encumbered) {
      const loan = getLoanForCollateral(collateral.id);
      if (loan) {
        if (loan.status === 'completed' || loan.status === 'repaid') {
          return { text: 'Released', color: 'bg-green-100 text-green-800', icon: <CheckCircle size={14} /> };
        }
        return { text: 'Under Loan', color: 'bg-blue-100 text-blue-800', icon: <Clock size={14} /> };
      }
      return { text: 'Encumbered', color: 'bg-yellow-100 text-yellow-800', icon: <AlertCircle size={14} /> };
    }
    return { text: 'Available', color: 'bg-green-100 text-green-800', icon: <CheckCircle size={14} /> };
  };

  // Get redemption date
  const getRedemptionDate = (collateral) => {
    if (!collateral.is_encumbered) return null;
    const loan = getLoanForCollateral(collateral.id);
    if (loan && loan.end_date) {
      return formatDate(loan.end_date);
    }
    return 'Unknown';
  };

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <Loader2 className="animate-spin text-blue-600" size={40} />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
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
                <span className="ml-2 text-xs bg-blue-50 text-blue-600 px-2 py-0.5 rounded-full font-medium">My Collateral</span>
              </div>
            </div>
            <Link
              to="/loans/apply"
              className="inline-flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-xl hover:bg-blue-700 transition-colors"
            >
              <Plus size={18} />
              Add Collateral
            </Link>
          </div>
        </div>
      </header>

      <main className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="mb-6">
          <h1 className="text-3xl font-bold text-gray-800">My Collateral</h1>
          <p className="text-gray-500 mt-1">View and manage your collateral items</p>
        </div>

        {collaterals.length === 0 ? (
          <div className="bg-white rounded-2xl shadow-sm border border-gray-100 p-12 text-center">
            <Package className="mx-auto text-gray-300" size={64} />
            <h3 className="text-lg font-semibold text-gray-800 mt-4">No Collateral Items</h3>
            <p className="text-gray-500 mt-2">Add items to use as collateral for loans</p>
            <Link
              to="/loans/apply"
              className="inline-block mt-4 px-6 py-2 bg-blue-600 text-white rounded-xl hover:bg-blue-700 transition-colors"
            >
              Add Your First Item
            </Link>
          </div>
        ) : (
          <div className="space-y-4">
            {collaterals.map((item) => {
              const status = getStatusBadge(item);
              const redemptionDate = getRedemptionDate(item);
              const loan = getLoanForCollateral(item.id);
              
              return (
                <div key={item.id} className="bg-white rounded-2xl shadow-sm border border-gray-100 p-6 hover:shadow-md transition-shadow">
                  <div className="flex flex-col sm:flex-row sm:items-start sm:justify-between gap-4">
                    <div className="flex-1">
                      <div className="flex items-center flex-wrap gap-3">
                        <h3 className="text-lg font-bold text-gray-800">
                          {item.brand} {item.model}
                        </h3>
                        <span className={`px-3 py-1 rounded-full text-xs font-medium flex items-center gap-1.5 ${status.color}`}>
                          {status.icon}
                          {status.text}
                        </span>
                      </div>
                      <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 mt-3 text-sm">
                        <div>
                          <p className="text-gray-500 text-xs">Type</p>
                          <p className="font-medium text-gray-700 capitalize">{item.item_type}</p>
                        </div>
                        <div>
                          <p className="text-gray-500 text-xs">Value</p>
                          <p className="font-medium text-gray-700">P{item.estimated_value?.toLocaleString()}</p>
                        </div>
                        <div>
                          <p className="text-gray-500 text-xs">Condition</p>
                          <p className="font-medium text-gray-700 capitalize">{item.condition}</p>
                        </div>
                        <div>
                          <p className="text-gray-500 text-xs">Status</p>
                          <p className="font-medium text-gray-700">{status.text}</p>
                        </div>
                      </div>
                      
{item.images && typeof item.images === 'string' ? JSON.parse(item.images) : item.images || []}


                      {item.images && item.images.length > 0 && (
                        <div className="flex gap-2 mt-3">
                          {item.images.slice(0, 3).map((img, idx) => (
                            <img 
                              key={idx} 
                              src={img} 
                              alt={`Collateral ${idx}`} 
                              className="w-12 h-12 rounded-lg object-cover border border-gray-200"
                            />
                          ))}
                          {item.images.length > 3 && (
                            <div className="w-12 h-12 rounded-lg bg-gray-100 flex items-center justify-center text-xs text-gray-500">
                              +{item.images.length - 3}
                            </div>
                          )}
                        </div>
                      )}
                    </div>
                    
                    <div className="flex flex-col gap-2 sm:items-end min-w-[140px]">
                      {item.is_encumbered && loan ? (
                        <>
                          <div className="text-sm">
                            <span className="text-gray-500">Loan: </span>
                            <span className="font-medium">{loan.contract_number || 'N/A'}</span>
                          </div>
                          <div className="text-sm">
                            <span className="text-gray-500">Redeem by: </span>
                            <span className="font-medium text-orange-600">{redemptionDate || 'N/A'}</span>
                          </div>
                          <Link
                            to={`/loans/${loan.id}`}
                            className="text-blue-600 hover:text-blue-700 text-sm font-medium"
                          >
                            View Loan →
                          </Link>

<Link
  to="/loans/apply"
  className="inline-flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-xl hover:bg-blue-700 transition-colors"
>
  <Plus size={18} />
  Add Collateral
</Link>

                        </>
                      ) : (
                        <div className="text-sm text-green-600">
                          <CheckCircle size={16} className="inline mr-1" />
                          Available for loan
                        </div>
                      )}
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </main>
    </div>
  );
}