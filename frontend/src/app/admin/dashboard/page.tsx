'use client';

import Link from "next/link";
import { motion } from "framer-motion";
import { useState, useEffect } from "react";
import {
  Database,
  Users,
  FileText,
  Settings,
  LogOut,
  Activity,
  Shield,
  Globe,
  Cpu,
  Zap
} from "lucide-react";
import WakiliLogo from "../../../components/WakiliLogo";

export default function AdminDashboard() {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [userInfo, setUserInfo] = useState<{ user: string } | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const token = localStorage.getItem('adminToken');
    if (!token) {
      window.location.href = '/admin';
      return;
    }

    // Verify token with backend
    verifyToken(token);
  }, []);

  const verifyToken = async (token: string) => {
    try {
      const response = await fetch('http://localhost:8000/api/v1/auth/verify', {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      if (response.ok) {
        const data = await response.json();
        setUserInfo(data);
        setIsAuthenticated(true);
      } else {
        localStorage.removeItem('adminToken');
        window.location.href = '/admin';
      }
    } catch {
      localStorage.removeItem('adminToken');
      window.location.href = '/admin';
    } finally {
      setIsLoading(false);
    }
  };

  const handleLogout = () => {
    localStorage.removeItem('adminToken');
    window.location.href = '/admin';
  };

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gray-900 flex items-center justify-center">
        <div className="text-center">
          <div className="w-8 h-8 border-2 border-emerald-500 border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
          <p className="text-gray-400">Verifying access...</p>
        </div>
      </div>
    );
  }

  if (!isAuthenticated) {
    return null;
  }

  const adminFeatures = [
    {
      title: "API Management",
      description: "Monitor and manage API endpoints",
      icon: <Database className="w-6 h-6" />,
      href: "/admin/api",
      color: "emerald"
    },
    {
      title: "User Management",
      description: "Manage user accounts and permissions",
      icon: <Users className="w-6 h-6" />,
      href: "/admin/users",
      color: "blue"
    },
    {
      title: "Document Processing",
      description: "Monitor document processing status",
      icon: <FileText className="w-6 h-6" />,
      href: "/admin/documents",
      color: "purple"
    },
    {
      title: "System Settings",
      description: "Configure system parameters",
      icon: <Settings className="w-6 h-6" />,
      href: "/admin/settings",
      color: "gray"
    },
    {
      title: "Analytics",
      description: "View system analytics and metrics",
      icon: <Activity className="w-6 h-6" />,
      href: "/admin/analytics",
      color: "orange"
    },
    {
      title: "Security",
      description: "Security settings and logs",
      icon: <Shield className="w-6 h-6" />,
      href: "/admin/security",
      color: "red"
    }
  ];

  const systemStatus = [
    { name: "Backend API", status: "Online", color: "green" },
    { name: "Database", status: "Online", color: "green" },
    { name: "File Storage", status: "Online", color: "green" },
    { name: "AI Services", status: "Online", color: "green" }
  ];

  return (
    <div className="min-h-screen bg-gray-900">
      {/* Header */}
      <header className="bg-gray-800 border-b border-gray-700">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-4">
            <div className="flex items-center space-x-4">
              <Link href="/">
                <WakiliLogo size="md" />
              </Link>
              <div className="text-white">
                <h1 className="text-lg font-semibold">Admin Dashboard</h1>
                <p className="text-sm text-gray-400">Welcome back, {userInfo?.user || 'Admin'}</p>
              </div>
            </div>
            <button
              onClick={handleLogout}
              className="flex items-center space-x-2 text-gray-400 hover:text-white transition-colors"
            >
              <LogOut className="w-4 h-4" />
              <span>Logout</span>
            </button>
          </div>
        </div>
      </header>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* System Status */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
          className="mb-8"
        >
          <h2 className="text-2xl font-bold text-white mb-6">System Status</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            {systemStatus.map((service) => (
              <div key={service.name} className="bg-gray-800 rounded-lg p-4 border border-gray-700">
                <div className="flex items-center justify-between">
                  <span className="text-gray-300">{service.name}</span>
                  <div className="flex items-center space-x-2">
                    <div className={`w-2 h-2 rounded-full bg-${service.color}-500`}></div>
                    <span className={`text-sm text-${service.color}-400`}>{service.status}</span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </motion.div>

        {/* Admin Features */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.2 }}
        >
          <h2 className="text-2xl font-bold text-white mb-6">Admin Features</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {adminFeatures.map((feature) => (
              <Link
                key={feature.title}
                href={feature.href}
                className="bg-gray-800 rounded-lg p-6 border border-gray-700 hover:border-gray-600 transition-all duration-200 hover:shadow-lg"
              >
                <div className={`w-12 h-12 bg-${feature.color}-500/20 rounded-lg flex items-center justify-center mb-4`}>
                  <div className={`text-${feature.color}-400`}>
                    {feature.icon}
                  </div>
                </div>
                <h3 className="text-lg font-semibold text-white mb-2">{feature.title}</h3>
                <p className="text-gray-400 text-sm">{feature.description}</p>
              </Link>
            ))}
          </div>
        </motion.div>

        {/* Quick Actions */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.4 }}
          className="mt-8"
        >
          <h2 className="text-2xl font-bold text-white mb-6">Quick Actions</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <button className="bg-emerald-600 hover:bg-emerald-700 text-white py-3 px-6 rounded-lg font-semibold transition-colors flex items-center justify-center space-x-2">
              <Cpu className="w-5 h-5" />
              <span>Restart Services</span>
            </button>
            <button className="bg-blue-600 hover:bg-blue-700 text-white py-3 px-6 rounded-lg font-semibold transition-colors flex items-center justify-center space-x-2">
              <Globe className="w-5 h-5" />
              <span>Check API Status</span>
            </button>
            <button className="bg-purple-600 hover:bg-purple-700 text-white py-3 px-6 rounded-lg font-semibold transition-colors flex items-center justify-center space-x-2">
              <Zap className="w-5 h-5" />
              <span>Clear Cache</span>
            </button>
          </div>
        </motion.div>
      </div>
    </div>
  );
}