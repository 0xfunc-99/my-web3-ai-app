import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import Navbar from './components/Navbar';
import SaveUserData from './pages/SaveUserData';
import FetchUserData from './pages/FetchUserData';
import AdminPortal from './pages/AdminPortal';
import AdminLogin from './components/AdminLogin';
import ProtectedRoute from './components/ProtectedRoute';
import './App.css';

function App() {
  return (
    <Router>
      <div className="app">
        <Navbar />
        <main className="main-content">
          <Routes>
            <Route path="/" element={<Navigate to="/save" replace />} />
            <Route path="/save" element={<SaveUserData />} />
            <Route path="/fetch" element={<FetchUserData />} />
            <Route path="/admin/login" element={<AdminLogin />} />
            <Route 
              path="/admin" 
              element={
                <ProtectedRoute>
                  <AdminPortal />
                </ProtectedRoute>
              } 
            />
          </Routes>
        </main>
      </div>
    </Router>
  );
}

export default App;