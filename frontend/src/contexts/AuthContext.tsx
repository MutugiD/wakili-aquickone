'use client';

import { createContext, useContext, useEffect, useState, useCallback } from 'react';
import { User, Session, AuthError } from '@supabase/supabase-js';
import { createClient } from '@/lib/supabase/client';

interface AuthContextType {
  user: User | null;
  session: Session | null;
  loading: boolean;
  signUp: (email: string, password: string, fullName: string, company: string) => Promise<{ error: AuthError | null }>;
  signIn: (email: string, password: string) => Promise<{ error: AuthError | null }>;
  signOut: () => Promise<void>;
  resetPassword: (email: string) => Promise<{ error: AuthError | null }>;
  updatePassword: (password: string) => Promise<{ error: AuthError | null }>;
  requestDemo: () => Promise<{ error: AuthError | null }>;
  updateProfile: (updates: { full_name?: string; company?: string }) => Promise<{ error: AuthError | null }>;
  refreshSession: () => Promise<void>;
  checkAuthStatus: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [session, setSession] = useState<Session | null>(null);
  const [loading, setLoading] = useState(true);
  const supabase = createClient();

  const checkAuthStatus = useCallback(async () => {
    try {
      console.log('🔐 Checking auth status...');
      const { data: { session: currentSession }, error } = await supabase.auth.getSession();

      if (error) {
        console.error('❌ Error getting session:', error);
        setSession(null);
        setUser(null);
        setLoading(false);
        return;
      }

      console.log('🔐 Current session:', currentSession ? 'Found' : 'None');
      console.log('🔐 Session user:', currentSession?.user?.email);

      setSession(currentSession);
      setUser(currentSession?.user ?? null);
      setLoading(false);
    } catch (error) {
      console.error('❌ Error in checkAuthStatus:', error);
      setSession(null);
      setUser(null);
      setLoading(false);
    }
  }, [supabase.auth]);

  useEffect(() => {
    console.log('🔐 AuthProvider mounted, checking initial session...');

    // Get initial session
    checkAuthStatus();

    // Listen for auth changes
    const {
      data: { subscription },
    } = supabase.auth.onAuthStateChange(async (event, session) => {
      console.log('🔐 Auth state change:', event, session ? 'Session found' : 'No session');
      console.log('🔐 Session user:', session?.user?.email);

      setSession(session);
      setUser(session?.user ?? null);
      setLoading(false);
    });

    return () => subscription.unsubscribe();
  }, [supabase.auth, checkAuthStatus]);

  const signUp = async (email: string, password: string, fullName: string, company: string) => {
    console.log('🔐 Signing up user:', email);
    const { error } = await supabase.auth.signUp({
      email,
      password,
      options: {
        data: {
          full_name: fullName,
          company: company,
        },
        emailRedirectTo: `${window.location.origin}/auth/callback`,
      },
    });

    if (error) {
      console.error('❌ Sign up error:', error);
    } else {
      console.log('✅ Sign up successful');
    }

    return { error };
  };

  const signIn = async (email: string, password: string) => {
    console.log('🔐 Signing in user:', email);
    const { error } = await supabase.auth.signInWithPassword({
      email,
      password,
    });

    if (error) {
      console.error('❌ Sign in error:', error);
    } else {
      console.log('✅ Sign in successful');
    }

    return { error };
  };

  const signOut = async () => {
    console.log('🔐 Signing out user');
    await supabase.auth.signOut();
    console.log('✅ Sign out successful');
  };

  const resetPassword = async (email: string) => {
    const { error } = await supabase.auth.resetPasswordForEmail(email, {
      redirectTo: `${window.location.origin}/auth/reset-password`,
    });

    return { error };
  };

  const updatePassword = async (password: string) => {
    const { error } = await supabase.auth.updateUser({
      password: password,
    });

    return { error };
  };

  // ✅ SECURE: Backend API call instead of direct database access
  const updateProfile = async (updates: { full_name?: string; company?: string }) => {
    if (!session?.access_token) {
      console.error('❌ No session available for profile update');
      return { error: new Error('No session available') as AuthError };
    }

    try {
      console.log('🔐 Updating profile with token:', session.access_token.substring(0, 20) + '...');
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/v1/auth/profile`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${session.access_token}`,
        },
        body: JSON.stringify(updates),
      });

      console.log('🔐 Profile update response status:', response.status);

      if (!response.ok) {
        const errorData = await response.json();
        console.error('❌ Profile update failed:', errorData);
        return { error: new Error(errorData.detail || 'Failed to update profile') as AuthError };
      }

      console.log('✅ Profile update successful');
      return { error: null };
    } catch (error) {
      console.error('❌ Profile update error:', error);
      return { error: error as AuthError };
    }
  };

  // ✅ SECURE: Backend API call instead of direct database access
  const requestDemo = async () => {
    if (!session?.access_token) {
      return { error: new Error('No session available') as AuthError };
    }

    try {
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/v1/auth/request-demo`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${session.access_token}`,
        },
      });

      if (!response.ok) {
        const errorData = await response.json();
        return { error: new Error(errorData.detail || 'Failed to request demo') as AuthError };
      }

      return { error: null };
    } catch (error) {
      return { error: error as AuthError };
    }
  };

  const refreshSession = async () => {
    console.log('🔐 Refreshing session...');
    const { data, error } = await supabase.auth.refreshSession();
    if (error) {
      console.error('❌ Error refreshing session:', error);
      return;
    }
    setSession(data.session);
    setUser(data.session?.user ?? null);
    console.log('✅ Session refreshed successfully');
  };

  const value = {
    user,
    session,
    loading,
    signUp,
    signIn,
    signOut,
    resetPassword,
    updatePassword,
    updateProfile,
    requestDemo,
    refreshSession,
    checkAuthStatus,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}