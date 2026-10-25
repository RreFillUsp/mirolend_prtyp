// frontend/src/pages/ApplyLoan.jsx
import { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth';
import { 
  ArrowLeft, 
  Wallet, 
  Calendar, 
  Percent, 
  TrendingUp,
  Loader2,
  Upload,
  X,
  Package,
  Camera
} from 'lucide-react';
import toast from 'react-hot-toast';
import api from '../api/client';

export default function ApplyLoan() {
  const { user } = useAuth();
  const navigate = useNavigate();
  const [isLoading, setIsLoading] = useState(false);
  const [formData, setFormData] = useState({
    amount: '',
    term_months: 6,
    // Collateral fields
    collateral_type: '',
    collateral_brand: '',
    collateral_model: '',
    collateral_estimated_value: '',
    collateral_condition: 'good',
    collateral_description: '',
    collateral_photos: [],
  });
  const [loanSummary, setLoanSummary] = useState(null);
  const [photoPreviews, setPhotoPreviews] = useState([]);

  // Calculate loan summary with 20% per month interest
  useEffect(() => {
    if (formData.amount && formData.term_months) {
      const amount = parseFloat(formData.amount);
      const term = parseInt(formData.term_months);
      if (amount > 0 && term > 0) {
        const monthlyRate = 0.20; // 20% per month
        const totalInterest = amount * monthlyRate * term;
        const totalPayment = amount + totalInterest;
        const monthlyPayment = totalPayment / term;
        
        setLoanSummary({
          amount: amount,
          monthlyPayment: monthlyPayment,
          totalPayment: totalPayment,
          totalInterest: totalInterest,
          term: term,
          monthlyRate: monthlyRate * 100,
        });
      } else {
        setLoanSummary(null);
      }
    } else {
      setLoanSummary(null);
    }
  }, [formData.amount, formData.term_months]);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData({ ...formData, [name]: value });
  };

  const handlePhotoUpload = (e) => {
    const files = Array.from(e.target.files);
    if (files.length + photoPreviews.length > 2) {
      toast.error('You can upload a maximum of 2 photos');
      return;
    }
    
    // Create previews
    const newPreviews = files.map(file => URL.createObjectURL(file));
    setPhotoPreviews([...photoPreviews, ...newPreviews]);
    setFormData({ ...formData, collateral_photos: [...formData.collateral_photos, ...files] });
  };

  const removePhoto = (index) => {
    const newPreviews = [...photoPreviews];
    const newFiles = [...formData.collateral_photos];
    URL.revokeObjectURL(newPreviews[index]);
    newPreviews.splice(index, 1);
    newFiles.splice(index, 1);
    setPhotoPreviews(newPreviews);
    setFormData({ ...formData, collateral_photos: newFiles });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    // Validate loan fields
    if (!formData.amount || parseFloat(formData.amount) < 100) {
      toast.error('Minimum loan amount is P100');
      return;
    }
    if (parseFloat(formData.amount) > 50000) {
      toast.error('Maximum loan amount is P50,000');
      return;
    }
    if (!formData.term_months) {
      toast.error('Please select a repayment period');
      return;
    }
    
    // Validate collateral
    if (!formData.collateral_type) {
      toast.error('Please select a collateral type');
      return;
    }
    if (formData.collateral_type === 'other' && !formData.collateral_description) {
      toast.error('Please describe the other item');
      return;
    }
    if (!formData.collateral_brand) {
      toast.error('Please enter the brand');
      return;
    }
    if (!formData.collateral_model) {
      toast.error('Please enter the model');
      return;
    }
    if (!formData.collateral_estimated_value || parseFloat(formData.collateral_estimated_value) < 100) {
      toast.error('Estimated value must be at least P100');
      return;
    }
    if (formData.collateral_photos.length < 2) {
      toast.error('Please upload at least 2 photos of the item');
      return;
    }

    setIsLoading(true);
    try {
      // Step 1: Create collateral with photos
      const collateralFormData = new FormData();
      collateralFormData.append('item_type', formData.collateral_type === 'other' ? 'other' : formData.collateral_type);
      collateralFormData.append('brand', formData.collateral_brand);
      collateralFormData.append('model', formData.collateral_model);
      collateralFormData.append('estimated_value', formData.collateral_estimated_value);
      collateralFormData.append('condition', formData.collateral_condition);
      collateralFormData.append('description', formData.collateral_description || '');
      
      // Append photos
      formData.collateral_photos.forEach((file) => {
        collateralFormData.append('photos', file);
      });

      console.log('📤 Creating collateral...');
      const collateralResponse = await api.post('/collateral', collateralFormData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      });
      
      const collateralId = collateralResponse.data.id;
      console.log('✅ Collateral created:', collateralId);

      // Step 2: Create loan application
      const loanData = {
        amount: parseFloat(formData.amount),
        term_months: parseInt(formData.term_months),
        collateral_id: collateralId,
      };

      console.log('📝 Submitting loan application:', loanData);
      const loanResponse = await api.post('/loans/applications', loanData);
      
      console.log('✅ Loan application submitted:', loanResponse.data);
      
      toast.success('Loan application submitted successfully! 🎉');
      
      setTimeout(() => {
        navigate('/loans');
      }, 1500);
      
    } catch (error) {
      console.error('❌ Error:', error);
      let message = 'Failed to submit application';
      if (error.response?.data?.detail) {
        message = error.response.data.detail;
      }
      toast.error(message);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white border-b border-gray-200 sticky top-0 z-50 shadow-sm">
        <div className="max-w-3xl mx-auto px-4 sm:px-6 lg:px-8">
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
                <span className="ml-2 text-xs bg-blue-50 text-blue-600 px-2 py-0.5 rounded-full font-medium">Apply Loan</span>
              </div>
            </div>
          </div>
        </div>
      </header>

      <main className="max-w-3xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-800">Apply for a Loan</h1>
          <p className="text-gray-500 mt-1">Get funds by using your electronics as collateral</p>
          <div className="mt-2 inline-flex items-center gap-2 bg-yellow-50 text-yellow-700 px-3 py-1 rounded-full text-sm">
            <Percent size={16} />
            Interest Rate: 20% per month
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Form */}
          <div className="lg:col-span-2">
            <form onSubmit={handleSubmit} className="bg-white rounded-2xl shadow-sm border border-gray-100 p-6 space-y-6">
              {/* Loan Amount */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Loan Amount <span className="text-red-500">*</span>
                </label>
                <div className="relative">
                  <span className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-500 font-semibold">P</span>
                  <input
                    type="number"
                    name="amount"
                    value={formData.amount}
                    onChange={handleChange}
                    placeholder="Enter amount (Min: P100, Max: P50,000)"
                    className="w-full pl-8 pr-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-white"
                    min="100"
                    max="50000"
                    required
                  />
                </div>
                <div className="flex justify-between text-xs text-gray-400 mt-1">
                  <span>Min: P100</span>
                  <span>Max: P50,000</span>
                </div>
              </div>

              {/* Repayment Period */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Repayment Period <span className="text-red-500">*</span>
                </label>
                <select
                  name="term_months"
                  value={formData.term_months}
                  onChange={handleChange}
                  className="w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-white"
                  required
                >
                  <option value="">Select period</option>
                  <option value="1">1 Month</option>
                  <option value="2">2 Months</option>
                  <option value="3">3 Months</option>
                  <option value="6">6 Months</option>
                  <option value="12">12 Months</option>
                </select>
              </div>

              {/* Collateral Section */}
              <div className="border-t pt-6">
                <h3 className="text-lg font-semibold text-gray-800 mb-4 flex items-center gap-2">
                  <Package size={20} className="text-blue-600" />
                  Collateral Details
                </h3>

                {/* Item Type */}
                <div className="mb-4">
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Item Type <span className="text-red-500">*</span>
                  </label>
                  <select
                    name="collateral_type"
                    value={formData.collateral_type}
                    onChange={handleChange}
                    className="w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-white"
                    required
                  >
                    <option value="">Select item type</option>
                    <option value="laptop">Laptop</option>
                    <option value="tablet">Tablet</option>
                    <option value="mobile">Mobile Device</option>
                    <option value="other">Other</option>
                  </select>
                </div>

                {/* Other Description */}
                {formData.collateral_type === 'other' && (
                  <div className="mb-4">
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Describe the item <span className="text-red-500">*</span>
                    </label>
                    <input
                      type="text"
                      name="collateral_description"
                      value={formData.collateral_description}
                      onChange={handleChange}
                      placeholder="e.g., Smart Watch, Drone, etc."
                      className="w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-white"
                      required
                    />
                  </div>
                )}

                {/* Brand & Model */}
                <div className="grid grid-cols-2 gap-4 mb-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Brand <span className="text-red-500">*</span>
                    </label>
                    <input
                      type="text"
                      name="collateral_brand"
                      value={formData.collateral_brand}
                      onChange={handleChange}
                      placeholder="e.g., Samsung"
                      className="w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-white"
                      required
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Model <span className="text-red-500">*</span>
                    </label>
                    <input
                      type="text"
                      name="collateral_model"
                      value={formData.collateral_model}
                      onChange={handleChange}
                      placeholder="e.g., Galaxy S23"
                      className="w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-white"
                      required
                    />
                  </div>
                </div>

                {/* Estimated Value */}
                <div className="mb-4">
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Estimated Value (Pula) <span className="text-red-500">*</span>
                  </label>
                  <input
                    type="number"
                    name="collateral_estimated_value"
                    value={formData.collateral_estimated_value}
                    onChange={handleChange}
                    placeholder="e.g., 8000"
                    className="w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-white"
                    min="100"
                    required
                  />
                </div>

                {/* Condition */}
                <div className="mb-4">
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Condition <span className="text-red-500">*</span>
                  </label>
                  <select
                    name="collateral_condition"
                    value={formData.collateral_condition}
                    onChange={handleChange}
                    className="w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-white"
                  >
                    <option value="new">New</option>
                    <option value="excellent">Excellent</option>
                    <option value="good">Good</option>
                    <option value="fair">Fair</option>
                    <option value="poor">Poor</option>
                  </select>
                </div>

                {/* Photos Upload */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Photos (2 photos required) <span className="text-red-500">*</span>
                  </label>
                  <div className="flex flex-wrap gap-4">
                    {photoPreviews.map((preview, index) => (
                      <div key={index} className="relative w-24 h-24 rounded-xl overflow-hidden border border-gray-200">
                        <img src={preview} alt={`Collateral ${index+1}`} className="w-full h-full object-cover" />
                        <button
                          type="button"
                          onClick={() => removePhoto(index)}
                          className="absolute top-1 right-1 bg-red-500 text-white rounded-full p-0.5 hover:bg-red-600"
                        >
                          <X size={14} />
                        </button>
                      </div>
                    ))}
                    {photoPreviews.length < 2 && (
                      <label className="w-24 h-24 border-2 border-dashed border-gray-300 rounded-xl flex flex-col items-center justify-center cursor-pointer hover:border-blue-500 transition-colors">
                        <Camera size={24} className="text-gray-400" />
                        <span className="text-xs text-gray-500 mt-1">Upload</span>
                        <input
                          type="file"
                          accept="image/*"
                          onChange={handlePhotoUpload}
                          className="hidden"
                          multiple
                        />
                      </label>
                    )}
                  </div>
                  <p className="text-xs text-gray-400 mt-2">
                    Upload at least 2 photos (JPG, PNG). Max 5MB each.
                  </p>
                </div>
              </div>

              {/* Submit */}
              <button
                type="submit"
                disabled={isLoading}
                className="w-full bg-gradient-to-r from-blue-600 to-blue-700 text-white py-3 rounded-xl hover:from-blue-700 hover:to-blue-800 transition-all duration-200 disabled:opacity-50 flex items-center justify-center font-semibold shadow-lg"
              >
                {isLoading ? (
                  <>
                    <Loader2 className="animate-spin mr-2" size={20} />
                    Submitting...
                  </>
                ) : (
                  'Submit Application'
                )}
              </button>
            </form>
          </div>

          {/* Loan Summary */}
          <div className="lg:col-span-1">
            <div className="bg-white rounded-2xl shadow-sm border border-gray-100 p-6 sticky top-24">
              <h3 className="text-lg font-semibold text-gray-800 mb-4 flex items-center gap-2">
                <TrendingUp size={20} className="text-blue-600" />
                Loan Summary
              </h3>
              
              {loanSummary ? (
                <div className="space-y-4">
                  <div className="p-4 bg-blue-50 rounded-xl">
                    <p className="text-sm text-gray-600">Monthly Payment</p>
                    <p className="text-2xl font-bold text-blue-600">
                      P{loanSummary.monthlyPayment.toFixed(2)}
                    </p>
                  </div>
                  
                  <div className="grid grid-cols-2 gap-3">
                    <div className="p-3 bg-gray-50 rounded-xl">
                      <p className="text-xs text-gray-500">Total Amount</p>
                      <p className="text-lg font-semibold text-gray-800">
                        P{loanSummary.totalPayment.toFixed(2)}
                      </p>
                    </div>
                    <div className="p-3 bg-gray-50 rounded-xl">
                      <p className="text-xs text-gray-500">Interest</p>
                      <p className="text-lg font-semibold text-orange-600">
                        P{loanSummary.totalInterest.toFixed(2)}
                      </p>
                    </div>
                  </div>
                  
                  <div className="p-3 bg-gray-50 rounded-xl">
                    <div className="flex justify-between text-sm">
                      <span className="text-gray-600">Interest Rate</span>
                      <span className="font-medium text-red-600">{loanSummary.monthlyRate.toFixed(0)}% Per Month</span>
                    </div>
                    <div className="flex justify-between text-sm mt-1">
                      <span className="text-gray-600">Term</span>
                      <span className="font-medium">{loanSummary.term} Months</span>
                    </div>
                    <div className="flex justify-between text-sm mt-1">
                      <span className="text-gray-600">Principal</span>
                      <span className="font-medium">P{loanSummary.amount.toFixed(2)}</span>
                    </div>
                  </div>
                </div>
              ) : (
                <div className="text-center py-8">
                  <Wallet className="mx-auto text-gray-300" size={48} />
                  <p className="text-gray-500 text-sm mt-3">
                    Enter loan amount and term to see summary
                  </p>
                </div>
              )}
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}