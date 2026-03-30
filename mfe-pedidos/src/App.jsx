import React, { useState } from 'react';
import Catalogo from './components/Catalogo';
import PedidosList from './components/PedidosList';

export default function App() {
  const [activeTab, setActiveTab] = useState('catalogo');
  const [refreshTrigger, setRefreshTrigger] = useState(0);

  const handleOrderCreated = () => {
    setRefreshTrigger(prev => prev + 1);
    setActiveTab('pedidos');
  };

  const tabStyle = (tab) => ({
    background: 'none',
    border: 'none',
    padding: '12px 20px',
    cursor: 'pointer',
    fontSize: '15px',
    fontFamily: 'inherit',
    borderBottom: activeTab === tab ? '3px solid #1351b4' : '3px solid transparent',
    color: activeTab === tab ? '#1351b4' : '#555',
    fontWeight: activeTab === tab ? '700' : '400',
    transition: 'all 0.2s',
  });

  return (
    <div>
      {/* Navegação de Abas — React state, sem depender do JS do GOV.BR */}
      <div style={{ borderBottom: '1px solid #ddd', marginBottom: '24px', display: 'flex' }}>
        <button
          type="button"
          style={tabStyle('catalogo')}
          onClick={() => setActiveTab('catalogo')}
        >
          <i className="fas fa-box-open mr-2" aria-hidden="true"></i>
          Catálogo de Bens
        </button>
        <button
          type="button"
          style={tabStyle('pedidos')}
          onClick={() => setActiveTab('pedidos')}
        >
          <i className="fas fa-list mr-2" aria-hidden="true"></i>
          Meus Pedidos Recentes
        </button>
      </div>

      {/* Conteúdo */}
      {activeTab === 'catalogo' && (
        <Catalogo onOrderCreated={handleOrderCreated} />
      )}
      {activeTab === 'pedidos' && (
        <PedidosList refreshTrigger={refreshTrigger} />
      )}
    </div>
  );
}
