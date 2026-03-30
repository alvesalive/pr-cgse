import React, { useState, useEffect, useRef } from 'react';
import axios from 'axios';

export default function PedidosList({ refreshTrigger }) {
  const [pedidos, setPedidos] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [confirmarExclusaoId, setConfirmarExclusaoId] = useState(null);
  const pollingRef = useRef(null);

  const fetchPedidos = (silent = false) => {
    const token = localStorage.getItem('token');
    if (!silent) setLoading(true);
    setError('');
    return axios.get('/api/pedidos/', {
      headers: { Authorization: `Bearer ${token}` },
      timeout: 15000
    })
      .then(res => {
        setPedidos(res.data);
        return res.data;
      })
      .catch(err => {
        if (!silent) {
          const msg = err.code === 'ECONNABORTED'
            ? 'Tempo esgotado. Tente novamente.'
            : `Erro ${err.response?.status || err.message}`;
          setError(msg);
        }
        return [];
      })
      .finally(() => { if (!silent) setLoading(false); });
  };

  const handleExcluirPedido = async (id) => {
    const token = localStorage.getItem('token');
    setError('');
    try {
      await axios.delete(`/api/pedidos/${id}`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setConfirmarExclusaoId(null);
      fetchPedidos();
    } catch (err) {
      setError(err.response?.data?.detail || 'Erro ao excluir pedido.');
      setConfirmarExclusaoId(null);
    }
  };

  // Polling automático enquanto houver pedidos "ANALISANDO"
  useEffect(() => {
    const hasAnalyzing = pedidos.some(p => p.risk_level === 'ANALISANDO');
    if (hasAnalyzing && !pollingRef.current) {
      pollingRef.current = setInterval(() => {
        fetchPedidos(true).then(data => {
          const stillAnalyzing = data.some(p => p.risk_level === 'ANALISANDO');
          if (!stillAnalyzing && pollingRef.current) {
            clearInterval(pollingRef.current);
            pollingRef.current = null;
          }
        });
      }, 4000);
    }
    if (!hasAnalyzing && pollingRef.current) {
      clearInterval(pollingRef.current);
      pollingRef.current = null;
    }
    return () => {
      if (pollingRef.current) {
        clearInterval(pollingRef.current);
        pollingRef.current = null;
      }
    };
  }, [pedidos]);

  useEffect(() => { fetchPedidos(); }, [refreshTrigger]);

  const riscoBadge = (risco) => {
    const styles = {
      BAIXO:      { bg: '#df9101', text: '#fff', label: 'baixo' },
      MEDIO:      { bg: '#0969da', text: '#fff', label: 'médio' },
      ALTO:       { bg: '#cf222e', text: '#fff', label: 'alto' },
      ANALISANDO: { bg: '#6e7781', text: '#fff', label: 'processando...' },
    };
    return styles[risco] || { bg: '#888', text: '#fff', label: risco || 'sem análise' };
  };

  if (loading) return (
    <div className="text-center mt-5">
      <div className="br-loading large" role="progressbar"></div>
      <p className="mt-3 text-muted">Buscando seus pedidos...</p>
    </div>
  );

  if (error) return (
    <div className="br-message danger mt-4" role="alert">
      <div className="icon"><i className="fas fa-times-circle fa-lg"></i></div>
      <div className="content"><span className="message-body">{error}</span></div>
      <div className="close">
        <button className="br-button circle small" type="button" onClick={() => fetchPedidos()}>
          <i className="fas fa-redo"></i>
        </button>
      </div>
    </div>
  );

  if (!pedidos.length) return (
    <div className="br-message info mt-4">
      <div className="icon"><i className="fas fa-info-circle"></i></div>
      <div className="content">Nenhum pedido efetuado ainda. Vá ao Catálogo para realizar uma solicitação.</div>
    </div>
  );

  return (
    <div className="br-table">
      <table>
        <thead>
          <tr>
            <th scope="col">Data / ID</th>
            <th scope="col">Status</th>
            <th scope="col">Classificação I.A</th>
            <th scope="col" className="text-right">Valor</th>
            <th scope="col">Itens</th>
            <th scope="col">Ações</th>
          </tr>
        </thead>
        <tbody>
          {pedidos.map(ped => {
            return (
              <tr key={ped.id}>
                <td data-th="Data / ID">
                  <span className="font-weight-bold">{new Date(ped.created_at).toLocaleString('pt-BR')}</span>
                  <br /><small className="text-muted">{ped.id.substring(0, 8)}...</small>
                </td>
                <td data-th="Status">
                  <span className="br-tag bg-primary text-white">{ped.status}</span>
                </td>
                <td data-th="Classificação I.A">
                  {(() => {
                    const b = riscoBadge(ped.risk_level);
                    return (
                        <span style={{
                          display: 'inline-flex',
                          alignItems: 'center',
                          justifyContent: 'center',
                          padding: '4px 14px',
                          borderRadius: '20px',
                          background: b.bg,
                          color: b.text,
                          fontSize: '11px',
                          fontWeight: 700,
                          lineHeight: '1.2',
                          textTransform: 'lowercase',
                          minWidth: '70px',
                          boxShadow: '0 1px 2px rgba(0,0,0,0.1)',
                          animation: ped.risk_level === 'ANALISANDO' ? 'pulse 1.2s infinite' : 'none'
                        }}>
                          {b.label}
                        </span>
                    );
                  })()}
                </td>
                <td data-th="Valor" className="text-right font-weight-bold" style={{ color: '#168821' }}>
                  R$ {(ped.total_amount || 0).toFixed(2)}
                </td>
                <td data-th="Itens">
                  {(ped.items || []).map(it => (
                    <div key={it.id}>{it.quantity}x {it.product_name}</div>
                  ))}
                </td>
                <td data-th="Ações">
                  {confirmarExclusaoId === ped.id ? (
                    <div className="d-flex align-items-center" style={{gap: '5px', padding: '4px', backgroundColor: '#fff3f3', borderRadius: '4px', border: '1px solid #f5c2c7'}}>
                      <span className="text-danger small font-weight-bold">Excluir?</span>
                      <button className="br-button danger small" onClick={() => handleExcluirPedido(ped.id)}>Sim</button>
                      <button className="br-button secondary small" onClick={() => setConfirmarExclusaoId(null)}>Não</button>
                    </div>
                  ) : (
                    <button 
                      className="br-button circle small" 
                      type="button" 
                      onClick={() => setConfirmarExclusaoId(ped.id)} 
                      title="Excluir Pedido"
                      disabled={ped.status === 'CANCELADO_EXCLUIDO'}
                    >
                      <i className="fas fa-trash text-danger"></i>
                    </button>
                  )}
                </td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
}
