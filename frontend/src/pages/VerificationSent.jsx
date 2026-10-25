import { Link } from 'react-router-dom';
import { Mail } from 'lucide-react';

export default function VerificationSent() {
  const [searchParams] = useSearchParams();
  const email = searchParams.get('email') || 'your email';

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 p-4">
      <div className="max-w-md w-full bg-white rounded-2xl shadow-xl p-8 text-center">
        <Mail className="mx-auto text-blue-500" size={48} />
        <h2 className="text-2xl font-bold text-gray-800 mt-4">Verify Your Email</h2>
        <p className="text-gray-600 mt-2">
          We've sent a verification link to <strong>{email}</strong>.
          Please check your inbox and click the link to activate your account.
        </p>
        <p className="text-sm text-gray-500 mt-4">The link expires in 24 hours.</p>
        <div className="mt-6 space-y-3">
          <Link to="/login" className="inline-block px-6 py-2 bg-blue-600 text-white rounded-xl hover:bg-blue-700 transition-colors">
            Go to Login
          </Link>
          <p className="text-xs text-gray-400">
            Didn't receive the email? <Link to="/resend-verification" className="text-blue-600 hover:underline">Resend</Link>
          </p>
        </div>
      </div>
    </div>
  );
}