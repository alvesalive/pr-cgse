import React from 'react';

export default class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error) {
    return { hasError: true, error };
  }

  componentDidCatch(error, info) {
    console.error('[ErrorBoundary] Erro no componente remoto:', error, info);
  }

  render() {
    if (this.state.hasError) {
      return (
        <div className="container-lg my-5">
          <div className="br-message danger">
            <div className="icon">
              <i className="fas fa-exclamation-triangle fa-lg" aria-hidden="true"></i>
            </div>
            <div className="content">
              <span className="message-title">Erro ao carregar módulo: </span>
              <span className="message-body">
                O serviço de pedidos está temporariamente indisponível. Verifique se todos os contêineres estão rodando.
              </span>
            </div>
            <div className="close">
              <button
                className="br-button circle small"
                type="button"
                onClick={() => this.setState({ hasError: false, error: null })}
              >
                <i className="fas fa-redo" aria-hidden="true"></i>
              </button>
            </div>
          </div>
          {import.meta.env.DEV && (
            <pre style={{ fontSize: '12px', color: '#c00', marginTop: '16px' }}>
              {String(this.state.error)}
            </pre>
          )}
        </div>
      );
    }
    return this.props.children;
  }
}
