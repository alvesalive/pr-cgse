import React from 'react';

export default function Header() {
  const userEmail = localStorage.getItem('user_email') || '';
  const userRole = localStorage.getItem('user_role') || 'USER';
  const isAdmin = userRole === 'ADMIN';
  const isLoggedIn = !!localStorage.getItem('token');
  const firstName = userEmail.split('@')[0] || '';

  const handleLogout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('user_email');
    window.location.href = '/login';
  };

  return (
    <header className="br-header" id="header" data-sticky="data-sticky" style={{ width: '100%' }}>
      <div className="container-lg">
        <div className="header-top">
          <div className="header-logo">
            <img src="/govbr-logo.png" alt="logo gov.br" style={{ height: '40px' }} />
            <span className="br-divider vertical"></span>
            <div className="header-sign">Governo Federal</div>
          </div>
          <div className="header-actions">
            {isLoggedIn && (
              <div className="header-login d-flex align-items-center" style={{ gap: '12px' }}>
                {isAdmin && (
                  <a
                    href="/admin"
                    className="br-button circle small"
                    title="Painel Administrativo"
                    style={{ textDecoration: 'none' }}
                  >
                    <i className="fas fa-cogs" aria-hidden="true"></i>
                  </a>
                )}
                <div style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: '8px',
                  padding: '4px 12px',
                  borderRadius: '20px',
                  background: 'rgba(19, 81, 180, 0.08)',
                  fontSize: '14px',
                  color: '#1351b4',
                  fontWeight: 600
                }}>
                  <i className="fas fa-user-circle" aria-hidden="true"></i>
                  <span>{firstName}</span>
                </div>
                <button
                  className="br-sign-in small"
                  type="button"
                  onClick={handleLogout}
                  style={{ marginLeft: '4px' }}
                >
                  <i className="fas fa-sign-out-alt" aria-hidden="true"></i>
                  <span className="d-sm-inline ml-1">Sair</span>
                </button>
              </div>
            )}
          </div>
        </div>
        <div className="header-bottom">
          <div className="header-menu">
            <div className="header-info">
              <div className="header-title font-weight-bold text-primary">
                Plataforma de Gestão de Pedidos
              </div>
              <div className="header-subtitle">Casa Civil - Presidência da República</div>
            </div>
          </div>
        </div>
      </div>
    </header>
  );
}
