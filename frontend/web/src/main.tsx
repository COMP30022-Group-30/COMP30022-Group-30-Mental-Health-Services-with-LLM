import React from 'react';
import ReactDOM from 'react-dom/client';
import { BrowserRouter } from 'react-router-dom';
import { AuthProvider } from '@/auth/AuthContext';
import { AdminAuthProvider } from '@/admin/AdminAuthContext';
import { DyslexicModeProvider } from '@/accessibility/DyslexicModeContext';
import App from './App';
import '@/styles/index.css';
import '@/styles/tokens.css';

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <BrowserRouter>
      <DyslexicModeProvider>
        <AuthProvider>
          <AdminAuthProvider>
            <App />
          </AdminAuthProvider>
        </AuthProvider>
      </DyslexicModeProvider>
    </BrowserRouter>
  </React.StrictMode>
);
