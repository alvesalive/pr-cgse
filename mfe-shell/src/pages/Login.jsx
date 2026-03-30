import React, { useState } from 'react';
import axios from 'axios';
import { useNavigate, Link } from 'react-router-dom';

export default function Login() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const handleLogin = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    try {
      const response = await axios.post('/api/auth/login', { email, password });
      if (response.data.access_token) {
        localStorage.setItem('token', response.data.access_token);
        localStorage.setItem('user_email', email);
        localStorage.setItem('user_role', response.data.role || 'USER');
        navigate('/');
        window.location.href = '/'; // força reload para mfe-pedidos reler localStorage
      }
    } catch (err) {
      setError('Credenciais inválidas ou serviço indisponível.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="container-lg" style={{ marginTop: '40px', minHeight: 'calc(100vh - 150px)' }}>
      <div className="row justify-content-center">
        <div className="col-12 col-md-6 col-lg-5">
          <div className="br-card" style={{ padding: '32px' }}>
            <div className="card-header pb-4 pt-2 text-center">
              <h1 className="h4 font-weight-bold">Acesso ao Sistema</h1>
              <p className="text-muted">Utilize suas credenciais institucionais</p>
            </div>

            <div className="card-content">
              {error && (
                <div className="br-message danger mb-3" role="alert">
                  <div className="icon"><i className="fas fa-times-circle fa-lg" aria-hidden="true"></i></div>
                  <div className="content">
                    <span className="message-title">Erro: </span>
                    <span className="message-body">{error}</span>
                  </div>
                  <div className="close">
                    <button className="br-button circle small" type="button" onClick={() => setError('')}>
                      <i className="fas fa-times" aria-hidden="true"></i>
                    </button>
                  </div>
                </div>
              )}

              <form onSubmit={handleLogin}>
                <div className="br-input mb-4">
                  <label htmlFor="email">E-mail Corporativo</label>
                  <input
                    id="email"
                    type="email"
                    placeholder="Digite seu e-mail"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    required
                  />
                  <button className="br-button circle small" type="button" aria-label="Limpar" onClick={() => setEmail('')}>
                    <i className="fas fa-times" aria-hidden="true"></i>
                  </button>
                </div>

                <div className="br-input mt-4">
                  <label htmlFor="password">Senha de Acesso</label>
                  <input
                    id="password"
                    type="password"
                    placeholder="Digite sua senha"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    required
                  />
                </div>

                <div className="mt-5 text-center">
                  <button type="submit" className="br-button primary block" disabled={loading}>
                    {loading
                      ? <><i className="fas fa-spinner fa-spin mr-1"></i> Acessando...</>
                      : 'Entrar na Plataforma'
                    }
                  </button>
                </div>

                <div className="mt-3 text-center">
                  <Link to="/register" className="br-button secondary block">
                    <i className="fas fa-user-plus mr-1"></i> Criar nova conta institucional
                  </Link>
                </div>
              </form>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
