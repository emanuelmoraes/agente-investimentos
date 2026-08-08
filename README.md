# 📈 Agente de Gestão de Investimentos

Um agente virtual inteligente especializado em **análise de carteiras de investimentos, perfil de risco, cotações em tempo real e recomendações financeiras**, desenvolvido em **Python 3.11** utilizando o framework **Agno**, o modelo **Google Gemini 3.5 Flash**, interface gráfica web em **Gradio** e armazenamento em banco de dados **SQLite**.

---

## 🚀 Funcionalidades Principais

- **🤖 Inteligência Financeira (Agno + Gemini 3.5 Flash):** Análise personalizada considerando o perfil de risco do usuário (conservador, moderado, arrojado) e seus objetivos de investimento.
- **🌐 Ferramentas em Tempo Real (Tools):**
  - **DuckDuckGo (`DuckDuckGoTools`):** Realiza buscas na internet sobre o mercado financeiro em tempo real sem necessidade de chave de API.
  - **Yahoo Finance (`YFinanceTools`):** Consulta cotações de ações/FIIs na B3 (com sufixo `.SA`) e no mercado internacional, notícias de empresas e recomendações de analistas.
- **🖼️ Interface Multimodal (Gradio):** Aceita envio de texto, anexos de arquivos e **colagem direta de imagens da área de transferência (Ctrl+V)** para análise de prints de carteira ou relatórios.
- **🔐 Autenticação de Usuários & Logout:** Tela visual de login e botão de **Sair/Logout** para alternar contas com segurança.
- **💾 Memória Persistente Isolada por Usuário (SQLite):** Armazena o histórico no banco de dados (`data/agent_storage.db`), garantindo que cada usuário (`investimentos_<username>`) veja apenas suas próprias conversas.

---

## 🛠️ Tecnologias Utilizadas

- **Linguagem:** Python 3.11+
- **Framework de Agentes:** [Agno](https://github.com/agno-agi/agno) (v1.0+)
- **Modelo de IA:** Google Gemini (`gemini-3.5-flash` via `google-genai`)
- **Interface Gráfica:** [Gradio](https://gradio.app/) (v6.0+)
- **Banco de Dados:** SQLite (`agno.db.sqlite.SqliteDb`)
- **Ferramentas:** `duckduckgo-search`, `ddgs`, `yfinance`

---

## 📋 Pré-requisitos

1. **Python 3.11** instalado.
2. Uma chave de API da Google Gemini ([Google AI Studio](https://aistudio.google.com/)).

---

## ⚙️ Instalação e Configuração

1. **Clone o repositório:**
   ```bash
   git clone https://github.com/seu-usuario/agente-investimentos.git
   cd agente-investimentos
   ```

2. **Crie e ative o ambiente virtual (Virtual Environment):**
   ```bash
   # Windows
   python -m venv .venv
   .venv\Scripts\activate

   # Linux/macOS
   python3 -m venv .venv
   source .venv/bin/activate
   ```

3. **Instale as dependências:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure as variáveis de ambiente:**
   Crie um arquivo `.env` na raiz do projeto contendo a sua chave do Gemini:
   ```env
   GOOGLE_API_KEY=sua_chave_api_aqui
   ```

---

## 💻 Como Executar

### 1. Interface Web Gráfica (Gradio) — *Recomendado*
```bash
python app.py
```
Acesse no seu navegador: **[http://127.0.0.1:7860](http://127.0.0.1:7860)**

#### Credenciais de Teste:
| Usuário | Senha |
| :--- | :--- |
| `admin` | `admin123` |
| `investidor` | `investidor123` |

### 2. Interface via Linha de Comando (CLI)
```bash
python main.py
```

---

## 📁 Estrutura do Projeto

```
agente-investimentos/
├── .env                  # Chaves de API (não versionado)
├── .gitignore            # Regras de ignorar arquivos do Git
├── app.py                # Aplicação da Interface Web Gradio (Login, Logout, Chat)
├── main.py               # Configuração do Agente Agno (Tools, Gemini, SQLite)
├── requirements.txt      # Dependências do projeto Python
└── data/
    └── agent_storage.db  # Banco de dados SQLite contendo as sessões (gerado automaticamente)
```

---

## 📄 Licença

Este projeto está sob a licença MIT. Sinta-se livre para usar e modificar!
