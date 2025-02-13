import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';

const AdminLogin = () => {
    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');
    const [error, setError] = useState('');
    const [loading, setLoading] = useState(false);
    const navigate = useNavigate();

    const handleLogin = async (e) => {
        e.preventDefault();
        setLoading(true);
        setError('');
        
        try {
            const response = await axios.post('http://localhost:5002/admin/login', {
                username,
                password
            });
            
            localStorage.setItem('adminToken', response.data.token);
            localStorage.setItem('isAdmin', 'true');
            localStorage.setItem('adminUsername', response.data.username);
            navigate('/admin');
        } catch (error) {
            setError(error.response?.data?.error || 'Login failed. Please try again.');
        } finally {
            setLoading(false);
        }
    };

    return (
        <div style={{
            minHeight: '100vh',
            width: '100vw',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            background: 'linear-gradient(145deg, #1a2b4b 0%, #162037 100%)',
            margin: 0,
            padding: 0,
            position: 'fixed',
            top: 0,
            left: 0,
            right: 0,
            bottom: 0,
            overflow: 'hidden'
        }}>
            {/* Background pattern */}
            <div style={{
                position: 'absolute',
                width: '100%',
                height: '100%',
                background: 'radial-gradient(circle at 50% 50%, rgba(255, 255, 255, 0.05) 0%, transparent 50%)',
                opacity: 0.6
            }} />
            
            <div style={{
                width: '100%',
                maxWidth: '420px',
                padding: '48px 40px',
                backgroundColor: 'rgba(30, 41, 59, 0.65)',
                borderRadius: '16px',
                boxShadow: '0 20px 40px rgba(0, 0, 0, 0.2), inset 0 1px 0 rgba(255, 255, 255, 0.1)',
                backdropFilter: 'blur(10px)',
                border: '1px solid rgba(255, 255, 255, 0.1)',
                position: 'relative',
                zIndex: 1,
                margin: '20px'
            }}>
                <div style={{ textAlign: 'center', marginBottom: '35px' }}>
                    <h2 style={{
                        fontSize: '36px',
                        fontWeight: '700',
                        color: 'white',
                        marginBottom: '12px',
                        letterSpacing: '-0.5px'
                    }}>Admin Login</h2>
                    <p style={{ 
                        color: '#94a3b8', 
                        fontSize: '15px',
                        lineHeight: '1.5'
                    }}>
                        Please sign in to continue
                    </p>
                </div>

                {error && (
                    <div style={{
                        backgroundColor: 'rgba(239, 68, 68, 0.1)',
                        borderLeft: '4px solid #ef4444',
                        padding: '16px',
                        marginBottom: '24px',
                        borderRadius: '6px',
                        color: '#fca5a5',
                        fontSize: '14px'
                    }}>
                        {error}
                    </div>
                )}

                <form onSubmit={handleLogin}>
                    <div style={{ marginBottom: '24px' }}>
                        <label style={{
                            display: 'block',
                            marginBottom: '8px',
                            color: '#e2e8f0',
                            fontSize: '14px',
                            fontWeight: '500'
                        }}>
                            Username
                        </label>
                        <input
                            type="text"
                            value={username}
                            onChange={(e) => setUsername(e.target.value)}
                            style={{
                                width: '100%',
                                padding: '14px 16px',
                                backgroundColor: 'rgba(15, 23, 42, 0.6)',
                                border: '1px solid rgba(148, 163, 184, 0.2)',
                                borderRadius: '10px',
                                color: 'white',
                                fontSize: '15px',
                                outline: 'none',
                                transition: 'all 0.3s ease',
                                boxShadow: 'inset 0 2px 4px rgba(0, 0, 0, 0.1)'
                            }}
                            placeholder="Enter your username"
                            required
                        />
                    </div>

                    <div style={{ marginBottom: '32px' }}>
                        <label style={{
                            display: 'block',
                            marginBottom: '8px',
                            color: '#e2e8f0',
                            fontSize: '14px',
                            fontWeight: '500'
                        }}>
                            Password
                        </label>
                        <input
                            type="password"
                            value={password}
                            onChange={(e) => setPassword(e.target.value)}
                            style={{
                                width: '100%',
                                padding: '14px 16px',
                                backgroundColor: 'rgba(15, 23, 42, 0.6)',
                                border: '1px solid rgba(148, 163, 184, 0.2)',
                                borderRadius: '10px',
                                color: 'white',
                                fontSize: '15px',
                                outline: 'none',
                                transition: 'all 0.3s ease',
                                boxShadow: 'inset 0 2px 4px rgba(0, 0, 0, 0.1)'
                            }}
                            placeholder="Enter your password"
                            required
                        />
                    </div>

                    <button
                        type="submit"
                        disabled={loading}
                        style={{
                            width: '100%',
                            padding: '14px',
                            background: loading 
                                ? '#60a5fa' 
                                : 'linear-gradient(to right, #3b82f6, #2563eb)',
                            border: 'none',
                            borderRadius: '10px',
                            color: 'white',
                            fontSize: '16px',
                            fontWeight: '600',
                            cursor: loading ? 'not-allowed' : 'pointer',
                            transition: 'all 0.3s ease',
                            display: 'flex',
                            alignItems: 'center',
                            justifyContent: 'center',
                            gap: '8px',
                            boxShadow: '0 4px 12px rgba(59, 130, 246, 0.25)',
                            transform: loading ? 'none' : 'translateY(0)',
                            '&:hover': {
                                transform: loading ? 'none' : 'translateY(-1px)',
                                boxShadow: '0 6px 16px rgba(59, 130, 246, 0.3)'
                            }
                        }}
                    >
                        {loading ? (
                            <>
                                <svg style={{
                                    animation: 'spin 1s linear infinite',
                                    width: '20px',
                                    height: '20px'
                                }} viewBox="0 0 24 24">
                                    <circle
                                        style={{
                                            opacity: 0.25
                                        }}
                                        cx="12"
                                        cy="12"
                                        r="10"
                                        stroke="currentColor"
                                        strokeWidth="4"
                                        fill="none"
                                    />
                                    <path
                                        style={{
                                            opacity: 0.75
                                        }}
                                        fill="currentColor"
                                        d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                                    />
                                </svg>
                                Signing in...
                            </>
                        ) : 'Sign in'}
                    </button>
                </form>
            </div>
        </div>
    );
};

export default AdminLogin; 