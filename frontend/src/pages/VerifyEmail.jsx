import { useState, useEffect } from 'react';
import { useSearchParams, Link } from 'react-router-dom';
import { CheckCircle, AlertCircle, Loader2 } from 'lucide-react';
import api from '../api/client';
import toast from 'react-hot-toast';

export default function VerifyEmail() {
  const [searchParams] = useSearchParams();
  const token = searchParams.get('token');
  const [status, setStatus] = useState('loading');
  const [message, setMessage] = useState('');

  useEffect(() => {
    if (!token) {
      setStatus('error');
      setMessage('No verification token provided.');
      return;
    }

    const verify = async () => {
      try {
        const response = await api.get(`/auth/verify-email?token=${token}`);
        setStatus('success');
        setMessage(response.data.message || 'Email verified successfully!');
        toast.success('Email verified! You can now login.');
      } catch (error) {
        setStatus('error');
        setMessage(error.response?.data?.detail || 'Verification failed. The token may be invalid or expired.');
        toast.error('Verification failed');
      }
    };

    verify();
  }, [token]);

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 p-4">
      <div className="max-w-md w-full bg-white rounded-2xl shadow-xl p-8 text-center">
        <div className="flex justify-center mb-4">
          {status === 'loading' && <Loader2 className="animate-spin text-blue-600" size={48} />}
          {status === 'success' && <CheckCircle className="text-green-500" size={48} />}
          {status === 'error' && <AlertCircle className="text-red-500" size={48} />}
        </div>
        <h2 className="text-2xl font-bold text-gray-800 mb-2">
          {status === 'loading' && 'Verifying...'}
          {status === 'success' && 'Verified!'}
          {status === 'error' && 'Verification Failed'}
        </h2>
        <p className="text-gray-600 mb-6">{message}</p>
        {status === 'success' && (
          <Link to="/login" className="inline-block px-6 py-2 bg-blue-600 text-white rounded-xl hover:bg-blue-700 transition-colors">
            Go to Login
          </Link>
        )}
        {status === 'error' && (
          <div className="space-y-3">
            <p className="text-sm text-gray-500">You can request a new verification link.</p>
            <Link to="/resend-verification" className="inline-block px-6 py-2 bg-blue-600 text-white rounded-xl hover:bg-blue-700 transition-colors">
              Resend Verification Email
            </Link>
          </div>
        )}
      </div>
    </div>
  );
}