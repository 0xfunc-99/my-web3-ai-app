import React, { useState, useEffect } from 'react';
import axios from 'axios';
import {
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend,
  PieChart, Pie, Cell, ResponsiveContainer
} from 'recharts';
import './AdminPortal.css';

const AdminPortal = () => {
  const [logs, setLogs] = useState([]);
  const [stats, setStats] = useState({});
  const [loading, setLoading] = useState(true);
  const [animate, setAnimate] = useState(false);
  const [currentTime, setCurrentTime] = useState(new Date());
  const [filterType, setFilterType] = useState('all');
  const [dateRange, setDateRange] = useState('all');
  const [searchTerm, setSearchTerm] = useState('');

  useEffect(() => {
    fetchLogs();
    // Start animation after data is loaded
    setTimeout(() => setAnimate(true), 100);
    // Refresh logs every 30 seconds
    const interval = setInterval(fetchLogs, 30000);
    
    // Update current time every second
    const timeInterval = setInterval(() => {
      setCurrentTime(new Date());
    }, 1000);

    return () => {
      clearInterval(interval);
      clearInterval(timeInterval);
    };
  }, []);

  const fetchLogs = async () => {
    try {
      const token = localStorage.getItem('adminToken');
      const response = await axios.get('http://localhost:5002/admin/logs', {
        headers: {
          Authorization: `Bearer ${token}`
        }
      });
      setLogs(response.data.logs);
      setStats(response.data.stats);
      setLoading(false);
    } catch (error) {
      console.error('Error fetching logs:', error);
      // If token is invalid, redirect to login
      if (error.response?.status === 401) {
        localStorage.removeItem('adminToken');
        localStorage.removeItem('isAdmin');
        localStorage.removeItem('adminUsername');
        window.location.href = '/admin/login';
      }
    }
  };

  // Filter logs based on type, date range, and search term
  const getFilteredLogs = () => {
    return logs.filter(log => {
      const matchesType = filterType === 'all' || log.type === filterType;
      const matchesSearch = log.message.toLowerCase().includes(searchTerm.toLowerCase()) ||
                          log.type.toLowerCase().includes(searchTerm.toLowerCase());
      
      if (dateRange === 'today') {
        const today = new Date().toDateString();
        const logDate = new Date(log.timestamp).toDateString();
        return matchesType && matchesSearch && today === logDate;
      }
      
      if (dateRange === 'week') {
        const weekAgo = new Date();
        weekAgo.setDate(weekAgo.getDate() - 7);
        const logDate = new Date(log.timestamp);
        return matchesType && matchesSearch && logDate >= weekAgo;
      }
      
      return matchesType && matchesSearch;
    });
  };

  // Prepare data for charts
  const prepareTimeSeriesData = () => {
    const timeData = getFilteredLogs().reduce((acc, log) => {
      const hour = new Date(log.timestamp).getHours();
      acc[hour] = (acc[hour] || 0) + 1;
      return acc;
    }, {});

    return Object.entries(timeData).map(([hour, count]) => ({
      hour: `${hour}:00`,
      count
    }));
  };

  const preparePieChartData = () => {
    const filteredLogs = getFilteredLogs();
    const securityAlerts = filteredLogs.filter(log => log.type === 'Security Alert').length;
    const transactions = filteredLogs.filter(log => log.type === 'Transaction').length;
    
    return [
      { name: 'Security Alerts', value: securityAlerts },
      { name: 'Transactions', value: transactions }
    ];
  };

  const COLORS = ['#FF6B6B', '#4ECDC4'];

  return (
    <div className={`admin-portal ${animate ? 'animate' : ''}`}>
      <div className="header">
        <div className="header-left">
          <h1>Admin Dashboard</h1>
          <div className="current-time">
            {currentTime.toLocaleTimeString()}
          </div>
        </div>
        <div className="refresh-button" onClick={fetchLogs}>
          <i className="fas fa-sync-alt"></i>
        </div>
      </div>
      
      {loading ? (
        <div className="loading">
          <div className="loader"></div>
          <p>Loading dashboard data...</p>
        </div>
      ) : (
        <>
          <div className="filters-section">
            <div className="filter-group">
              <select 
                value={filterType} 
                onChange={(e) => setFilterType(e.target.value)}
                className="filter-select"
              >
                <option value="all">All Types</option>
                <option value="XSS Attack">XSS Attacks</option>
                <option value="Blockchain Transaction">Transactions</option>
              </select>

              <select 
                value={dateRange} 
                onChange={(e) => setDateRange(e.target.value)}
                className="filter-select"
              >
                <option value="all">All Time</option>
                <option value="today">Today</option>
                <option value="week">Last 7 Days</option>
              </select>

              <input
                type="text"
                placeholder="Search logs..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="search-input"
              />
            </div>
          </div>

          <div className="stats-cards">
            <div className="stat-card">
              <div className="stat-icon">📊</div>
              <h3>Total Logs</h3>
              <p className="stat-number">{getFilteredLogs().length}</p>
              <div className="stat-indicator"></div>
            </div>
            <div className="stat-card warning">
              <div className="stat-icon">⚠️</div>
              <h3>Attacks Detected</h3>
              <p className="stat-number">
                {getFilteredLogs().filter(log => log.type === 'XSS Attack').length}
              </p>
              <div className="stat-indicator"></div>
            </div>
            <div className="stat-card success">
              <div className="stat-icon">✅</div>
              <h3>Transactions</h3>
              <p className="stat-number">
                {getFilteredLogs().filter(log => log.type === 'Blockchain Transaction').length}
              </p>
              <div className="stat-indicator"></div>
            </div>
          </div>

          <div className="charts-container">
            <div className="chart-card">
              <h2>Activity Timeline</h2>
              <ResponsiveContainer width="100%" height={300}>
                <LineChart data={prepareTimeSeriesData()}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#2c3e50" opacity={0.1} />
                  <XAxis dataKey="hour" stroke="#718096" />
                  <YAxis stroke="#718096" />
                  <Tooltip 
                    contentStyle={{ 
                      backgroundColor: '#1a202c',
                      border: 'none',
                      borderRadius: '8px',
                      color: '#fff'
                    }}
                  />
                  <Legend />
                  <Line 
                    type="monotone" 
                    dataKey="count" 
                    stroke="#4ECDC4"
                    strokeWidth={2}
                    dot={{ stroke: '#4ECDC4', strokeWidth: 2 }}
                    activeDot={{ r: 8 }}
                  />
                </LineChart>
              </ResponsiveContainer>
            </div>

            <div className="chart-card">
              <h2>Activity Distribution</h2>
              <ResponsiveContainer width="100%" height={300}>
                <PieChart>
                  <Pie
                    data={preparePieChartData()}
                    cx="50%"
                    cy="50%"
                    labelLine={false}
                    outerRadius={80}
                    fill="#8884d8"
                    dataKey="value"
                    animationBegin={0}
                    animationDuration={1500}
                  >
                    {preparePieChartData().map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                    ))}
                  </Pie>
                  <Tooltip 
                    contentStyle={{ 
                      backgroundColor: '#1a202c',
                      border: 'none',
                      borderRadius: '8px',
                      color: '#fff'
                    }}
                  />
                  <Legend />
                </PieChart>
              </ResponsiveContainer>
            </div>
          </div>

          <div className="logs-section">
            <h2>Recent Activity Logs</h2>
            <div className="logs-table-container">
              <table className="logs-table">
                <thead>
                  <tr>
                    <th>Timestamp</th>
                    <th>Type</th>
                    <th>Message</th>
                    <th>Status</th>
                  </tr>
                </thead>
                <tbody>
                  {getFilteredLogs().slice(-10).map((log, index) => (
                    <tr 
                      key={index} 
                      className={`log-row ${log.type === 'XSS Attack' ? 'attack-log' : ''}`}
                      style={{ animationDelay: `${index * 0.1}s` }}
                    >
                      <td>
                        {new Date(log.timestamp || new Date()).toLocaleString('en-US', {
                          year: 'numeric',
                          month: 'short',
                          day: 'numeric',
                          hour: '2-digit',
                          minute: '2-digit',
                          second: '2-digit',
                          hour12: true
                        })}
                      </td>
                      <td>
                        <span className={`log-type ${log.type.toLowerCase().replace(/\s+/g, '-')}`}>
                          {log.type === 'Transaction' ? '🔗 Transaction' : '⚠️ Security Alert'}
                        </span>
                      </td>
                      <td>{log.message}</td>
                      <td>
                        <span className={`status-badge ${log.status === 'Success' ? 'success' : 'error'}`}>
                          {log.status === 'Success' ? '✅ Success' : '❌ Failed'}
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </>
      )}
    </div>
  );
};

export default AdminPortal;

