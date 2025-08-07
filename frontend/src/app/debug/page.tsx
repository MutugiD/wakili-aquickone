'use client';

import { useEffect, useState } from 'react';
import { useAuth } from '@/contexts/AuthContext';
import { supabase } from '@/lib/supabase';

export default function DebugPage() {
  const { user, session, loading } = useAuth();
  const [authStatus, setAuthStatus] = useState<string>('Checking...');
  const [profileData, setProfileData] = useState<Record<string, unknown> | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const checkAuth = async () => {
      try {
        // Check Supabase session
        const { data: { session: currentSession } } = await supabase.auth.getSession();

        if (currentSession) {
          setAuthStatus('✅ Supabase session found');
          console.log('🔐 Supabase session:', currentSession);
          console.log('🔐 User:', currentSession.user);

          // Test backend profile endpoint
          try {
            const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/v1/auth/profile`, {
              headers: {
                'Authorization': `Bearer ${currentSession.access_token}`,
                'Content-Type': 'application/json',
              },
            });

            console.log('🔍 Profile endpoint response status:', response.status);

            if (response.ok) {
              const profile = await response.json();
              setProfileData(profile);
              setAuthStatus('✅ Backend profile endpoint working');
              console.log('✅ Profile data:', profile);
            } else {
              const errorText = await response.text();
              setError(`❌ Profile endpoint failed: ${response.status} - ${errorText}`);
              console.error('❌ Profile endpoint error:', errorText);
            }
          } catch (profileError) {
            setError(`❌ Profile endpoint error: ${profileError}`);
            console.error('❌ Profile endpoint error:', profileError);
          }
        } else {
          setAuthStatus('❌ No Supabase session found');
        }
      } catch (err) {
        setError(`❌ Auth check error: ${err}`);
        console.error('❌ Auth check error:', err);
      }
    };

    if (!loading) {
      checkAuth();
    }
  }, [loading]);

  return (
    <div className="min-h-screen bg-gray-900 text-white p-8">
      <div className="max-w-4xl mx-auto">
        <h1 className="text-3xl font-bold mb-8">🔍 Authentication Debug</h1>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* Auth Status */}
          <div className="bg-gray-800 p-6 rounded-lg">
            <h2 className="text-xl font-semibold mb-4">Authentication Status</h2>
            <div className="space-y-2">
              <p><strong>Loading:</strong> {loading ? 'Yes' : 'No'}</p>
              <p><strong>Auth Status:</strong> {authStatus}</p>
              <p><strong>User:</strong> {user?.email || 'None'}</p>
              <p><strong>User ID:</strong> {user?.id || 'None'}</p>
              <p><strong>Session:</strong> {session ? 'Active' : 'None'}</p>
            </div>
          </div>

          {/* Profile Data */}
          <div className="bg-gray-800 p-6 rounded-lg">
            <h2 className="text-xl font-semibold mb-4">Profile Data</h2>
            {profileData ? (
              <pre className="text-sm bg-gray-700 p-4 rounded overflow-auto">
                {JSON.stringify(profileData, null, 2)}
              </pre>
            ) : (
              <p className="text-gray-400">No profile data available</p>
            )}
          </div>

          {/* Error Display */}
          {error && (
            <div className="col-span-full bg-red-900 p-6 rounded-lg">
              <h2 className="text-xl font-semibold mb-4 text-red-300">Error</h2>
              <p className="text-red-200">{error}</p>
            </div>
          )}

          {/* Test Buttons */}
          <div className="col-span-full bg-gray-800 p-6 rounded-lg">
            <h2 className="text-xl font-semibold mb-4">Test Actions</h2>
            <div className="space-x-4">
              <button
                onClick={() => window.location.href = '/chat'}
                className="bg-blue-600 hover:bg-blue-700 px-4 py-2 rounded"
              >
                Test /chat Access
              </button>
              <button
                onClick={() => window.location.href = '/upload'}
                className="bg-green-600 hover:bg-green-700 px-4 py-2 rounded"
              >
                Test /upload Access
              </button>
              <button
                onClick={() => window.location.reload()}
                className="bg-gray-600 hover:bg-gray-700 px-4 py-2 rounded"
              >
                Refresh Page
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}