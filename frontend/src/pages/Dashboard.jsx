// frontend/src/pages/Dashboard.jsx
import { useState, useEffect } from 'react';
import { useAuth } from '../hooks/useAuth';
import { Link } from 'react-router-dom';
import { 
  LogOut, 
  Package, 
  FileText, 
  CreditCard,
  Wallet,
  TrendingUp,
  Clock,
  Plus,
  Search,
  Bell,
  Settings,
  Shield,
  ArrowUpRight,
  ArrowDownRight,
  Loader2,
  UserPlus,
  CheckCircle
} from 'lucide-react';
import toast from 'react-hot-toast';
import api from '../api/client';

export default function Dashboard() {
  const { user, logout } = useAuth();
  const [activities, setActivities] = useState([]);
  const [isLoadingActivities, setIsLoadingActivities] = useState(true);

  // Stats data
  const stats = [
    { 
      title: 'Total Loans', 
      value: '0', 
      change: '+0%', 
      positive: true,
      icon: Wallet,
      color: 'bg-blue-50 text-blue-600'
    },
    { 
      title: 'Active Loans', 
      value: '0', 
      change: 'Active', 
      positive: true,
      icon: TrendingUp,
      color: 'bg-green-50 text-green-600'
    },
    { 
      title: 'Pending Approvals', 
      value: '0', 
      change: 'Awaiting', 
      positive: false,
      icon: Clock,
      color: 'bg-yellow-50 text-yellow-600'
    },
    { 
      title: 'Total Borrowed', 
      value: 'P0.00', 
      change: '0 loans', 
      positive: true,
      icon: CreditCard,
      color: 'bg-purple-50 text-purple-600'
    },
  ];

  // Quick Actions
  const quickActions = [
    { 
      title: 'Apply for Loan', 
      description: 'Get funds fast', 
      icon: Wallet,
      color: 'from-blue-500 to-blue-600',
      href: '/loans/apply'
    },
    { 
      title: 'Add Collateral', 
      description: 'Use electronics', 
      icon: Package,
      color: 'from-green-500 to-green-600',
      href: '/collateral'
    },
    { 
      title: 'Make Payment', 
      description: 'Pay your loans', 
      icon: CreditCard,
      color: 'from-purple-500 to-purple-600',
      href: '/payments'
    },
    { 
      title: 'KYC Verification', 
      description: 'Get verified', 
      icon: Shield,
      color: 'from-orange-500 to-orange-600',
      href: '/kyc'
    },
  ];

  // Fetch activities
  useEffect(() => {
    const fetchActivities = async () => {
      try {
        const response = await api.get('/users/activities');
        setActivities(response.data || []);
      } catch (error) {
        console.error('Failed to fetch activities:', error);
      } finally {
        setIsLoadingActivities(false);
      }
    };
    fetchActivities();
  }, []);

  // Helper to get icon component
  const getActivityIcon = (iconName) => {
    const icons = {
      'user-plus': UserPlus,
      'file-text': FileText,
      'check-circle': CheckCircle,
      'credit-card': CreditCard,
    };
    const Icon = icons[iconName] || FileText;
    return <Icon size={18} className="text-blue-600" />;
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white border-b border-gray-200 sticky top-0 z-50 shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            {/* Logo */}
            <div className="flex items-center gap-2">
              <div className="w-10 h-10 bg-gradient-to-br from-blue-600 to-blue-700 rounded-xl flex items-center justify-center shadow-lg">
                <span className="text-white font-bold text-lg">ML</span>
              </div>
              <div>
                <span className="text-xl font-bold text-gray-800">MicroLend</span>
                <span className="ml-2 text-xs bg-blue-50 text-blue-600 px-2 py-0.5 rounded-full font-medium">Botswana</span>
              </div>
            </div>

            {/* Search */}
            <div className="hidden lg:flex items-center flex-1 max-w-md mx-8">
              <div className="relative w-full">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" size={18} />
                <input
                  type="text"
                  placeholder="Search loans, collateral..."
                  className="w-full pl-10 pr-4 py-2 bg-gray-50 border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent text-sm"
                />
              </div>
            </div>

            {/* Right Menu */}
            <div className="flex items-center gap-3">
              <button className="hidden sm:flex p-2 text-gray-400 hover:text-gray-600 hover:bg-gray-100 rounded-xl relative">
                <Bell size={20} />
                <span className="absolute top-1.5 right-1.5 w-2 h-2 bg-red-500 rounded-full ring-2 ring-white"></span>
              </button>
              <button className="hidden sm:flex p-2 text-gray-400 hover:text-gray-600 hover:bg-gray-100 rounded-xl">
                <Settings size={20} />
              </button>
              
              {/* User Profile */}
              <div className="flex items-center gap-3 pl-3 border-l border-gray-200">
                <div className="w-9 h-9 rounded-full bg-gradient-to-br from-blue-500 to-purple-500 flex items-center justify-center text-white font-semibold shadow-md text-sm">
                  {user?.firstName?.[0] || 'U'}
                </div>
                <div className="hidden md:block">
                  <p className="text-sm font-semibold text-gray-800 leading-none">
                    {user?.firstName || 'User'}
                  </p>
                  <p className="text-xs text-gray-500 mt-1">{user?.email}</p>
                </div>
                <button
                  onClick={logout}
                  className="p-2 text-gray-400 hover:text-red-600 hover:bg-red-50 rounded-xl"
                >
                  <LogOut size={18} />
                </button>
              </div>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Welcome Banner */}
        <div className="relative overflow-hidden bg-gradient-to-r from-blue-600 via-blue-700 to-blue-800 rounded-2xl p-6 md:p-8 mb-8 text-white shadow-xl">
          <div className="absolute inset-0 opacity-10">
            <div className="absolute top-0 -right-20 w-64 h-64 bg-white rounded-full"></div>
            <div className="absolute -bottom-20 -left-20 w-96 h-96 bg-white rounded-full"></div>
          </div>
          <div className="relative flex flex-col md:flex-row md:items-center md:justify-between">
            <div>
              <h1 className="text-2xl md:text-3xl font-bold mb-2">
                Welcome back, {user?.firstName || 'User'}! 👋
              </h1>
              <p className="text-blue-100 text-sm md:text-base">Here's what's happening with your finances today</p>
            </div>
            <div className="mt-4 md:mt-0">
              <Link
                to="/loans/apply"
                className="inline-flex items-center gap-2 px-6 py-3 bg-white text-blue-600 font-semibold rounded-xl hover:bg-blue-50 transition-all shadow-lg hover:shadow-xl"
              >
                <Plus size={20} />
                Apply for Loan
              </Link>
            </div>
          </div>
        </div>

        {/* Stats Grid */}
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 md:gap-6 mb-8">
          {stats.map((stat, index) => {
            const Icon = stat.icon;
            return (
              <div
                key={index}
                className="bg-white rounded-2xl shadow-sm hover:shadow-md transition-all p-5 border border-gray-100"
              >
                <div className="flex items-center justify-between mb-3">
                  <div className={`p-2.5 rounded-xl ${stat.color}`}>
                    <Icon size={20} />
                  </div>
                  <span className={`text-xs font-medium flex items-center gap-0.5 px-2 py-0.5 rounded-full ${
                    stat.positive ? 'bg-green-50 text-green-600' : 'bg-yellow-50 text-yellow-600'
                  }`}>
                    {stat.positive ? <ArrowUpRight size={12} /> : <ArrowDownRight size={12} />}
                    {stat.change}
                  </span>
                </div>
                <p className="text-2xl font-bold text-gray-800">{stat.value}</p>
                <p className="text-xs text-gray-500 mt-0.5 font-medium uppercase tracking-wide">{stat.title}</p>
              </div>
            );
          })}
        </div>

        {/* Quick Actions & Recent Activity */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Quick Actions */}
          <div className="lg:col-span-2">
            <div className="bg-white rounded-2xl shadow-sm border border-gray-100 p-6">
              <h3 className="text-base font-semibold text-gray-800 mb-5 flex items-center gap-2">
                <span className="w-1 h-5 bg-blue-600 rounded-full"></span>
                Quick Actions
              </h3>
              <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
                {quickActions.map((action, index) => {
                  const Icon = action.icon;
                  return (
                    <Link
                      key={index}
                      to={action.href}
                      className={`bg-gradient-to-br ${action.color} rounded-xl p-4 text-white hover:scale-105 transition-all duration-200 shadow-md hover:shadow-lg text-center`}
                    >
                      <Icon size={28} className="mx-auto mb-1.5" />
                      <h4 className="font-semibold text-xs leading-tight">{action.title}</h4>
                      <p className="text-[10px] opacity-80 mt-0.5">{action.description}</p>
                    </Link>
                  );
                })}
              </div>
            </div>
          </div>

          {/* Recent Activity */}
          <div className="lg:col-span-1">
            <div className="bg-white rounded-2xl shadow-sm border border-gray-100 p-6 h-full">
              <div className="flex items-center justify-between mb-5">
                <h3 className="text-base font-semibold text-gray-800 flex items-center gap-2">
                  <span className="w-1 h-5 bg-purple-600 rounded-full"></span>
                  Recent Activity
                </h3>
                {activities.length > 0 && (
                  <span className="text-xs text-blue-600 cursor-pointer hover:underline font-medium">
                    View All
                  </span>
                )}
              </div>
              
              {isLoadingActivities ? (
                <div className="flex justify-center py-8">
                  <Loader2 className="animate-spin text-blue-600" size={24} />
                </div>
              ) : activities.length === 0 ? (
                <div className="text-center py-8">
                  <Clock className="mx-auto text-gray-300" size={32} />
                  <p className="text-gray-500 text-sm mt-2">No activity yet</p>
                </div>
              ) : (
                <div className="space-y-4 max-h-[320px] overflow-y-auto pr-2">
                  {activities.slice(0, 5).map((activity, index) => {
                    const IconComponent = getActivityIcon(activity.icon);
                    const timeAgo = new Date(activity.timestamp);
                    const now = new Date();
                    const diffMs = now - timeAgo;
                    const diffMins = Math.floor(diffMs / 60000);
                    const diffHours = Math.floor(diffMs / 3600000);
                    const diffDays = Math.floor(diffMs / 86400000);
                    
                    let timeDisplay = '';
                    if (diffMins < 1) timeDisplay = 'Just now';
                    else if (diffMins < 60) timeDisplay = `${diffMins}m ago`;
                    else if (diffHours < 24) timeDisplay = `${diffHours}h ago`;
                    else if (diffDays < 7) timeDisplay = `${diffDays}d ago`;
                    else timeDisplay = timeAgo.toLocaleDateString('en-BW', { month: 'short', day: 'numeric' });
                    
                    return (
                      <div key={index} className="flex items-start gap-3 pb-4 border-b border-gray-100 last:border-0 last:pb-0">
                        <div className="w-8 h-8 rounded-full bg-blue-50 flex items-center justify-center flex-shrink-0">
                          {IconComponent}
                        </div>
                        <div className="flex-1 min-w-0">
                          <p className="text-sm font-medium text-gray-800 truncate">
                            {activity.title}
                          </p>
                          <p className="text-xs text-gray-500 truncate">{activity.description}</p>
                          <p className="text-[10px] text-gray-400 mt-0.5">{timeDisplay}</p>
                        </div>
                      </div>
                    );
                  })}
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Bottom Section */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mt-8">
          {/* Recent Loans */}
          <div className="bg-white rounded-2xl shadow-sm border border-gray-100 p-6">
            <div className="flex items-center justify-between mb-5">
              <h3 className="text-base font-semibold text-gray-800 flex items-center gap-2">
                <span className="w-1 h-5 bg-green-600 rounded-full"></span>
                Recent Loans
              </h3>
              <Link to="/loans" className="text-xs text-blue-600 hover:underline font-medium">View All</Link>
            </div>
            <div className="text-center py-8">
              <FileText className="mx-auto text-gray-300" size={28} />
              <p className="text-gray-500 mt-3 text-sm">No loans yet</p>
              <Link to="/loans/apply" className="text-sm text-blue-600 hover:underline mt-2 inline-block font-medium">
                Apply for your first loan →
              </Link>
            </div>
          </div>

          {/* Collateral */}
          <div className="bg-white rounded-2xl shadow-sm border border-gray-100 p-6">
            <div className="flex items-center justify-between mb-5">
              <h3 className="text-base font-semibold text-gray-800 flex items-center gap-2">
                <span className="w-1 h-5 bg-orange-600 rounded-full"></span>
                My Collateral
              </h3>
              <Link to="/collateral" className="text-xs text-blue-600 hover:underline font-medium">View All</Link>
            </div>
            <div className="text-center py-8">
              <Package className="mx-auto text-gray-300" size={28} />
              <p className="text-gray-500 mt-3 text-sm">No collateral items</p>
              <Link to="/loans/apply" className="text-sm text-blue-600 hover:underline mt-2 inline-block font-medium">
                Add your first item →
              </Link>
            </div>
          </div>
        </div>
      </main>

      {/* Footer */}
      <footer className="bg-white border-t border-gray-200 mt-12">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="flex flex-col md:flex-row justify-between items-center gap-4">
            <p className="text-xs text-gray-400">
              © 2024 MicroLend Botswana. All rights reserved.
            </p>
            <div className="flex items-center gap-6">
              <Link to="/privacy" className="text-xs text-gray-400 hover:text-gray-600">Privacy Policy</Link>
              <Link to="/terms" className="text-xs text-gray-400 hover:text-gray-600">Terms of Service</Link>
              <Link to="/help" className="text-xs text-gray-400 hover:text-gray-600">Help Center</Link>
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
}