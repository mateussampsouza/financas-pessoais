# 💰 Aplicativo de Finanças Pessoais

Aplicativo web completo de finanças pessoais desenvolvido com **Python moderno (FastAPI)**, banco de dados local **SQLite**, **autenticação de usuários (JWT)**, **isolamento multi-tenant de dados**, **Tema Escuro nativo**, design responsivo (*mobile-first* e desktop), gráficos interativos com **Chart.js** e suíte completa de testes automatizados com **pytest**.

---

## 🚀 Funcionalidades

1. **🔐 Autenticação de Usuários**:
   - Tela de Login / Cadastro com design moderno (dark/glassmorphism).
   - Sessão via token JWT, persistida em `localStorage`.
   - Cada usuário só enxerga suas próprias categorias e transações (multi-tenant).
   - Categorias padrão criadas automaticamente para cada novo usuário no cadastro.
   - Cabeçalho com nome do usuário logado e botão de Sair.

2. **🏠 Tela Home**:
   - Card com **Saldo Atual** e indicador dinâmico.
   - **Gráfico de barras horizontal** comparativo de *Despesas vs Receitas*.
   - **Lista de transações recentes**: exibe automaticamente apenas as transações de hoje e dos últimos 3 dias.
   - Clique em qualquer transação para editar rapidamente.

3. **📊 Tela Todas as Transações**:
   - Filtro de datas com valor padrão (do primeiro ao último dia do mês atual). O seletor de data fecha automaticamente assim que uma data é escolhida.
   - Botões interativos para alternar entre **Todas**, **Despesas** ou **Receitas**.
   - Cards com descrição, tipo, categoria com ícone e cor, valor e data/hora.
   - Clique no card abre em modo de edição.

4. **🏷️ Tela Categorias**:
   - Filtro por período (padrão: mês atual).
   - **Gráfico em Donut** interativo mostrando o percentual e valor de despesas por categoria no período.
   - Cards de categorias com ícone, cor personalizada, nome e total gasto no período.
   - Criação de novas categorias e edição com seletor visual de ícones e paleta de cores.
   - Categorias com transações vinculadas não podem ser excluídas — o app exibe um aviso amigável explicando o motivo.

5. **➕ Telas de Nova/Editar Transação**:
   - Formulário completo: tipo (despesa/receita), descrição, valor (com máscara monetária em tempo real, ex: `R$ 1.250,50`), seleção de categoria, data, hora e repetição mensal.
   - Botão para salvar, cancelar e excluir transações existentes.

6. **🎨 Telas de Nova/Editar Categoria**:
   - Nome da categoria, grid seletor de ícones modernos e paleta de cores predefinidas.

7. **📱 Menu Fixo Inferior (Bottom Bar)**:
   - Acesso rápido para **Home**, **Transações**, **Novo (+)**, **Categorias** e **Receita** (atalho que já abre o formulário de nova transação com o tipo Receita pré-selecionado e travado).

---

## 🛠️ Como Executar

### 1. Pré-requisitos
- Python 3.9+ instalado

### 2. Configurar o Ambiente Virtual e Instalar Dependências
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 3. Rodar os Testes Automatizados
```bash
pytest
```

### 4. Iniciar a Aplicação
```bash
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Acesse no seu navegador: **[http://127.0.0.1:8000](http://127.0.0.1:8000)** ou abra no seu smartphone conectado à rede local. Na primeira vez, crie uma conta na aba "Cadastrar".

> **Sobre o `financas.db`**: como este app agora exige um usuário dono de cada categoria/transação, o banco de dados antigo (sem essa coluna) precisou ser recriado do zero. Se você tinha dados de teste no `financas.db` anterior, eles não foram migrados.

> **Chave de segurança do JWT**: por padrão, uma chave é gerada automaticamente e salva em `.secret_key` na primeira execução (não versionado no git). Para definir a sua própria, exporte a variável de ambiente `FINANCAS_SECRET_KEY` antes de iniciar o servidor.

---

## 🧪 Estrutura de Testes
O projeto inclui testes automatizados para:
- Cadastro, login, validação de senha incorreta e de token inválido/ausente.
- Criação, edição, exclusão e validação de duplicidade de categorias.
- Bloqueio de exclusão de categorias com transações vinculadas.
- Registro, atualização, exclusão e filtros avançados de transações por data e tipo.
- Cálculo de saldo consolidado e filtro de transações recentes na tela Home.
- Isolamento completo de dados entre usuários diferentes (categorias, transações e resumo).
