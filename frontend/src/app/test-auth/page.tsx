'use client';

import { useState } from 'react';
import { useAuth } from '@/contexts/AuthContext';
import { useRouter } from 'next/navigation';

export default function TestAuthPage() {
  const { signIn, user, session, loading } = useAuth();
  const router = useRouter();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [isSigningIn, setIsSigningIn] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSignIn = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSigningIn(true);
    setError(null);

    try {
      const { error } = await signIn(email, password);
      if (error) {
        setError(error.message);
      } else {
        console.log('✅ Sign in successful, redirecting...');
        // Wait a moment for the session to be set
        setTimeout(() => {
          router.push('/chat');
        }, 1000);
      }
    } catch (err) {
      setError('An unexpected error occurred');
      console.error('Sign in error:', err);
    } finally {
      setIsSigningIn(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-900 flex items-center justify-center p-4">
      <div className="max-w-md w-full bg-gray-800 rounded-lg p-8">
        <h1 className="text-2xl font-bold text-white mb-6 text-center">Test Authentication</h1>

        {/* Current Status */}
        <div className="mb-6 p-4 bg-gray-700 rounded">
          <h2 className="text-lg font-semibold text-white mb-2">Current Status</h2>
          <div className="space-y-1 text-sm">
            <p><span className="text-gray-400">Loading:</span> <span className={loading ? 'text-yellow-400' : 'text-green-400'}>{loading ? 'Yes' : 'No'}</span></p>
            <p><span className="text-gray-400">User:</span> <span className={user ? 'text-green-400' : 'text-red-400'}>{user?.email || 'None'}</span></p>
            <p><span className="text-gray-400">Session:</span> <span className={session ? 'text-green-400' : 'text-red-400'}>{session ? 'Active' : 'None'}</span></p>
          </div>
        </div>

        {/* Login Form */}
        <form onSubmit={handleSignIn} className="space-y-4">
          <div>
            <label htmlFor="email" className="block text-sm font-medium text-gray-300 mb-1">
              Email
            </label>
            <input
              type="email"
              id="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-md text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="Enter your email"
              required
            />
          </div>

          <div>
            <label htmlFor="password" className="block text-sm font-medium text-gray-300 mb-1">
              Password
            </label>
            <input
              type="password"
              id="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-md text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="Enter your password"
              required
            />
          </div>

          {error && (
            <div className="p-3 bg-red-900 border border-red-700 rounded-md">
              <p className="text-red-200 text-sm">{error}</p>
            </div>
          )}

          <button
            type="submit"
            disabled={isSigningIn || loading}
            className="w-full bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            {isSigningIn ? 'Signing In...' : 'Sign In'}
          </button>
        </form>

        {/* Test Buttons */}
        <div className="mt-6 space-y-2">
          <button
            onClick={() => router.push('/debug')}
            className="w-full bg-gray-600 text-white py-2 px-4 rounded-md hover:bg-gray-700 transition-colors"
          >
            Go to Debug Page
          </button>

          <button
            onClick={() => router.push('/chat')}
            className="w-full bg-green-600 text-white py-2 px-4 rounded-md hover:bg-green-700 transition-colors"
          >
            Test /chat Access
          </button>

          <button
            onClick={() => router.push('/upload')}
            className="w-full bg-purple-600 text-white py-2 px-4 rounded-md hover:bg-purple-700 transition-colors"
          >
            Test /upload Access
          </button>
        </div>

        {/* Quick Login Buttons */}
        <div className="mt-6 pt-6 border-t border-gray-700">
          <h3 className="text-sm font-medium text-gray-300 mb-3">Quick Test Logins</h3>
          <div className="space-y-2">
            <button
              onClick={() => {
                setEmail('dennismutugi@gmail.com');
                setPassword('test123');
              }}
              className="w-full bg-gray-600 text-white py-1 px-3 rounded text-sm hover:bg-gray-700 transition-colors"
            >
              Set Test Credentials
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}