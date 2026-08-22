# Plano de Implementação: Aplicativo de Finanças Pessoais Moderno e Responsivo

Aplicativo web completo de gestão financeira pessoal com interface responsiva mobile-first (desktop e smartphone), modo escuro elegante, backend em Python moderno (FastAPI + SQLite + SQLAlchemy / Pydantic) e frontend reativo e dinâmico com integração nativa, visualização por gráficos (Chart.js), animações e testes automatizados (pytest).

---

## 🏗️ Arquitetura e Tecnologias

1. **Backend (Python)**:
   - **FastAPI**: API REST rápida, moderna, com validação de dados via Pydantic e OpenAPI/Swagger automático.
   - **SQLite + SQLAlchemy**: Banco de dados relacional local leve, sem necessidade de servidores externos.
   - **Pytest + TestClient**: Suíte completa de testes unitários e de integração cobrindo transações, categorias, filtros e regras de negócio.
2. **Frontend**:
   - **Arquitetura SPA / Responsiva**: Single Page Application fluida com navegação sem recarregamento de página.
   - **Design & UI**: Vanilla CSS moderno com paleta escura sofisticada (Glassmorphism, gradientes suaves, cards elegantes, micro-interações).
   - **Gráficos**: **Chart.js** integrado (Gráfico de barras horizontal para Despesas vs Receitas na Home; Gráfico Donut de Despesas por Categoria).
   - **Ícones**: Lucide Icons modernos e seletor intuitivo de ícones/cores para categorias.
   - **Mobile-first Bottom Bar**: Menu fixo inferior estilizado para smartphones e adaptado para telas desktop.

---

## 📱 Telas & Funcionalidades

### 1. Tela Home
- **Card Resumo**:
  - Saldo Atual (com formatação monetária em R$ e destaque visual positivo/negativo).
  - Gráfico de barras horizontal comparativo de Receitas vs Despesas.
- **Transações Recentes**:
  - Lista de transações filtradas exclusivamente para hoje e até 3 dias anteriores (últimos 4 dias).
  - Cards detalhados com: descrição, tipo (despesa/receita com cores e badges), valor, categoria (com ícone e cor), data/hora.
  - Clique no card abre diretamente a tela de Edição de Transação.

### 2. Tela Todas as Transações
- **Filtros**:
  - Data inicial (padrão: 1º dia do mês atual) e Data final (padrão: último dia do mês atual) — formato YYYY-MM-DD.
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

### 4. Tela Nova / Editar Transação
- Campos:
  - Tipo: Despesa ou Receita
  - Descrição
  - Valor (formatação monetária)
  - Categoria (seleção dinâmica com visualização do ícone e cor)
  - Data e Hora
  - Repetir mensalmente (checkbox/toggle)
- Ações: Botão Salvar, Botão Excluir (quando em edição), Botão Cancelar/Voltar.

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
  - 🏷️ **Categorias**
  - ➕ **Novo** (atalho rápido para Nova Transação com modal/tela fluida)

---

## 📂 Estrutura do Projeto

```
financas-pessoais-antg-prompt/
├── app/
│   ├── __init__.py
│   ├── main.py              # Ponto de entrada FastAPI e montagem dos estáticos
│   ├── config.py            # Configurações do app
│   ├── database.py          # Conexão SQLite e SessionLocal com SQLAlchemy
│   ├── models.py            # Modelos do banco (Transaction, Category)
│   ├── schemas.py           # Schemas Pydantic de entrada e saída
│   ├── seed.py              # Categorias e dados iniciais para primeira execução
│   ├── routers/
│   │   ├── transactions.py  # Endpoints CRUD e filtros de transações
│   │   ├── categories.py    # Endpoints CRUD e agregadores de categorias
│   │   └── summary.py       # Endpoints de resumo da Home (saldo, barras, recentes)
│   └── static/
│       ├── index.html       # HTML semântico com todas as visualizações SPA
│       ├── css/
│       │   └── style.css    # Tema Dark moderno, Glassmorphism, responsividade perfeita
│       └── js/
│           ├── app.js       # Gerenciamento de estado, navegação e manipulação DOM
│           ├── api.js       # Camada de comunicação com endpoints FastAPI
│           └── charts.js    # Inicialização e renderização do Chart.js (Barras e Donut)
├── tests/
│   ├── __init__.py
│   ├── conftest.py          # Fixtures de banco de dados em memória para testes
│   ├── test_categories.py   # Testes dos endpoints de categorias
│   ├── test_transactions.py # Testes de criação, edição, filtros e repetição mensal
│   └── test_summary.py      # Testes das métricas da Home e saldo
├── requirements.txt         # fastapi, uvicorn, sqlalchemy, pydantic, pytest, httpx
└── README.md                # Guia de execução e documentação
```

---

## 🧪 Plano de Verificação e Testes

1. **Testes Automatizados**:
   - Rodar `pytest` cobrindo todos os fluxos de criação de categoria, transações, filtros de data, filtro por tipo (despesa/receita), cálculo de saldo e transações recentes de 3 dias.
2. **Testes de Interface e Navegação**:
   - Iniciar o servidor FastAPI (`uvicorn app.main:app --port 8000`).
   - Testar via navegador em resolução desktop e mobile (viewport smartphone).
   - Validar responsividade do Bottom Menu, renderização dos gráficos (Chart.js) e transições entre telas.
