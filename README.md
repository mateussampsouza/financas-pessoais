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
   - Card fixo (sticky) ao final da lista com o **total do período** filtrado (receitas somam, despesas subtraem).

4. **🏷️ Tela Categorias**:
   - Filtro por período (padrão: mês atual).
   - **Gráfico em Donut** interativo mostrando o percentual e valor de despesas por categoria no período, com o **total de despesas** do período exibido logo abaixo do gráfico.
   - Cards de categorias com ícone, cor personalizada, nome e total gasto/recebido no período — despesas em vermelho com sinal de menos, receitas em verde sem sinal; categorias com movimentação de ambos os tipos mostram os dois valores.
   - Criação de novas categorias e edição com seletor visual de ícones e paleta de cores.
   - Categorias com transações vinculadas não podem ser excluídas — o app exibe um aviso amigável explicando o motivo.

5. **➕ Telas de Nova/Editar Transação**:
   - Formulário completo: tipo (despesa/receita), descrição, valor (com máscara monetária em tempo real, ex: `R$ 1.250,50`), seleção de categoria, data, hora e recorrência.
   - **Recorrência configurável**: campo "Recorrência" (Nunca, Diária, Semanal, Mensal, Anual) + "Quantidade" (total de ocorrências da série, 1-99) + "Parcela" (posição da transação atual dentro da série, sempre ≤ Quantidade). Ao salvar, o app gera de uma vez todas as ocorrências passadas e futuras da série (mesma descrição, tipo, valor, categoria e hora — só a data muda).
   - Recorrência, Quantidade e Parcela ficam **bloqueados na edição**: alterar uma ocorrência nunca reflete nas demais da série.
   - Ao excluir uma transação recorrente, um diálogo pergunta se a exclusão deve afetar **somente aquela ocorrência** ou **ela e todas as seguintes** da série.
   - Botão para salvar, cancelar e excluir transações existentes.

6. **🎨 Telas de Nova/Editar Categoria**:
   - Nome da categoria, grid seletor de ícones modernos e paleta de cores predefinidas.

7. **📱 Menu Fixo Inferior (Bottom Bar)**:
   - Acesso rápido para **Home**, **Transações**, **Novo (+)**, **Categorias** e **Receita** (atalho que já abre o formulário de nova transação com o tipo Receita pré-selecionado e travado).

---

## 🛠️ Como Executar

### 1. Pré-requisitos
- Python 3.14+ instalado

### 2. Configurar o Ambiente Virtual e Instalar Dependências
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements-dev.txt   # inclui requirements.txt + ferramentas de teste/lint
```
Para instalar apenas as dependências de produção (sem pytest/ruff), use `pip install -r requirements.txt`.

### 3. Rodar os Testes Automatizados e o Lint
```bash
pytest
ruff check .
```

### 4. Iniciar a Aplicação
```bash
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Acesse no seu navegador: **[http://127.0.0.1:8000](http://127.0.0.1:8000)** ou abra no seu smartphone conectado à rede local. Na primeira vez, crie uma conta na aba "Cadastrar".

> **Sobre o `financas.db`**: como este app agora exige um usuário dono de cada categoria/transação, o banco de dados antigo (sem essa coluna) precisou ser recriado do zero. Se você tinha dados de teste no `financas.db` anterior, eles não foram migrados.

> **Chave de segurança do JWT**: por padrão, uma chave é gerada automaticamente e salva em `.secret_key` na primeira execução (não versionado no git). Para definir a sua própria, exporte a variável de ambiente `FINANCAS_SECRET_KEY` antes de iniciar o servidor.

> **⚠️ Persistência em produção (Fly.io)**: tanto o `financas.db` quanto o `.secret_key` são gravados em `FINANCAS_DATA_DIR` (`/data` no Docker). O `fly.toml` já declara um **Volume persistente** (`financas_data`) montado em `/data`; sem ele, cada novo deploy apaga o banco de dados inteiro e gera uma nova chave JWT (o que desloga todos os usuários). Confirme com `fly volumes list` que o volume existe e está anexado à app antes de considerar o ambiente de produção confiável.

---

## 🐳 Como Executar com Docker

O projeto já inclui um `Dockerfile` pronto para produção (imagem baseada em `python:3.14-slim`, roda como usuário não-root).

A imagem já inclui `alembic/` e `alembic.ini`, e o `CMD` executa `alembic upgrade head` antes de iniciar o `uvicorn` — qualquer container novo (local ou em produção) já sobe com o schema do banco atualizado, sem passo manual.

### 1. Build da Imagem
```bash
docker build -t financas-pessoais .
```

### 2. Rodar o Container
```bash
docker run -d \
  --name financas-pessoais \
  -p 8000:8000 \
  -v financas_data:/data \
  -e FINANCAS_SECRET_KEY=troque-por-uma-chave-secreta \
  financas-pessoais
```
- `-v financas_data:/data` cria um **volume nomeado** para persistir `financas.db` e `.secret_key` entre reinícios/recriações do container — sem ele, os dados são perdidos a cada novo `docker run`/`docker build`.
- `-e FINANCAS_SECRET_KEY=...` é opcional, mas recomendado em produção (caso omitido, uma chave é gerada automaticamente dentro do volume na primeira execução).
- O container respeita a variável `PORT` (usada pelo Fly.io); localmente, sem defini-la, o Uvicorn sobe na porta `8000`.

Acesse em **[http://127.0.0.1:8000](http://127.0.0.1:8000)**.

### 3. Parar e Remover
```bash
docker stop financas-pessoais && docker rm financas-pessoais
```

---

## 🔄 Migrações de Banco de Dados (Alembic)

O projeto usa [Alembic](https://alembic.sqlalchemy.org/) para versionar mudanças no schema do banco. A aplicação continua criando tabelas automaticamente na primeira execução (`Base.metadata.create_all`), mas qualquer alteração de schema **a partir de agora** deve ser feita via migração, não editando `models.py` e recriando o banco do zero.

> **Em Docker/produção (Fly.io) isso já é automático**: o `CMD` do `Dockerfile` roda `alembic upgrade head` antes do `uvicorn` a cada início do container, então um novo deploy já aplica as migrações pendentes no volume persistente sem intervenção manual. **Em desenvolvimento local** (`uvicorn` executado diretamente, fora do Docker), nada dispara a migração automaticamente — rode `alembic upgrade head` você mesmo depois de puxar uma alteração de schema.

**Criar uma nova migração após alterar `app/models.py`:**
```bash
alembic revision --autogenerate -m "descrição da mudança"
alembic upgrade head
```

**Aplicar migrações pendentes em um ambiente existente:**
```bash
alembic upgrade head
```

> Se você já tem um `financas.db` criado antes da introdução do Alembic (schema já no formato atual, sem histórico de migração), rode uma vez `alembic stamp head` nesse banco para marcá-lo como atualizado, sem tentar recriar as tabelas.

---

## 🧪 Estrutura de Testes
O projeto inclui testes automatizados para:
- Cadastro, login, validação de senha incorreta e de token inválido/ausente.
- Criação, edição, exclusão e validação de duplicidade de categorias.
- Bloqueio de exclusão de categorias com transações vinculadas.
- Registro, atualização, exclusão e filtros avançados de transações por data e tipo.
- Geração de séries recorrentes (diária, semanal, mensal) com posicionamento correto de passado/futuro via Quantidade/Parcela, validação dos dois campos, edição que não afeta as demais ocorrências e os dois modos de exclusão (`only` / `following`).
- Cálculo de saldo consolidado e filtro de transações recentes na tela Home.
- Isolamento completo de dados entre usuários diferentes (categorias, transações e resumo).

---

## 🚢 CI/CD com GitHub Actions + Fly.io

O workflow em [`.github/workflows/deploy.yml`](.github/workflows/deploy.yml) automatiza testes e deploy a cada alteração no repositório:

1. **Job `test`** (roda em todo `push` e `pull request` para `main`):
   - Instala as dependências de `requirements-dev.txt`.
   - Executa `ruff check .` (lint) e `pytest` (suíte de testes).
2. **Job `deploy`** (roda apenas em `push` para `main`, e só depois que o job `test` passar):
   - Usa `superfly/flyctl-actions` para instalar o `flyctl`.
   - Executa `flyctl deploy --remote-only`, que faz o build da imagem Docker remotamente na infraestrutura da Fly.io e atualiza a aplicação, usando o `fly.toml` do repositório.

Ou seja: **Pull Requests só rodam testes** (nada é publicado), e **apenas um merge/push em `main` com os testes passando** dispara o deploy real em produção.

### Configurar o Secret `FLY_API_TOKEN`
O job de deploy depende de um token de API da Fly.io configurado como secret do repositório:

1. Gere um token: `fly tokens create deploy` (ou `fly auth token`, com o [flyctl](https://fly.io/docs/flyctl/) instalado e autenticado).
2. No GitHub, acesse **Settings → Secrets and variables → Actions → New repository secret**.
3. Nome: `FLY_API_TOKEN`. Valor: o token gerado no passo 1.

Sem esse secret configurado, o job `deploy` falha na etapa de autenticação com a Fly.io.

### Deploy manual (sem esperar o CI)
Com o [flyctl](https://fly.io/docs/flyctl/) instalado e autenticado localmente:
```bash
fly deploy --remote-only
```
