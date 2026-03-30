import React, { useState } from 'react';
import axios from 'axios';
import { useNavigate, Link } from 'react-router-dom';

export default function Register() {
  const [form, setForm] = useState({ nome_completo: '', email: '', password: '', confirmPassword: '' });
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const handleChange = (e) => setForm(prev => ({ ...prev, [e.target.id]: e.target.value }));

  const handleRegister = async (e) => {
    e.preventDefault();
    setError('');

    if (form.password !== form.confirmPassword) {
      setError('As senhas não coincidem.');
      return;
    }
    if (form.password.length < 6) {
      setError('A senha deve ter no mínimo 6 caracteres.');
      return;
    }

    setLoading(true);
    try {
      const response = await axios.post('/api/auth/register', {
        nome_completo: form.nome_completo,
        email: form.email,
        password: form.password,
      });

      if (response.data.access_token) {
        localStorage.setItem('token', response.data.access_token);
        localStorage.setItem('user_email', form.email);
        localStorage.setItem('user_role', response.data.role || 'USER');
        window.location.href = '/';
      }
    } catch (err) {
      const msg = err.response?.data?.detail || 'Erro ao realizar cadastro.';
      setError(msg);
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
              <h1 className="h4 font-weight-bold">Criar Conta Institucional</h1>
              <p className="text-muted">Preencha os dados para solicitar acesso</p>
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

              <form onSubmit={handleRegister}>
                <div className="br-input mb-4">
                  <label htmlFor="nome_completo">Nome Completo</label>
                  <input
                    id="nome_completo"
                    type="text"
                    placeholder="Seu nome completo"
                    value={form.nome_completo}
                    onChange={handleChange}
                    required
                  />
                </div>

                <div className="br-input mb-4">
                  <label htmlFor="email">E-mail Corporativo</label>
                  <input
                    id="email"
                    type="email"
                    placeholder="nome@orgao.gov.br"
                    value={form.email}
                    onChange={handleChange}
                    required
                  />
                </div>

                <div className="br-input mb-4">
                  <label htmlFor="password">Senha</label>
                  <input
                    id="password"
                    type="password"
                    placeholder="Mínimo 6 caracteres"
                    value={form.password}
                    onChange={handleChange}
                    required
                  />
                </div>

                <div className="br-input mb-4">
                  <label htmlFor="confirmPassword">Confirmar Senha</label>
                  <input
                    id="confirmPassword"
                    type="password"
                    placeholder="Repita sua senha"
                    value={form.confirmPassword}
                    onChange={handleChange}
                    required
                  />
                </div>

                <div className="mt-4 text-center">
                  <button type="submit" className="br-button primary block" disabled={loading}>
                    {loading
                      ? <><i className="fas fa-spinner fa-spin mr-1"></i> Criando conta...</>
                      : <><i className="fas fa-user-plus mr-1"></i> Cadastrar</>
                    }
                  </button>
                </div>

                <div className="mt-3 text-center">
                  <Link to="/login" className="br-button secondary block mt-2">
                    <i className="fas fa-arrow-left mr-1"></i> Já tenho conta — Entrar
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
