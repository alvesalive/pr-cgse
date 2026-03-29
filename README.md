# Plataforma de Gestão de Pedidos Internos

Este projeto (MVP) visa modernizar o controle de pedidos internos corporativos, substituindo planilhas por uma arquitetura distribuída, segura e observável.

## Decisões de Arquitetura e Segurança (LGPD e Nuvem Soberana)
O sistema foi desenhado com foco estrito em segurança governamental/corporativa, implementando uma topologia de **três redes isoladas** no Docker (simulando uma DMZ e a segregação de dados):

* **DMZ / Rede Frontend:** Contém os Microfrontends (React) e o API Gateway (Nginx). É a única camada com portas expostas para o usuário final, filtrando e roteando as requisições.
* **Nuvem Pública (Operacional):** Contém o `svc-catalogo` e o `svc-pedidos`. Opera os fluxos de negócio, cache e storage usando apenas UUIDs anônimos.
* **Nuvem Soberana (Isolada):** Contém o `svc-auth` e o banco de usuários. Protege Dados Pessoais Identificáveis (PII). Não possui rota de rede para a DMZ ou para a internet, sendo acessível apenas internamente via API Gateway para autenticação ou via mensageria para rotinas em background.

* **Comunicação Inter-serviços (Padrões Híbridos):**
  * **Síncrona (HTTP):** O `svc-pedidos` consulta o `svc-catalogo` em tempo real para obter o preço do produto no momento da compra.
  * **Assíncrona (Eventos/RabbitMQ):** O `svc-pedidos` publica eventos de "Pedido Concluído". O `svc-auth` consome a fila para disparar notificações cruzando o UUID anônimo com o e-mail real.
* **Observabilidade:** New Relic (APM) habilitado apenas nos serviços públicos. 

## Estratégia de Microfrontends e Analytics
A interface foi dividida usando a abordagem de Module Federation (Vite + React) para garantir escalabilidade de times e isolamento de responsabilidades:
* **MFE Shell (Host):** Responsável apenas pela casca da aplicação, roteamento e Autenticação (Login). Operando com dados sensíveis, ele **não possui** nenhum script de telemetria externa.
* **MFE Pedidos (Remote):** Responsável pela operação do catálogo e gestão. Aqui implementamos o **Microsoft Clarity** para obter mapas de calor (heatmaps) e session replay.
  * O Clarity foi configurado com **Strict Masking**. Isso garante que a Microsoft receba os dados de usabilidade (onde o usuário clica, se há atrito na tela), mas todos os textos, valores e números são substituídos por asteriscos no momento da gravação no navegador. O time de UX ganha métricas, e a instituição garante compliance com a LGPD.

## Como Executar
1. Configure o `.env` (use o `.env.example`).
2. Suba a stack: `docker-compose up --build -d` (O banco de catálogo já fará o *seed* inicial de produtos).
3. Acesse a aplicação via API Gateway: `http://localhost:8080`.

## Trade-offs
Para manter o foco na entrega, algumas tecnologias foram intencionalmente deixadas de fora:

* **Kubernetes (K8s) Real:** Devido a complexidade e maiores exigencias de infraestrutura, optou-se por simular o comportamento do K8s (Namespaces e Liveness/Readiness Probes) diretamente no `docker-compose`.

* **Apache Kafka:** Embora seja o "padrão" para event-streaming, exige mais infraestrutura e complexidade. Para o escopo de disparar notificações assíncronas isoladas, o **RabbitMQ** oferece o padrão de mensageria (AMQP) com baixo consumo de recursos.

* **BFF (Backend for Frontend) Customizado:** Em vez de construir um microsserviço dedicado apenas para agregar dados para o React, optou-se por usar o  Nginx como um API Gateway leve. 