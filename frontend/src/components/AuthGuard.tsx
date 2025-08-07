'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/contexts/AuthContext';

interface AuthGuardProps {
  children: React.ReactNode;
  requireAuth?: boolean;
  requireAdmin?: boolean;
  redirectTo?: string;
}

export default function AuthGuard({
  children,
  requireAuth = true,
  requireAdmin = false,
  redirectTo = '/login'
}: AuthGuardProps) {
  const { user, session, loading } = useAuth();
  const router = useRouter();
  const [isAuthorized, setIsAuthorized] = useState(false);
  const [userRole, setUserRole] = useState<string | null>(null);
  const [authError, setAuthError] = useState<string | null>(null);

  useEffect(() => {
    const checkAuthorization = async () => {
      console.log('🔒 AuthGuard: Checking authorization...');
      console.log('🔒 AuthGuard: Loading state:', loading);
      console.log('🔒 AuthGuard: User:', user?.email);
      console.log('🔒 AuthGuard: Session:', session ? 'Active' : 'None');
      console.log('🔒 AuthGuard: Require auth:', requireAuth);
      console.log('🔒 AuthGuard: Require admin:', requireAdmin);

      if (loading) {
        console.log('🔒 AuthGuard: Still loading, waiting...');
        return;
      }

      // If no auth required, allow access
      if (!requireAuth) {
        console.log('🔒 AuthGuard: No auth required, allowing access');
        setIsAuthorized(true);
        return;
      }

      // If auth required but no user, redirect to login
      if (!user || !session) {
        console.log('🔒 AuthGuard: No user or session, redirecting to login');
        setAuthError('Authentication required');
        router.push(redirectTo);
        return;
      }

      console.log('🔒 AuthGuard: User authenticated, checking admin role...');

      // If admin required, check user role
      if (requireAdmin) {
        console.log('🔒 AuthGuard: Checking admin role...');
        try {
          const { data: userData, error } = await fetch('/api/user/role', {
            method: 'GET',
            headers: {
              'Authorization': `Bearer ${session.access_token}`,
            },
          }).then(res => res.json());

          if (error || userData?.role !== 'admin') {
            console.log('🔒 AuthGuard: Admin access denied');
            setAuthError('Admin access required');
            router.push('/unauthorized');
            return;
          }

          setUserRole(userData.role);
          console.log('🔒 AuthGuard: Admin access granted');
        } catch (error) {
          console.error('🔒 AuthGuard: Error checking user role:', error);
          setAuthError('Role verification failed');
          router.push('/unauthorized');
          return;
        }
      }

      console.log('🔒 AuthGuard: Authorization successful');
      setIsAuthorized(true);
      setAuthError(null);
    };

    checkAuthorization();
  }, [user, session, loading, requireAuth, requireAdmin, router, redirectTo]);

  // Show loading spinner while checking auth
  if (loading || (!isAuthorized && requireAuth)) {
    return (
      <div className="min-h-screen bg-gray-900 flex items-center justify-center">
        <div className="text-center">
          <div className="w-16 h-16 border-4 border-emerald-500 border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
          <p className="text-gray-400">
            {loading ? 'Verifying authentication...' : 'Checking authorization...'}
          </p>
          {authError && (
            <p className="text-red-400 mt-2">{authError}</p>
          )}
        </div>
      </div>
    );
  }

  // Show unauthorized message for admin-only pages
  if (requireAdmin && userRole !== 'admin') {
    return (
      <div className="min-h-screen bg-gray-900 flex items-center justify-center">
        <div className="text-center">
          <div className="w-16 h-16 text-red-500 mx-auto mb-4">🚫</div>
          <h1 className="text-2xl font-bold text-white mb-2">Access Denied</h1>
          <p className="text-gray-400 mb-4">You don&apos;t have permission to access this page.</p>
          <button
            onClick={() => router.push('/')}
            className="bg-emerald-600 text-white px-6 py-2 rounded-lg hover:bg-emerald-700 transition-colors"
          >
            Go Home
          </button>
        </div>
      </div>
    );
  }

  return <>{children}</>;
}