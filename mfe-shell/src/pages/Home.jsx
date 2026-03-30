import React, { lazy, Suspense } from 'react';
import ErrorBoundary from '../components/ErrorBoundary';

const MfePedidos = lazy(() => import('pedidos_app/Dashboard'));

export default function Home() {
  return (
    <div className="container-lg my-4" style={{ minHeight: 'calc(100vh - 200px)' }}>
      <h2 className="mb-4" style={{ color: '#1351b4', fontWeight: 700 }}>
        <i className="fas fa-inbox mr-2" aria-hidden="true"></i>
        Painel do Solicitante
      </h2>
      <ErrorBoundary>
        <Suspense fallback={
          <div className="text-center mt-5">
            <div className="br-loading large" role="progressbar" aria-label="Carregando módulo de pedidos"></div>
            <p className="mt-3 text-muted">Conectando ao Serviço de Pedidos...</p>
          </div>
        }>
          <MfePedidos />
        </Suspense>
      </ErrorBoundary>
    </div>
  );
}
