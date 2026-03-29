# 📌 Backlog Ágil - Gestão de Pedidos

Este documento gerencia as entregas do projeto. O desenvolvimento está dividido em Sprints temáticas.
**Instrução para o Agente de IA:** Ao concluir uma tarefa, marque com um `[x]` e aguarde a validação antes de prosseguir para a próxima.

## 🚀 Sprint 1: Fundação e Infraestrutura (Base)
- [ ] Criar a estrutura de diretórios do monorepo (`svc-auth`, `svc-catalogo`, `svc-pedidos`, `mfe-shell`, `mfe-pedidos`, `infra`).
- [ ] Criar os arquivos `requirements.txt` para cada microsserviço conforme as especificações.
- [ ] Configurar o arquivo `.env` base (contendo credenciais de banco, MinIO, RabbitMQ, chaves JWT, LLM e New Relic).
- [ ] Criar o arquivo `infra/nginx.conf` mapeando os upstreams e rotas do API Gateway.
- [ ] Criar o `docker-compose.yml` completo com as 3 redes (`rede_frontend`, `rede_backend_publica`, `rede_backend_soberana`), os 3 bancos PostgreSQL, Redis, RabbitMQ e MinIO (com o container `minio-setup`).
- [ ] Subir a infraestrutura e validar se todos os containers ficam `healthy`.

## 🛡️ Sprint 2: Microsserviço Soberano (Autenticação)
- [ ] Configurar a base do FastAPI, conexão com SQLAlchemy e schemas Pydantic no `svc-auth`.
- [ ] Criar o modelo de banco de dados `User` (id, nome_completo, email, password_hash).
- [ ] Implementar o endpoint `POST /api/auth/register` (com hash bcrypt).
- [ ] Implementar o endpoint `POST /api/auth/login` retornando o JWT apenas com o `sub` (UUID do usuário).
- [ ] Implementar a rotina de *Background Task* com a biblioteca `pika` para escutar a fila `notificacoes_pedidos` no RabbitMQ, buscar o usuário no banco e imprimir um log simulando o envio de e-mail.
- [ ] Testar a subida do container `svc-auth` via Docker.

## 📦 Sprint 3: Microsserviço de Catálogo (Público)
- [ ] Configurar a base do FastAPI, SQLAlchemy e Pydantic no `svc-catalogo`.
- [ ] Criar o modelo de banco `Product` (id, nome, descricao, preco_atual, anexo_url).
- [ ] Implementar a conexão com o MinIO usando `minio-python`.
- [ ] Implementar endpoints: `GET /api/catalogo/produtos` e `POST /api/catalogo/produtos/{id}/imagem` (upload para MinIO).
- [ ] Criar o script `seed.py` que insere 3 produtos iniciais na base (ex: Laptop, Monitor, Cadeira) caso a tabela esteja vazia.
- [ ] Testar a subida do container `svc-catalogo` e verificar o log do seed.

## 🛒 Sprint 4: Microsserviço de Pedidos (Público / Core)
- [ ] Configurar base do FastAPI, SQLAlchemy e dependências de autenticação (validação do JWT) no `svc-pedidos`.
- [ ] Configurar o **New Relic** no entrypoint da aplicação.
- [ ] Criar modelos de banco `Order` e `OrderItem`.
- [ ] Implementar a integração Síncrona via `httpx`: no endpoint de criar pedido, buscar o `preco_atual` no `svc-catalogo` antes de salvar.
- [ ] Implementar a integração com a **LLM** (OpenAI/Anthropic) para definir a `prioridade_ia` baseada na quantidade e valor total do pedido.
- [ ] Implementar a integração Assíncrona via `pika`: no endpoint de atualizar status para `CONCLUIDO`, publicar mensagem na fila `notificacoes_pedidos`.
- [ ] Implementar o **Redis** (`redis-py`) no endpoint `GET /api/pedidos/` usando padrão Cache-Aside (invalidando em novos `POST` ou `PUT`).

## 🖥️ Sprint 5: Microfrontends e Analytics
- [ ] Fazer o setup do **MFE Shell** (`mfe-shell`) com Vite, React, Tailwind e Module Federation.
- [ ] Implementar tela de Login, contexto global de Autenticação e armazenamento seguro do JWT.
- [ ] Fazer o setup do **MFE Pedidos** (`mfe-pedidos`) com Vite, React e Module Federation (expondo o componente principal para o Shell).
- [ ] Adicionar o script do **Microsoft Clarity** no `index.html` do `mfe-pedidos`, garantindo que o *Strict Masking* esteja configurado para ocultar PII.
- [ ] Desenvolver a tela de Catálogo (consumindo `GET /api/catalogo/produtos`).
- [ ] Desenvolver a tela de Gestão de Pedidos (consumindo `GET /api/pedidos/` e criando novos pedidos).
- [ ] Integrar os Microfrontends via API Gateway (`nginx`).

## 🧪 Sprint 6: Qualidade e CI/CD
- [ ] Escrever testes unitários para `svc-auth` (`test_auth.py` com `pytest-asyncio`).
- [ ] Escrever testes unitários para `svc-pedidos` (`test_pedidos.py`, realizando mock do Redis, RabbitMQ e LLM).
- [ ] Escrever testes unitários básicos para `svc-catalogo`.
- [ ] Criar o pipeline do GitHub Actions `.github/workflows/ci.yml` para rodar os testes a cada *push* na *main*.
- [ ] Revisão final: garantir que os comandos do `README.md` sobem a aplicação do zero perfeitamente.