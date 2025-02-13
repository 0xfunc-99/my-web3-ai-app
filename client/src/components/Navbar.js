import React from 'react';
import { Link, useNavigate } from 'react-router-dom';

const Navbar = () => {
    const navigate = useNavigate();
    const isAdmin = localStorage.getItem('isAdmin') === 'true';

    const handleLogout = () => {
        localStorage.removeItem('isAdmin');
        navigate('/admin/login');
    };

    return (
        <nav style={{ 
            background: '#333', 
            padding: '1rem', 
            color: 'white'
        }}>
            <ul style={{ 
                listStyle: 'none', 
                display: 'flex', 
                gap: '20px', 
                margin: 0, 
                padding: 0 
            }}>
                <li>
                    <Link to="/save" style={{ color: 'white', textDecoration: 'none' }}>
                        Save Data
                    </Link>
                </li>
                <li>
                    <Link to="/fetch" style={{ color: 'white', textDecoration: 'none' }}>
                        View Data
                    </Link>
                </li>
                <li>
                    {isAdmin ? (
                        <>
                            <Link to="/admin" style={{ color: 'white', textDecoration: 'none', marginRight: '10px' }}>
                                Admin Portal
                            </Link>
                            <button 
                                onClick={handleLogout}
                                style={{
                                    background: '#dc3545',
                                    color: 'white',
                                    border: 'none',
                                    padding: '5px 10px',
                                    borderRadius: '3px',
                                    cursor: 'pointer'
                                }}
                            >
                                Logout
                            </button>
                        </>
                    ) : (
                        <Link to="/admin/login" style={{ color: 'white', textDecoration: 'none' }}>
                            Admin Login
                        </Link>
                    )}
                </li>
            </ul>
        </nav>
    );
};

export default Navbar; 