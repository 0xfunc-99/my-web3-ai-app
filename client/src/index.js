import React from 'react';
import ReactDOM from 'react-dom/client'; // Import createRoot from react-dom/client
import App from './App';

// Get the root element from the HTML file
const rootElement = document.getElementById('root');

// Create a React root using createRoot
const root = ReactDOM.createRoot(rootElement);

// Render the app
root.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);