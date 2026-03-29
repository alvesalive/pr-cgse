# Especificações Técnicas de Desenvolvimento
Atue como Desenvolvedor Sênior. Siga a arquitetura de Microfrontends (Vite+React) e Microsserviços (FastAPI).

## 1. MFE Shell (Porta 3000)
* Gerencia o login. Guarda JWT. NÃO possui Microsoft Clarity.

## 2. MFE Pedidos/Catálogo (Porta 3001)
* MFE injetado via Module Federation. Possui MS Clarity com *Strict Masking*.
* Exibe listagem de produtos do catálogo (com imagens do MinIO) e listagem de pedidos.

## 3. Microsserviço Auth (`/svc-auth` - Nuvem Soberana)
* **Banco:** `db-soberano`. Tabela: `User` (id, nome_completo, email, password_hash).
* **Worker:** Escuta fila `notificacoes_pedidos` no RabbitMQ, cruza UUID com email e simula envio de email (print log).

## 4. Microsserviço Catálogo (`/svc-catalogo` - Nuvem Pública)
* **Banco:** `db-catalogo`. Tabela: `Product` (id, nome, descricao, preco_atual, anexo_url).
* **Feature:** `POST /produtos/{id}/imagem` faz upload para o MinIO (bucket `catalogo-imagens`).
* **Seed:** Ao iniciar, um script `seed.py` deve popular o banco com 3 produtos fictícios.

## 5. Microsserviço Pedidos (`/svc-pedidos` - Nuvem Pública)
* **Banco:** `db-publico`. Tabelas: `Order` e `OrderItem`.
* **Redis:** Usar Cache-Aside no `GET /pedidos`.
* **Integração Síncrona (Catálogo):** No `POST /pedidos`, receber `product_id` e `quantidade`. Fazer requisição HTTP via `httpx` para `http://svc-catalogo:8000/produtos/{id}` para obter o `preco_atual`. Salvar este preço no `OrderItem`.
* **Integração IA:** Após salvar, chamar LLM com prompt anônimo para definir `prioridade_ia`.
* **Integração Assíncrona:** No `PUT /pedidos/{id}/status`, se for CONCLUIDO, enviar `{"pedido_id": id, "user_uuid": uuid}` para o RabbitMQ.
* **Observabilidade:** Instrumentar com New Relic.