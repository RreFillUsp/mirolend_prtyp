// frontend/src/App.jsx
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { Toaster } from 'react-hot-toast';
import Login from './pages/Login';
import Register from './pages/Register';
import Dashboard from './pages/Dashboard';
import { useAuth } from './hooks/useAuth';
import ApplyLoan from './pages/ApplyLoan';
import MyLoans from './pages/MyLoans';
import Collateral from './pages/Collateral';
import Payments from './pages/Payments';
import VerifyEmail from './pages/VerifyEmail';
import ResendVerification from './pages/ResendVerification';
import VerificationSent from './pages/VerificationSent';


function PrivateRoute({ children }) {
  const { isAuthenticated } = useAuth();
  return isAuthenticated ? children : <Navigate to="/login" />;
}

function PublicRoute({ children }) {
  const { isAuthenticated } = useAuth();
  return isAuthenticated ? <Navigate to="/dashboard" /> : children;
}

function App() {
  return (
    <BrowserRouter>
      <Toaster position="top-right" />
      <Routes>
        <Route path="/" element={<Navigate to="/login" />} />
        <Route
          path="/login"
          element={
            <PublicRoute>
              <Login />
            </PublicRoute>
          }
        />
        <Route
          path="/register"
          element={
            <PublicRoute>
              <Register />
            </PublicRoute>
          }
        />

        <Route
  path="/loans"
  element={
    <PrivateRoute>
      <MyLoans />
    </PrivateRoute>
  }
/>
          <Route
          path="/loans/apply"
          element={
            <PrivateRoute>
              <ApplyLoan />
            </PrivateRoute>
          }
        />

        Inside Routes:
<Route path="/verify-email" element={<VerifyEmail />} />
<Route path="/resend-verification" element={<ResendVerification />} />
<Route path="/verification-sent" element={<VerificationSent />} />

         <Route
         path="/collateral"
         element={
            <PrivateRoute>
                 <Collateral />
            </PrivateRoute>
  }
/>
<Route
  path="/payments"
  element={
    <PrivateRoute>
      <Payments />
    </PrivateRoute>
  }
/>

<Route
  path="/collateral/add"
  element={<Navigate to="/loans/apply" replace />}
/>
        <Route
          path="/dashboard"
          element={
            <PrivateRoute>
              <Dashboard />
            </PrivateRoute>
          }
        />
      </Routes>
    </BrowserRouter>
  );
}

export default App;