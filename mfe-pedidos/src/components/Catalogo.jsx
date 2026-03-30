import React, { useState, useEffect } from 'react';
import axios from 'axios';

export default function Catalogo({ onOrderCreated }) {
  const [produtos, setProdutos] = useState([]);
  const [loading, setLoading] = useState(true);
  const [carrinho, setCarrinho] = useState({});
  const [submitLoading, setSubmitLoading] = useState(false);
  const [feedback, setFeedback] = useState(null); // { type: 'success'|'danger', msg: '' }

  useEffect(() => {
    const token = localStorage.getItem('token');
    axios.get('/api/catalogo/produtos', {
      headers: { Authorization: `Bearer ${token}` },
      timeout: 15000
    })
      .then(res => {
        setProdutos(res.data);
        setLoading(false);
      })
      .catch(err => {
        console.error(err);
        setFeedback({ type: 'danger', msg: 'Erro ao carregar catálogo restrito.' });
        setLoading(false);
      });
  }, []);

  const handleAdd = (id) => {
    setCarrinho(prev => ({
      ...prev,
      [id]: (prev[id] || 0) + 1
    }));
  };

  const handleSub = (id) => {
    setCarrinho(prev => {
      const next = { ...prev };
      if (next[id] > 1) {
        next[id] -= 1;
      } else {
        delete next[id];
      }
      return next;
    });
  };

  const getTotalItems = () => Object.values(carrinho).reduce((a, b) => a + b, 0);

  const handleComprar = async () => {
    const items = Object.entries(carrinho).map(([id, qty]) => ({ product_id: id, quantity: qty }));
    if (items.length === 0) return;
    const token = localStorage.getItem('token');
    setSubmitLoading(true);
    try {
      await axios.post('/api/pedidos/', { items }, {
        headers: { Authorization: `Bearer ${token}` },
        timeout: 60000  // LLM pode levar até 30s
      });
      setFeedback({ type: 'success', msg: 'Pedido solicitado! A I.A de Risco foi acionada. Verifique em "Meus Pedidos".' });
      setCarrinho({});
      onOrderCreated();
    } catch (err) {
      const msg = err.code === 'ECONNABORTED'
        ? 'Tempo esgotado. O pedido pode ter sido gerado. Verifique em "Meus Pedidos".'
        : (err.response?.data?.detail || 'Falha ao processar Solicitação de Pedido.');
      setFeedback({ type: 'danger', msg });
    } finally {
      setSubmitLoading(false);
    }
  };

  if (loading) return <div className="br-loading mt-4" role="progressbar"></div>;

  return (
    <div>
      {feedback && (
        <div className={`br-message ${feedback.type} mb-4`} role="alert">
          <div className="icon"><i className={`fas ${feedback.type === 'success' ? 'fa-check-circle' : 'fa-times-circle'} fa-lg`} aria-hidden="true"></i></div>
          <div className="content">
            <span className="message-title">{feedback.type === 'success' ? 'Sucesso: ' : 'Erro: '}</span>
            <span className="message-body">{feedback.msg}</span>
          </div>
          <div className="close">
            <button className="br-button circle small" type="button" onClick={() => setFeedback(null)}>
              <i className="fas fa-times" aria-hidden="true"></i>
            </button>
          </div>
        </div>
      )}

      <div className="row g-4">
        <div className="col-12 col-lg-8">
          <div className="row">
            {produtos.map(p => (
              <div key={p.id} className="col-sm-6 col-md-4 mb-3">
                <div className="br-card">
                  <div className="card-header pb-0">
                    <img src={p.anexo_url} alt={p.nome} style={{ width: '100%', height: '180px', objectFit: 'cover', borderRadius: '4px' }} />
                  </div>
                  <div className="card-content mt-2">
                    <h5 className="font-weight-bold">{p.nome}</h5>
                    <p className="text-muted">R$ {p.preco_atual ? p.preco_atual.toFixed(2) : '0.00'}</p>
                  </div>
                  <div className="card-footer d-flex justify-content-between align-items-center">
                    {carrinho[p.id] ? (
                      <div className="d-flex align-items-center">
                        <button className="br-button circle small" type="button" onClick={() => handleSub(p.id)}><i className="fas fa-minus"></i></button>
                        <span className="mx-3">{carrinho[p.id]}</span>
                        <button className="br-button circle small" type="button" onClick={() => handleAdd(p.id)}><i className="fas fa-plus"></i></button>
                      </div>
                    ) : (
                      <button className="br-button primary block" type="button" onClick={() => handleAdd(p.id)}>
                        <i className="fas fa-cart-plus mr-1"></i> Selecionar
                      </button>
                    )}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>

        <div className="col-12 col-lg-4">
          <div className="br-card hover" style={{ position: 'sticky', top: '20px' }}>
            <div className="card-header border-bottom">
              <h5><i className="fas fa-shopping-basket mr-2"></i> Resumo da Requisição</h5>
            </div>
            <div className="card-content">
              {getTotalItems() === 0 ? (
                <p className="text-muted">Selecione itens ao lado para solicitar.</p>
              ) : (
                <ul className="br-list" role="list">
                  {Object.entries(carrinho).map(([id, qty]) => {
                    const prod = produtos.find(p => p.id === id);
                    if (!prod) return null;
                    return (
                      <li className="br-item py-3" key={id}>
                        <div className="row align-items-center">
                          <div className="col-auto"><span className="br-tag bg-primary text-white">{qty}x</span></div>
                          <div className="col">{prod.nome}</div>
                          <div className="col-auto font-weight-bold">R$ {((prod.preco_atual || 0) * qty).toFixed(2)}</div>
                        </div>
                      </li>
                    );
                  })}
                </ul>
              )}
            </div>
            <div className="card-footer mt-2 border-top">
              <button
                className="br-button primary block"
                type="button"
                disabled={getTotalItems() === 0 || submitLoading}
                onClick={handleComprar}
              >
                {submitLoading ? <i className="fas fa-spinner fa-spin mr-1"></i> : <i className="fas fa-check-circle mr-1"></i>}
                Finalizar Tramite ({getTotalItems()})
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
