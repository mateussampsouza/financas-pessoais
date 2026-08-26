# Plano de Implementação: Aplicativo de Finanças Pessoais Moderno e Responsivo

Aplicativo web completo de gestão financeira pessoal com interface responsiva mobile-first (desktop e smartphone), modo escuro elegante, autenticação de usuários com isolamento multi-tenant, backend em Python moderno (FastAPI + SQLite + SQLAlchemy / Pydantic), frontend reativo com visualização por gráficos (Chart.js), animações, testes automatizados (pytest) e empacotamento para deploy em produção (Docker / Fly.io).

---

## 🏗️ Arquitetura e Tecnologias

1. **Backend (Python)**:
   - **FastAPI**: API REST rápida, moderna, com validação de dados via Pydantic e OpenAPI/Swagger automático.
   - **SQLite + SQLAlchemy**: Banco de dados relacional local leve, sem necessidade de servidores externos.
   - **Autenticação JWT**: `python-jose` para geração/validação de tokens e `bcrypt` para hash de senhas.
   - **Pytest + TestClient**: Suíte completa de testes unitários e de integração cobrindo autenticação, transações, categorias, filtros e regras de negócio.
2. **Frontend**:
   - **Arquitetura SPA / Responsiva**: Single Page Application fluida com navegação sem recarregamento de página.
   - **Design & UI**: Vanilla CSS moderno com paleta escura sofisticada (Glassmorphism, gradientes suaves, cards elegantes, micro-interações).
   - **Gráficos**: **Chart.js** integrado (Gráfico de barras horizontal para Despesas vs Receitas na Home; Gráfico Donut de Despesas por Categoria).
   - **Ícones**: Lucide Icons modernos e seletor intuitivo de ícones/cores para categorias.
   - **Mobile-first Bottom Bar**: Menu fixo inferior estilizado para smartphones e adaptado para telas desktop.
3. **Infraestrutura / Deploy**:
   - **Docker**: imagem baseada em `python:3.14-slim`, expõe a aplicação via `uvicorn` na porta definida pela variável de ambiente `PORT`; o `CMD` roda `alembic upgrade head` antes do `uvicorn`, aplicando migrações de schema pendentes a cada início do container.
   - **Fly.io**: build via Dockerfile (`fly.toml`), com diretório de dados configurável (`FINANCAS_DATA_DIR`) apontando para um volume persistente, garantindo que o banco SQLite e a chave JWT sobrevivam a novos deploys.

---

## 🔐 Autenticação de Usuários e Multi-tenant

- **Cadastro / Login**: tela de autenticação com alternância entre "Entrar" e "Cadastrar", visual dark/glassmorphism consistente com o restante do app.
- **Modelo `User`**: `id`, `username` (único, case-insensitive), `password_hash` (bcrypt), `created_at`.
- **Sessão via JWT**: token emitido no registro/login, persistido em `localStorage` no frontend e enviado em toda requisição via header `Authorization: Bearer <token>`; expiração de 7 dias.
- **Chave de assinatura do JWT**: lida de `FINANCAS_SECRET_KEY` se definida; caso contrário, gerada automaticamente e persistida em `.secret_key` dentro do diretório de dados (`FINANCAS_DATA_DIR`), garantindo tokens válidos entre reinícios.
- **Isolamento multi-tenant**: `Category` e `Transaction` possuem `user_id` obrigatório (FK para `users.id`), com filtragem por usuário autenticado em todos os endpoints de categorias, transações e resumo.
- **Seed automático**: ao cadastrar um novo usuário, categorias padrão são criadas automaticamente para ele (`app/seed.py`).
- **Cabeçalho da aplicação**: exibe o nome do usuário logado e botão de "Sair" (logout limpa o token e retorna à tela de login).
- **Endpoints de autenticação**:
  - `POST /api/auth/register`: cria usuário, gera categorias padrão e retorna token.
  - `POST /api/auth/login`: valida credenciais e retorna token.
  - `GET /api/auth/me`: retorna dados do usuário autenticado.

---

## 📱 Telas & Funcionalidades

### 0. Tela de Login / Cadastro
- Card único com alternância entre os modos "Entrar" e "Cadastrar".
- Validação de usuário/senha inválidos e feedback amigável de erro.
- Ao autenticar com sucesso, token é salvo e o dashboard é carregado.

### 1. Tela Home
- **Card Resumo**:
  - Saldo Atual (com formatação monetária em R$ e destaque visual positivo/negativo).
  - Gráfico de barras horizontal comparativo de Receitas vs Despesas.
- **Transações Recentes**:
  - Lista de transações filtradas exclusivamente para hoje e até 3 dias anteriores (últimos 4 dias), restritas ao usuário logado.
  - Cards detalhados com: descrição, tipo (despesa/receita com cores e badges), valor, categoria (com ícone e cor), data/hora.
  - Clique no card abre diretamente a tela de Edição de Transação.

### 2. Tela Todas as Transações
- **Filtros**:
  - Data inicial (padrão: 1º dia do mês atual) e Data final (padrão: último dia do mês atual) — formato YYYY-MM-DD.
  - Ao selecionar uma data no seletor, o calendário fecha/desfoca automaticamente (sem cliques extras).
  - Filtro por tipo: botões interativos `[ Todas ]`, `[ Despesas ]`, `[ Receitas ]`.
- **Lista de Transações**:
  - Cards com descrição, tipo, valor, categoria (ícone/cor), data e hora.
  - Ao clicar no card, abre a tela Nova Transação em modo de **Edição da Transação**.
  - Exibição de totais filtrados do período.

### 3. Tela Categorias
- **Filtro de Data**: Data inicial (1º dia do mês) e Data final (último dia do mês).
- **Card Donut Chart**: Gráfico donut das despesas agrupadas por categoria no período filtrado.
- **Lista de Cards de Categorias**:
  - Ícone, cor personalizada, nome da categoria e total de gastos acumulado no período selecionado.
  - Clique no card abre em modo **Editar Categoria** (editando nome, ícone e cor).
- **Botão Adicionar Categoria**: Direciona para o formulário de Nova Categoria.
- **Bloqueio de exclusão**: categorias com transações vinculadas não podem ser excluídas; o backend retorna HTTP 400 com mensagem clara e o frontend exibe o aviso amigável correspondente.

### 4. Tela Nova / Editar Transação
- Campos:
  - Tipo: Despesa ou Receita
  - Descrição
  - Valor, com **máscara monetária dinâmica** em tempo real (ex: `R$ 0,00` → `R$ 1.250,50`), com parsing transparente para decimal/float no envio à API e preenchimento correto ao editar transações existentes.
  - Categoria (seleção dinâmica com visualização do ícone e cor)
  - Data e Hora
  - **Recorrência**: select com `nunca`, `diária`, `semanal`, `mensal`, `anual`
  - **Quantidade**: total de ocorrências da série (numérico, 1-99); desabilitado quando Recorrência = `nunca`
  - **Parcela**: posição da transação atual dentro da série (numérico, 1-99), sempre limitada ao valor de Quantidade (o campo trava o próprio `max` e reduz o valor digitado se exceder)
- Ações: Botão Salvar, Botão Excluir (quando em edição), Botão Cancelar/Voltar.
- **Regra de geração de recorrência**: dado `quantidade = N` e `parcela = P` (posição da ocorrência sendo criada dentro da série), o backend gera as `N` transações da série de uma só vez — `P-1` ocorrências no passado e `N-P` no futuro a partir da data/hora informada — todas com a mesma descrição, tipo, valor, categoria e hora, mudando apenas a data:
  - `diária`: cada ocorrência soma/subtrai 1 dia da anterior.
  - `semanal`: soma/subtrai 7 dias, mantendo o mesmo dia da semana.
  - `mensal`/`anual`: mesmo dia do mês/ano, com ajuste automático para meses mais curtos (ex.: 31/01 recorrente mensal → 28/02, ou 29/02 em ano bissexto).
  - Todas as ocorrências de uma mesma série compartilham um `recurrence_group_id`.
- **Edição não propaga**: editar qualquer campo de uma ocorrência (descrição, valor, categoria, data/hora) nunca altera as demais transações da série — os campos Recorrência, Quantidade e Parcela ficam bloqueados tanto na UI (`disabled`) quanto na API (o schema de atualização não os aceita).
- **Exclusão com diálogo de escolha**: ao excluir uma transação que pertence a uma série (`recurrence_group_id` não nulo), um modal de confirmação (novo componente — o app não tinha nenhum modal antes) pergunta se deve excluir **somente aquela ocorrência** ou **ela e todas as seguintes** da série (a partir da data clicada em diante; ocorrências anteriores nunca são afetadas). O endpoint `DELETE /api/transactions/{id}` aceita `?mode=only|following` para isso.

### 5. Tela Nova / Editar Categoria
- Campos:
  - Nome da Categoria
  - Seletor visual de Ícones (grid de ícones modernos: alimentação, transporte, moradia, lazer, salário, investimentos, saúde, compras, etc.)
  - Seletor de Cores (paleta de cores pré-definidas harmoniosas + color picker customizado)
- Ações: Botão Salvar, Botão Excluir (quando em edição), Botão Cancelar/Voltar.

### 6. Menu Fixo Inferior (Bottom Bar)
- Itens fixos na barra inferior:
  - 🏠 **Home**
  - 📊 **Transações**
  - ➕ **Novo** (atalho rápido para Nova Transação)
  - 🏷️ **Categorias**
  - 💰 **Receita** (atalho que abre diretamente o formulário de Nova Transação com o tipo Receita pré-selecionado e travado)

---

## 📂 Estrutura do Projeto

```
financas-pessoais-antg-prompt/
├── app/
│   ├── __init__.py
│   ├── main.py              # Ponto de entrada FastAPI, lifespan (create_all) e montagem dos estáticos
│   ├── config.py            # Configurações do app: DATABASE_URL, FINANCAS_DATA_DIR, JWT (SECRET_KEY, algoritmo, expiração)
│   ├── database.py          # Conexão SQLite e SessionLocal com SQLAlchemy
│   ├── models.py            # Modelos do banco (User, Category, Transaction) com relacionamentos e user_id
│   ├── schemas.py           # Schemas Pydantic de entrada e saída (incluindo UserCreate, UserLogin, UserResponse, Token)
│   ├── auth.py              # Hash/verificação de senha (bcrypt), criação/validação de JWT, dependência get_current_user
│   ├── seed.py              # Categorias padrão criadas para cada novo usuário
│   ├── routers/
│   │   ├── auth.py          # Endpoints de registro, login e usuário autenticado (/api/auth)
│   │   ├── transactions.py  # Endpoints CRUD e filtros de transações (protegidos por usuário)
│   │   ├── categories.py    # Endpoints CRUD e agregadores de categorias (protegidos por usuário)
│   │   └── summary.py       # Endpoints de resumo da Home (saldo, barras, recentes), por usuário
│   └── static/
│       ├── index.html       # HTML semântico com todas as visualizações SPA (incluindo tela de login/cadastro)
│       ├── css/
│       │   └── style.css    # Tema Dark moderno, Glassmorphism, responsividade perfeita
│       └── js/
│           ├── app.js       # Gerenciamento de estado, navegação, autenticação e manipulação DOM
│           ├── api.js       # Camada de comunicação com endpoints FastAPI (envia Authorization: Bearer <token>)
│           └── charts.js    # Inicialização e renderização do Chart.js (Barras e Donut)
├── tests/
│   ├── __init__.py
│   ├── conftest.py          # Fixtures de banco de dados em memória e usuário autenticado para testes
│   ├── test_auth.py         # Testes de registro, login, senha incorreta e validação de token
│   ├── test_categories.py   # Testes dos endpoints de categorias, incluindo bloqueio de exclusão vinculada
│   ├── test_transactions.py # Testes de criação, edição, filtros e recorrência (geração diária/semanal/mensal, validação, edição isolada, exclusão only/following)
│   └── test_summary.py      # Testes das métricas da Home, saldo e isolamento entre usuários
├── alembic/
│   ├── env.py                # Configuração do Alembic (lê DATABASE_URL de app/config.py)
│   └── versions/              # Migrações versionadas do schema (ex: recurrence_group_id, recurrence_quantity, recurrence_installment)
├── alembic.ini                 # Configuração do Alembic (script_location)
├── Dockerfile                # Build da imagem de produção (Python 3.14-slim + uvicorn); copia alembic/ e roda `alembic upgrade head` antes do uvicorn no CMD
├── .dockerignore              # Exclui venv, testes, cache e arquivos de banco/planejamento da imagem
├── fly.toml                    # Configuração de build/deploy do Fly.io (Dockerfile, volume persistente, http service)
├── requirements.txt           # fastapi, uvicorn, sqlalchemy, pydantic, pytest, httpx, bcrypt, python-jose, python-multipart, alembic
└── README.md                  # Guia de execução e documentação
```

---

## 🚀 Deploy (Docker / Fly.io)

1. **Containerização**:
   - `Dockerfile` instala as dependências de `requirements.txt`, copia o pacote `app/` além de `alembic/` e `alembic.ini`, e no `CMD` executa `alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}` — todo início de container já aplica migrações pendentes antes de servir requisições.
   - `.dockerignore` mantém a imagem enxuta, excluindo `venv/`, testes, cache do pytest, banco local e arquivos de planejamento.
2. **Persistência de dados**:
   - `app/config.py` permite configurar o diretório de dados via `FINANCAS_DATA_DIR` (padrão: raiz do projeto), usado tanto para o arquivo SQLite (`financas.db`) quanto para o `.secret_key` do JWT.
   - `fly.toml` declara um volume persistente (`financas_data`) montado em `/data` e a variável `FINANCAS_DATA_DIR=/data`, garantindo que o banco e a chave JWT sobrevivam a novos deploys.
3. **Configuração no Fly.io**:
   - `fly.toml` define o build via Dockerfile, a região primária (`gru`), o `http_service` na porta interna 8000 e o mount do volume.
   - Antes do primeiro deploy, criar o volume com `fly volumes create financas_data --region gru --size 1`.
   - A CI (`.github/workflows/deploy.yml`) faz deploy com `flyctl deploy --remote-only`, autenticado via secret `FLY_API_TOKEN`.

---

## 🧪 Plano de Verificação e Testes

1. **Testes Automatizados**:
   - Rodar `pytest` cobrindo: cadastro, login, senha incorreta e token inválido/ausente; CRUD de categorias e transações; bloqueio de exclusão de categoria vinculada; filtros de data e tipo; cálculo de saldo e transações recentes; isolamento completo de dados entre usuários diferentes.
   - Recorrência de transações: geração correta de séries diárias/semanais/mensais (incluindo ajuste de dia em meses curtos), validação de Quantidade/Parcela obrigatórios e consistentes, edição de uma ocorrência sem afetar as demais da série, e os dois modos de exclusão (`only` e `following`).
2. **Testes de Interface e Navegação (Manual / Browser)**:
   - Iniciar o servidor FastAPI (`uvicorn app.main:app --reload --host 127.0.0.1 --port 8000`).
   - Testar fluxo completo de cadastro e login de novos usuários.
   - Testar via navegador em resolução desktop e mobile (viewport smartphone).
   - Validar responsividade do Bottom Menu, renderização dos gráficos (Chart.js) e transições entre telas.
   - Digitar valores no campo de valor e verificar a máscara `R$ 0,00`.
   - Selecionar data e verificar se o calendário fecha automaticamente.
   - Clicar no botão `Receita` do menu inferior e verificar pré-seleção como Receita.
   - Tentar excluir uma categoria vinculada a uma transação e conferir a mensagem de bloqueio.
   - Criar 2 usuários diferentes e confirmar que transações, categorias e saldos são 100% isolados.
   - Selecionar cada opção de Recorrência e verificar que Quantidade/Parcela habilitam/desabilitam corretamente e que Parcela nunca excede Quantidade; criar uma série e confirmar que todas as ocorrências aparecem na lista de Transações; abrir uma ocorrência para editar e confirmar que Recorrência/Quantidade/Parcela aparecem bloqueados; excluir uma ocorrência do meio da série com "esta e as seguintes" e confirmar que só as anteriores permanecem.
3. **Verificação de Deploy**:
   - `docker build -t financas .` e `docker run` local para validar a imagem antes do primeiro deploy.
   - Confirmar que o container roda `alembic upgrade head` no start (logs mostram a migração antes da linha do `uvicorn`) e que o schema do banco reflete a versão mais recente.
   - Após o deploy no Fly.io, confirmar que os dados (usuários, categorias, transações) sobrevivem a um novo deploy, validando o volume persistente em `FINANCAS_DATA_DIR`.
