'use client';

import Link from "next/link";
import { motion } from "framer-motion";
import { useState, useEffect } from "react";
import {
  Users,
  UserPlus,
  CheckCircle,
  XCircle,
  Clock,
  Building,
  Calendar,
  Search
} from "lucide-react";
import WakiliLogo from "../../../components/WakiliLogo";
import { supabase } from "@/lib/supabase";

interface User {
  id: string;
  email: string;
  full_name: string;
  company: string;
  role: 'admin' | 'user' | 'demo_user';
  demo_requested: boolean;
  demo_approved: boolean;
  demo_date: string | null;
  created_at: string;
}

export default function AdminUsersPage() {
  const [users, setUsers] = useState<User[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [filterRole, setFilterRole] = useState('all');
  const [filterDemo, setFilterDemo] = useState('all');

  useEffect(() => {
    fetchUsers();
  }, []);

  const fetchUsers = async () => {
    try {
      const { data, error } = await supabase
        .from('users')
        .select('*')
        .order('created_at', { ascending: false });

      if (error) {
        console.error('Error fetching users:', error);
      } else {
        setUsers(data || []);
      }
    } catch (error) {
      console.error('Error:', error);
    } finally {
      setLoading(false);
    }
  };

  const approveDemo = async (userId: string) => {
    try {
      const { error } = await supabase
        .from('users')
        .update({
          demo_approved: true,
          demo_date: new Date().toISOString()
        })
        .eq('id', userId);

      if (error) {
        console.error('Error approving demo:', error);
      } else {
        fetchUsers(); // Refresh the list
      }
    } catch (error) {
      console.error('Error:', error);
    }
  };

  const rejectDemo = async (userId: string) => {
    try {
      const { error } = await supabase
        .from('users')
        .update({
          demo_requested: false,
          demo_approved: false,
          demo_date: null
        })
        .eq('id', userId);

      if (error) {
        console.error('Error rejecting demo:', error);
      } else {
        fetchUsers(); // Refresh the list
      }
    } catch (error) {
      console.error('Error:', error);
    }
  };

  const filteredUsers = users.filter(user => {
    const matchesSearch = user.email.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         user.full_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         user.company.toLowerCase().includes(searchTerm.toLowerCase());

    const matchesRole = filterRole === 'all' || user.role === filterRole;
    const matchesDemo = filterDemo === 'all' ||
                       (filterDemo === 'requested' && user.demo_requested) ||
                       (filterDemo === 'approved' && user.demo_approved);

    return matchesSearch && matchesRole && matchesDemo;
  });

  const stats = {
    total: users.length,
    pending: users.filter(u => u.demo_requested && !u.demo_approved).length,
    approved: users.filter(u => u.demo_approved).length,
    new: users.filter(u => new Date(u.created_at) > new Date(Date.now() - 7 * 24 * 60 * 60 * 1000)).length
  };

  return (
    <div className="min-h-screen bg-gray-900">
      {/* Header */}
      <header className="bg-gray-800 border-b border-gray-700">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-4">
            <div className="flex items-center space-x-4">
              <Link href="/admin/dashboard">
                <WakiliLogo size="md" />
              </Link>
              <div className="text-white">
                <h1 className="text-lg font-semibold">User Management</h1>
                <p className="text-sm text-gray-400">Manage user accounts and demo requests</p>
              </div>
            </div>
            <Link
              href="/admin/dashboard"
              className="text-gray-400 hover:text-white transition-colors"
            >
              ← Back to Dashboard
            </Link>
          </div>
        </div>
      </header>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Stats */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
          className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8"
        >
          <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
            <div className="flex items-center">
              <Users className="w-8 h-8 text-blue-400" />
              <div className="ml-4">
                <p className="text-sm text-gray-400">Total Users</p>
                <p className="text-2xl font-bold text-white">{stats.total}</p>
              </div>
            </div>
          </div>
          <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
            <div className="flex items-center">
              <Clock className="w-8 h-8 text-yellow-400" />
              <div className="ml-4">
                <p className="text-sm text-gray-400">Pending Demos</p>
                <p className="text-2xl font-bold text-white">{stats.pending}</p>
              </div>
            </div>
          </div>
          <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
            <div className="flex items-center">
              <CheckCircle className="w-8 h-8 text-green-400" />
              <div className="ml-4">
                <p className="text-sm text-gray-400">Approved Demos</p>
                <p className="text-2xl font-bold text-white">{stats.approved}</p>
              </div>
            </div>
          </div>
          <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
            <div className="flex items-center">
              <UserPlus className="w-8 h-8 text-emerald-400" />
              <div className="ml-4">
                <p className="text-sm text-gray-400">New This Week</p>
                <p className="text-2xl font-bold text-white">{stats.new}</p>
              </div>
            </div>
          </div>
        </motion.div>

        {/* Filters */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.2 }}
          className="bg-gray-800 rounded-lg p-6 border border-gray-700 mb-8"
        >
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">Search</label>
              <div className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
                <input
                  type="text"
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="w-full pl-10 pr-4 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white placeholder-gray-400 focus:ring-2 focus:ring-emerald-500 focus:border-transparent"
                  placeholder="Search users..."
                />
              </div>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">Role</label>
              <select
                value={filterRole}
                onChange={(e) => setFilterRole(e.target.value)}
                className="w-full py-2 px-3 bg-gray-700 border border-gray-600 rounded-lg text-white focus:ring-2 focus:ring-emerald-500 focus:border-transparent"
              >
                <option value="all">All Roles</option>
                <option value="admin">Admin</option>
                <option value="user">User</option>
                <option value="demo_user">Demo User</option>
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">Demo Status</label>
              <select
                value={filterDemo}
                onChange={(e) => setFilterDemo(e.target.value)}
                className="w-full py-2 px-3 bg-gray-700 border border-gray-600 rounded-lg text-white focus:ring-2 focus:ring-emerald-500 focus:border-transparent"
              >
                <option value="all">All</option>
                <option value="requested">Demo Requested</option>
                <option value="approved">Demo Approved</option>
              </select>
            </div>
          </div>
        </motion.div>

        {/* Users Table */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.4 }}
          className="bg-gray-800 rounded-lg border border-gray-700 overflow-hidden"
        >
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-700">
              <thead className="bg-gray-700">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase tracking-wider">
                    User
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase tracking-wider">
                    Company
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase tracking-wider">
                    Role
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase tracking-wider">
                    Demo Status
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase tracking-wider">
                    Joined
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase tracking-wider">
                    Actions
                  </th>
                </tr>
              </thead>
              <tbody className="bg-gray-800 divide-y divide-gray-700">
                {loading ? (
                  <tr>
                    <td colSpan={6} className="px-6 py-4 text-center text-gray-400">
                      Loading users...
                    </td>
                  </tr>
                ) : filteredUsers.length === 0 ? (
                  <tr>
                    <td colSpan={6} className="px-6 py-4 text-center text-gray-400">
                      No users found
                    </td>
                  </tr>
                ) : (
                  filteredUsers.map((user) => (
                    <tr key={user.id} className="hover:bg-gray-700">
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="flex items-center">
                          <div className="flex-shrink-0 h-10 w-10">
                            <div className="h-10 w-10 rounded-full bg-emerald-500/20 flex items-center justify-center">
                              <span className="text-sm font-medium text-emerald-400">
                                {user.full_name.charAt(0).toUpperCase()}
                              </span>
                            </div>
                          </div>
                          <div className="ml-4">
                            <div className="text-sm font-medium text-white">{user.full_name}</div>
                            <div className="text-sm text-gray-400">{user.email}</div>
                          </div>
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="flex items-center">
                          <Building className="w-4 h-4 text-gray-400 mr-2" />
                          <span className="text-sm text-gray-300">{user.company}</span>
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${
                          user.role === 'admin' ? 'bg-red-100 text-red-800' :
                          user.role === 'demo_user' ? 'bg-yellow-100 text-yellow-800' :
                          'bg-green-100 text-green-800'
                        }`}>
                          {user.role}
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        {user.demo_requested ? (
                          user.demo_approved ? (
                            <div className="flex items-center">
                              <CheckCircle className="w-4 h-4 text-green-400 mr-2" />
                              <span className="text-sm text-green-400">Approved</span>
                              {user.demo_date && (
                                <Calendar className="w-4 h-4 text-gray-400 ml-2" />
                              )}
                            </div>
                          ) : (
                            <div className="flex items-center">
                              <Clock className="w-4 h-4 text-yellow-400 mr-2" />
                              <span className="text-sm text-yellow-400">Pending</span>
                            </div>
                          )
                        ) : (
                          <span className="text-sm text-gray-400">No request</span>
                        )}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-300">
                        {new Date(user.created_at).toLocaleDateString()}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                        {user.demo_requested && !user.demo_approved && (
                          <div className="flex space-x-2">
                            <button
                              onClick={() => approveDemo(user.id)}
                              className="text-green-400 hover:text-green-300"
                            >
                              <CheckCircle className="w-4 h-4" />
                            </button>
                            <button
                              onClick={() => rejectDemo(user.id)}
                              className="text-red-400 hover:text-red-300"
                            >
                              <XCircle className="w-4 h-4" />
                            </button>
                          </div>
                        )}
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        </motion.div>
      </div>
    </div>
  );
}