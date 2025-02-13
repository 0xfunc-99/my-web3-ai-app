import React from 'react';
import { Navigate } from 'react-router-dom';

const ProtectedRoute = ({ children }) => {
    const isAdmin = localStorage.getItem('isAdmin') === 'true';
    
    if (!isAdmin) {
        return <Navigate to="/admin/login" />;
    }

    return children;
};

export default ProtectedRoute; 