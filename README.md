# 📈 Agente de Gestão de Investimentos

Um agente virtual inteligente especializado em **análise de carteiras de investimentos, perfil de risco, cotações em tempo real e recomendações financeiras**, desenvolvido em **Python 3.11** utilizando o framework **Agno**, o modelo **Google Gemini 3.5 Flash**, interface gráfica web em **Gradio** e armazenamento em banco de dados **SQLite**.

---

## 🚀 Funcionalidades Principais

- **📚 Base de Conhecimento (RAG):** Consulta documentos internos (relatórios em PDF, arquivos de texto ou diretrizes em `data/documents/`) para fundamentar as respostas do agente.
- **🌐 Ferramentas em Tempo Real (Tools):**
  - **DuckDuckGo (`DuckDuckGoTools`):** Realiza buscas na internet sobre o mercado financeiro em tempo real sem necessidade de chave de API.
  - **Yahoo Finance (`YFinanceTools`):** Consulta cotações de ações/FIIs na B3 (com sufixo `.SA`) e no mercado internacional, notícias de empresas e recomendações de analistas.
- **🖼️ Interface Multimodal & Voz (Gradio):** Aceita envio de texto, anexos de arquivos, **colagem direta de imagens (Ctrl+V)** e **gravação de áudio pelo microfone**.
- **🔊 Síntese de Voz (TTS Neural):** Converte as respostas do agente em áudio falado em Português (`pt-BR-AntonioNeural` via `edge-tts`) com reprodução automática.
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

### 3. Ingestão de Documentos para RAG (Opcional)
Para alimentar o agente com relatórios, artigos ou carteiras recomendadas:
1. Coloque seus arquivos (`.pdf`, `.txt`, `.md`) no diretório `data/documents/`.
2. Execute o pipeline de vetorização para indexar no LanceDB:
   ```bash
   python ingest.py
   ```

---

## 📁 Estrutura do Projeto

```
agente-investimentos/
├── .env                     # Variáveis de ambiente e secrets (não versionado)
├── .gitignore               # Regras de exclusão do Git
├── app.py                   # Aplicação Web Gradio (Multimodal, Voz, Chat, Sessões)
├── main.py                  # Definição do Agente Agno (Tools, Gemini, Knowledge, CLI)
├── ingest.py                # Pipeline de ingestão/vetorização (LanceDB + Gemini Embedder)
├── requirements.txt         # Dependências Python do projeto
├── prompts/                 # Diretrizes e system prompts tipados do agente
│   ├── __init__.py
│   └── investment_agent.py
└── data/                    # Dados locais e runtime (ignorado pelo Git)
    ├── documents/           # Pasta de entrada para documentos RAG (PDF, TXT, MD)
    ├── lancedb/             # Vector Database gerado pelo ingest.py
    └── agent_storage.db     # Banco SQLite com sessões e histórico de conversas
```

---

## 📄 Licença

Este projeto está sob a licença MIT. Sinta-se livre para usar e modificar!

