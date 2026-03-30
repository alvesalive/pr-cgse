import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Link } from 'react-router-dom';

export default function Admin() {
  const [produtos, setProdutos] = useState([]);
  const [loading, setLoading] = useState(true);
  const [feedback, setFeedback] = useState(null);

  // Form produto
  const [novoForm, setNovoForm] = useState({ nome: '', descricao: '', preco_atual: '' });
  const [novoLoading, setNovoLoading] = useState(false);
  const [editandoId, setEditandoId] = useState(null);
  const [confirmarExclusaoId, setConfirmarExclusaoId] = useState(null);

  // Upload de imagem
  const [uploadProdutoId, setUploadProdutoId] = useState('');
  const [uploadFile, setUploadFile] = useState(null);
  const [uploadLoading, setUploadLoading] = useState(false);

  const token = localStorage.getItem('token');
  const ax = axios.create({ headers: { Authorization: `Bearer ${token}` } });

  const fetchProdutos = () => {
    setLoading(true);
    ax.get('/api/catalogo/produtos')
      .then(res => setProdutos(res.data))
      .catch(() => setFeedback({ type: 'danger', msg: 'Erro ao carregar catálogo.' }))
      .finally(() => setLoading(false));
  };

  useEffect(() => { fetchProdutos(); }, []);

  const handleSalvarProduto = async (e) => {
    e.preventDefault();
    setNovoLoading(true);
    setFeedback(null);
    try {
      const payload = {
        nome: novoForm.nome,
        descricao: novoForm.descricao,
        preco_atual: parseFloat(novoForm.preco_atual),
      };
      
      if (editandoId) {
        await ax.put(`/api/catalogo/produtos/${editandoId}`, payload);
        setFeedback({ type: 'success', msg: `Produto "${novoForm.nome}" atualizado com sucesso!` });
      } else {
        await ax.post('/api/catalogo/produtos', payload);
        setFeedback({ type: 'success', msg: `Produto "${novoForm.nome}" cadastrado com sucesso!` });
      }
      
      setNovoForm({ nome: '', descricao: '', preco_atual: '' });
      setEditandoId(null);
      fetchProdutos();
    } catch (err) {
      const msg = err.response?.data?.detail || 'Erro ao salvar produto.';
      setFeedback({ type: 'danger', msg });
    } finally {
      setNovoLoading(false);
    }
  };

  const handleEditarClick = (p) => {
    setEditandoId(p.id);
    setNovoForm({ nome: p.nome, descricao: p.descricao, preco_atual: p.preco_atual });
  };
  
  const handleCancelarEdicao = () => {
    setEditandoId(null);
    setNovoForm({ nome: '', descricao: '', preco_atual: '' });
  };

  const handleExcluirProduto = async (id, nome) => {
    setFeedback(null);
    try {
      await ax.delete(`/api/catalogo/produtos/${id}`);
      setFeedback({ type: 'success', msg: 'Produto excluído com sucesso!' });
      setConfirmarExclusaoId(null);
      fetchProdutos();
    } catch (err) {
      const msg = err.response?.data?.detail || 'Erro ao excluir produto.';
      setFeedback({ type: 'danger', msg });
      setConfirmarExclusaoId(null);
    }
  };

  const handleUploadImagem = async (e) => {
    e.preventDefault();
    if (!uploadProdutoId || !uploadFile) {
      setFeedback({ type: 'danger', msg: 'Selecione um produto e uma imagem.' });
      return;
    }
    setUploadLoading(true);
    setFeedback(null);
    const formData = new FormData();
    formData.append('file', uploadFile);
    try {
      await ax.post(`/api/catalogo/produtos/${uploadProdutoId}/imagem`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });
      setFeedback({ type: 'success', msg: 'Imagem enviada ao MinIO S3 com sucesso! ✅' });
      setUploadFile(null);
      setUploadProdutoId('');
      fetchProdutos();
    } catch (err) {
      const msg = err.response?.data?.detail || 'Erro no upload da imagem.';
      setFeedback({ type: 'danger', msg });
    } finally {
      setUploadLoading(false);
    }
  };

  return (
    <div className="container-lg my-4">
      <div className="d-flex align-items-center justify-content-between mb-4">
        <div>
          <h2 className="mb-1" style={{ color: '#1351b4', fontWeight: 700 }}>
            <i className="fas fa-cogs mr-2"></i> Painel Administrativo
          </h2>
          <p className="text-muted mb-0">Gestão de Catálogo de Bens — Acesso Restrito</p>
        </div>
        <Link to="/" className="br-button secondary">
          <i className="fas fa-arrow-left mr-2"></i> Voltar ao Catálogo
        </Link>
      </div>

      {feedback && (
        <div className={`br-message ${feedback.type} mb-4`} role="alert">
          <div className="icon">
            <i className={`fas ${feedback.type === 'success' ? 'fa-check-circle' : 'fa-times-circle'} fa-lg`}></i>
          </div>
          <div className="content">
            <span className="message-body">{feedback.msg}</span>
          </div>
          <div className="close">
            <button className="br-button circle small" type="button" onClick={() => setFeedback(null)}>
              <i className="fas fa-times"></i>
            </button>
          </div>
        </div>
      )}

      <div className="row">
        {/* Form Produto */}
        <div className="col-12 col-lg-5 mb-4">
          <div className="br-card" style={{ padding: '24px' }}>
            <h5 className="font-weight-bold mb-3">
              <i className={`fas ${editandoId ? 'fa-edit text-warning' : 'fa-plus-circle text-primary'} mr-2`}></i> 
              {editandoId ? 'Editando Produto' : 'Cadastrar Novo Produto'}
            </h5>
            <form onSubmit={handleSalvarProduto}>
              <div className="br-input mb-3">
                <label htmlFor="adm-nome">Nome do Bem</label>
                <input id="adm-nome" type="text" placeholder="Ex: Notebook Dell i7"
                  value={novoForm.nome} onChange={e => setNovoForm(p => ({ ...p, nome: e.target.value }))} required />
              </div>
              <div className="br-input mb-3">
                <label htmlFor="adm-desc">Descrição</label>
                <input id="adm-desc" type="text" placeholder="Especificações técnicas"
                  value={novoForm.descricao} onChange={e => setNovoForm(p => ({ ...p, descricao: e.target.value }))} />
              </div>
              <div className="br-input mb-4">
                <label htmlFor="adm-preco">Preço Unitário (R$)</label>
                <input id="adm-preco" type="number" step="0.01" min="0" placeholder="0.00"
                  value={novoForm.preco_atual} onChange={e => setNovoForm(p => ({ ...p, preco_atual: e.target.value }))} required />
              </div>
              <div className="d-flex" style={{gap: '8px'}}>
                <button type="submit" className={`br-button block ${editandoId ? 'secondary' : 'primary'}`} disabled={novoLoading} style={{flex: 1}}>
                  {novoLoading
                    ? <><i className="fas fa-spinner fa-spin mr-1"></i> Salvando...</>
                    : <><i className="fas fa-save mr-1"></i> {editandoId ? 'Atualizar Produto' : 'Salvar Produto'}</>
                  }
                </button>
                {editandoId && (
                  <button type="button" className="br-button block" onClick={handleCancelarEdicao} style={{flex: 1}}>
                    <i className="fas fa-times mr-1"></i> Cancelar
                  </button>
                )}
              </div>
            </form>
          </div>

          {/* Upload de imagem */}
          <div className="br-card mt-3" style={{ padding: '24px' }}>
            <h5 className="font-weight-bold mb-3">
              <i className="fas fa-cloud-upload-alt mr-2 text-primary"></i> Upload de Imagem → MinIO S3
            </h5>
            <form onSubmit={handleUploadImagem}>
              <div className="br-select mb-3">
                <label htmlFor="adm-produto-sel">Produto</label>
                <select id="adm-produto-sel"
                  value={uploadProdutoId}
                  onChange={e => setUploadProdutoId(e.target.value)}
                  required
                  style={{ width: '100%', padding: '10px', border: '1px solid #ccc', borderRadius: '4px' }}
                >
                  <option value="">-- Selecione um produto --</option>
                  {produtos.map(p => (
                    <option key={p.id} value={p.id}>{p.nome}</option>
                  ))}
                </select>
              </div>
              <div className="br-upload mb-4">
                <label htmlFor="adm-img">Arquivo de Imagem</label>
                <input id="adm-img" type="file" accept="image/*"
                  onChange={e => setUploadFile(e.target.files[0])}
                  style={{ display: 'block', marginTop: '8px' }}
                  required />
                {uploadFile && (
                  <small className="text-muted mt-1 d-block">
                    <i className="fas fa-image mr-1"></i> {uploadFile.name}
                  </small>
                )}
              </div>
              <button type="submit" className="br-button secondary block" disabled={uploadLoading}>
                {uploadLoading
                  ? <><i className="fas fa-spinner fa-spin mr-1"></i> Enviando ao S3...</>
                  : <><i className="fas fa-upload mr-1"></i> Enviar Imagem</>
                }
              </button>
            </form>
          </div>
        </div>

        {/* Tabela de produtos existentes */}
        <div className="col-12 col-lg-7 mb-4">
          <div className="br-card" style={{ padding: '24px' }}>
            <h5 className="font-weight-bold mb-3">
              <i className="fas fa-list mr-2 text-primary"></i> Produtos Cadastrados
            </h5>
            {loading ? (
              <div className="br-loading" role="progressbar"></div>
            ) : produtos.length === 0 ? (
              <div className="br-message info">
                <div className="icon"><i className="fas fa-info-circle"></i></div>
                <div className="content">Nenhum produto cadastrado. Use o formulário ao lado.</div>
              </div>
            ) : (
              <div className="br-table">
                <table>
                  <thead>
                    <tr>
                      <th>Nome</th>
                      <th>Preço</th>
                      <th>Imagem S3</th>
                      <th>Ações</th>
                    </tr>
                  </thead>
                  <tbody>
                    {produtos.map(p => (
                      <tr key={p.id}>
                        <td>
                          <div className="font-weight-bold">{p.nome}</div>
                          <small className="text-muted">{p.descricao}</small>
                        </td>
                        <td>R$ {(p.preco_atual || 0).toFixed(2)}</td>
                        <td>
                          {p.anexo_url ? (
                            <span className="br-tag bg-success text-white">
                              <i className="fas fa-check mr-1"></i> Bucket OK
                            </span>
                          ) : (
                            <span className="br-tag bg-secondary text-white">
                              <i className="fas fa-clock mr-1"></i> Sem imagem
                            </span>
                          )}
                        </td>
                        <td>
                          {confirmarExclusaoId === p.id ? (
                            <div className="d-flex align-items-center" style={{gap: '5px', padding: '4px', backgroundColor: '#fff3f3', borderRadius: '4px', border: '1px solid #f5c2c7'}}>
                              <span className="text-danger small font-weight-bold">Deletar?</span>
                              <button className="br-button danger small" onClick={() => handleExcluirProduto(p.id, p.nome)}>Sim</button>
                              <button className="br-button secondary small" onClick={() => setConfirmarExclusaoId(null)}>Não</button>
                            </div>
                          ) : (
                            <>
                              <button className="br-button circle small" type="button" onClick={() => handleEditarClick(p)} title="Editar Produto">
                                <i className="fas fa-edit text-primary"></i>
                              </button>
                              <button className="br-button circle small" type="button" onClick={() => setConfirmarExclusaoId(p.id)} title="Excluir Produto">
                                <i className="fas fa-trash text-danger"></i>
                              </button>
                            </>
                          )}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
