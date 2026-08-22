# 💰 Aplicativo de Finanças Pessoais

Aplicativo web completo de finanças pessoais desenvolvido com **Python moderno (FastAPI)**, banco de dados local **SQLite**, **Tema Escuro nativo**, design responsivo (*mobile-first* e desktop), gráficos interativos com **Chart.js** e suíte completa de testes automatizados com **pytest**.

---

## 🚀 Funcionalidades

1. **🏠 Tela Home**:
   - Card com **Saldo Atual** e indicador dinâmico.
   - **Gráfico de barras horizontal** comparativo de *Despesas vs Receitas*.
   - **Lista de transações recentes**: exibe automaticamente apenas as transações de hoje e dos últimos 3 dias.
   - Clique em qualquer transação para editar rapidamente.

2. **📊 Tela Todas as Transações**:
   - Filtro de datas com valor padrão (do primeiro ao último dia do mês atual).
   - Botões interativos para alternar entre **Todas**, **Despesas** ou **Receitas**.
   - Cards com descrição, tipo, categoria com ícone e cor, valor e data/hora.
   - Clique no card abre em modo de edição.

3. **🏷️ Tela Categorias**:
   - Filtro por período (padrão: mês atual).
   - **Gráfico em Donut** interativo mostrando o percentual e valor de despesas por categoria no período.
   - Cards de categorias com ícone, cor personalizada, nome e total gasto no período.
   - Criação de novas categorias e edição com seletor visual de ícones e paleta de cores.

4. **➕ Telas de Nova/Editar Transação**:
   - Formulário completo: tipo (despesa/receita), descrição, valor, seleção de categoria, data, hora e repetição mensal.
   - Botão para salvar, cancelar e excluir transações existentes.

5. **🎨 Telas de Nova/Editar Categoria**:
   - Nome da categoria, grid seletor de ícones modernos e paleta de cores predefinidas.

6. **📱 Menu Fixo Inferior (Bottom Bar)**:
   - Acesso rápido para **Home**, **Transações**, **Novo (+)** e **Categorias**.

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

Acesse no seu navegador: **[http://127.0.0.1:8000](http://127.0.0.1:8000)** ou abra no seu smartphone conectado à rede local.

---

## 🧪 Estrutura de Testes
O projeto inclui testes automatizados para:
- Criação, edição, exclusão e validação de duplicidade de categorias.
- Registro, atualização, exclusão e filtros avançados de transações por data e tipo.
- Cálculo de saldo consolidado e filtro de transações recentes na tela Home.
