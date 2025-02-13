import React, { useState, useEffect } from 'react';
import axios from 'axios';

const AdminDashboard = () => {
    const [stats, setStats] = useState(null);
    const [logs, setLogs] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState('');
    const [filter, setFilter] = useState('all');
    const [timeRange, setTimeRange] = useState('all');
    const [searchQuery, setSearchQuery] = useState('');

    const fetchData = async () => {
        setLoading(true);
        setError('');
        const token = localStorage.getItem('adminToken');

        try {
            const [statsResponse, logsResponse] = await Promise.all([
                axios.get('http://localhost:5002/admin/dashboard', {
                    headers: { Authorization: `Bearer ${token}` }
                }),
                axios.get('http://localhost:5002/admin/logs', {
                    headers: { Authorization: `Bearer ${token}` }
                })
            ]);

            setStats(statsResponse.data);
            setLogs(logsResponse.data.logs);
        } catch (error) {
            setError(error.response?.data?.error || 'Failed to fetch data');
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchData();
        // Set up auto-refresh every 30 seconds
        const interval = setInterval(fetchData, 30000);
        return () => clearInterval(interval);
    }, []);

    const filteredLogs = logs.filter(log => {
        const matchesFilter = filter === 'all' || log.type === filter;
        const matchesSearch = searchQuery === '' || 
            log.message.toLowerCase().includes(searchQuery.toLowerCase());
        
        if (timeRange === 'all') return matchesFilter && matchesSearch;
        
        const logDate = new Date(log.timestamp);
        const now = new Date();
        const hoursDiff = (now - logDate) / (1000 * 60 * 60);
        
        switch (timeRange) {
            case '1h': return hoursDiff <= 1 && matchesFilter && matchesSearch;
            case '24h': return hoursDiff <= 24 && matchesFilter && matchesSearch;
            case '7d': return hoursDiff <= 168 && matchesFilter && matchesSearch;
            default: return matchesFilter && matchesSearch;
        }
    });

    if (loading) {
        return (
            <div className="flex justify-center items-center min-h-[400px]">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600"></div>
            </div>
        );
    }

    return (
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <h1 className="text-3xl font-bold text-gray-900 mb-8">Admin Dashboard</h1>

            {error && (
                <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded relative mb-4">
                    {error}
                </div>
            )}

            {/* Stats Grid */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
                <div className="bg-white rounded-lg shadow p-6">
                    <h3 className="text-lg font-medium text-gray-900">Total Logs</h3>
                    <p className="text-3xl font-bold text-indigo-600">{stats?.total_predictions || 0}</p>
                </div>
                <div className="bg-white rounded-lg shadow p-6">
                    <h3 className="text-lg font-medium text-gray-900">Attacks Detected</h3>
                    <p className="text-3xl font-bold text-red-600">{stats?.attack_predictions || 0}</p>
                </div>
                <div className="bg-white rounded-lg shadow p-6">
                    <h3 className="text-lg font-medium text-gray-900">Safe Transactions</h3>
                    <p className="text-3xl font-bold text-green-600">{stats?.safe_predictions || 0}</p>
                </div>
            </div>

            {/* Filters */}
            <div className="bg-white rounded-lg shadow p-6 mb-8">
                <div className="flex flex-wrap gap-4 items-center">
                    <select
                        value={filter}
                        onChange={(e) => setFilter(e.target.value)}
                        className="rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
                    >
                        <option value="all">All Types</option>
                        <option value="XSS Attack">Attacks</option>
                        <option value="Blockchain Transaction">Transactions</option>
                    </select>

                    <select
                        value={timeRange}
                        onChange={(e) => setTimeRange(e.target.value)}
                        className="rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
                    >
                        <option value="all">All Time</option>
                        <option value="1h">Last Hour</option>
                        <option value="24h">Last 24 Hours</option>
                        <option value="7d">Last 7 Days</option>
                    </select>

                    <input
                        type="text"
                        placeholder="Search logs..."
                        value={searchQuery}
                        onChange={(e) => setSearchQuery(e.target.value)}
                        className="flex-1 rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
                    />
                </div>
            </div>

            {/* Logs Table */}
            <div className="bg-white rounded-lg shadow overflow-hidden">
                <div className="overflow-x-auto">
                    <table className="min-w-full divide-y divide-gray-200">
                        <thead className="bg-gray-50">
                            <tr>
                                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                    Timestamp
                                </th>
                                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                    Type
                                </th>
                                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                    Level
                                </th>
                                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                    Message
                                </th>
                            </tr>
                        </thead>
                        <tbody className="bg-white divide-y divide-gray-200">
                            {filteredLogs.map((log, index) => (
                                <tr key={index}>
                                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                                        {new Date(log.timestamp).toLocaleString()}
                                    </td>
                                    <td className="px-6 py-4 whitespace-nowrap">
                                        <span className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${
                                            log.type === 'XSS Attack' 
                                                ? 'bg-red-100 text-red-800'
                                                : 'bg-green-100 text-green-800'
                                        }`}>
                                            {log.type}
                                        </span>
                                    </td>
                                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                                        {log.level}
                                    </td>
                                    <td className="px-6 py-4 text-sm text-gray-900">
                                        {log.message}
                                    </td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    );
};

export default AdminDashboard; 