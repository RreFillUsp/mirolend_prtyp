// frontend/src/hooks/useAuth.js
import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import toast from 'react-hot-toast';
import api from '../api/client';

export function useAuth() {
  const [isLoading, setIsLoading] = useState(false);
  const [user, setUser] = useState(() => {
    const saved = localStorage.getItem('user');
    return saved ? JSON.parse(saved) : null;
  });
  const navigate = useNavigate();

  const login = async (email, password) => {
  setIsLoading(true);
  try {
    console.log('📝 Login attempt:', email);
    
    const response = await api.post('/auth/login', { email, password });
    const data = response.data;
    
    console.log('✅ Login successful:', data);
    
    // Store both token and user
    localStorage.setItem('access_token', data.access_token);
    localStorage.setItem('user', JSON.stringify(data.user));
    setUser(data.user);
    
    toast.success('Welcome back!');
    navigate('/dashboard');
    return { success: true };
  } catch (error) {
    console.error('❌ Login error:', error);
    const message = error.response?.data?.detail || 'Invalid credentials';
    toast.error(message);
    return { success: false, error: message };
  } finally {
    setIsLoading(false);
  }
};

  

  const register = async (userData) => {
  setIsLoading(true);
  try {
    const response = await api.post('/auth/register', {
      email: userData.email,
      phone: userData.phone,
      password: userData.password,
      first_name: userData.firstName,
      last_name: userData.lastName,
    });
    
    const data = response.data;
    if (data.requires_verification) {
      toast.success('Registration successful! Please verify your email.');
      // Redirect to verification sent page
      navigate(`/verification-sent?email=${encodeURIComponent(userData.email)}`);
      return { success: true, requiresVerification: true };
    } else {
      toast.success('Account created! Please login.');
      navigate('/login');
      return { success: true };
    }
  } catch (error) {

      console.error('❌ Registration error:', error);
      
      let message = 'Registration failed';
      if (error.response?.data?.detail) {
        message = error.response.data.detail;
      }
      
      toast.error(message);
      return { success: false, error: message };
    } finally {
      setIsLoading(false);
    }
  };

  const logout = () => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('user');
    setUser(null);
    toast.success('Logged out');
    navigate('/login');
  };

  return {
    user,
    isLoading,
    login,
    register,
    logout,
    isAuthenticated: !!user,
  };
}