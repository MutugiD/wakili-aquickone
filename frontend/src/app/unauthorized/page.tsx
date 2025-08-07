'use client';

import Link from 'next/link';
import { Shield, Home, ArrowLeft } from 'lucide-react';

export default function UnauthorizedPage() {
  return (
    <div className="min-h-screen bg-gray-900 flex items-center justify-center">
      <div className="max-w-md w-full mx-auto px-6 text-center">
        <div className="bg-gray-800 rounded-2xl p-8 shadow-xl border border-gray-700">
          <div className="w-16 h-16 bg-red-500/20 rounded-full flex items-center justify-center mx-auto mb-6">
            <Shield className="w-8 h-8 text-red-400" />
          </div>

          <h1 className="text-2xl font-bold text-white mb-4">Access Denied</h1>
          <p className="text-gray-400 mb-6">
            You don&apos;t have permission to access this page. This area requires administrator privileges.
          </p>

          <div className="space-y-4">
            <Link
              href="/"
              className="w-full bg-emerald-600 text-white py-3 px-6 rounded-lg font-semibold hover:bg-emerald-700 transition-colors flex items-center justify-center"
            >
              <Home className="w-4 h-4 mr-2" />
              Go Home
            </Link>

            <button
              onClick={() => window.history.back()}
              className="w-full bg-gray-700 text-white py-3 px-6 rounded-lg font-semibold hover:bg-gray-600 transition-colors flex items-center justify-center"
            >
              <ArrowLeft className="w-4 h-4 mr-2" />
              Go Back
            </button>
          </div>

          <div className="mt-6 pt-6 border-t border-gray-700">
            <p className="text-sm text-gray-500">
              Need access? Contact your administrator or{' '}
              <Link href="/demo" className="text-emerald-400 hover:text-emerald-300">
                request a demo
              </Link>
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}