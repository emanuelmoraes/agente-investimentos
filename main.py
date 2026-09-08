""" Agente para gestão de investimentos """

import os
from pathlib import Path
from dotenv import load_dotenv
from agno.agent import Agent
from agno.models.google import Gemini
from agno.db.sqlite import SqliteDb
from agno.tools.duckduckgo import DuckDuckGoTools
from agno.knowledge.embedder.google import GeminiEmbedder
from agno.vectordb.lancedb import LanceDb, SearchType
from agno.knowledge import Knowledge
from agno.tools.duckduckgo import DuckDuckGoTools
from agno.tools.yfinance import YFinanceTools

from prompts import (
    INVESTMENT_AGENT_DESCRIPTION,
    INVESTMENT_AGENT_INSTRUCTIONS,
)

load_dotenv()

class SafeDuckDuckGoTools(DuckDuckGoTools):
    """
    Subclasse de DuckDuckGoTools que trata exceções (ex: DDGSException quando 0 resultados são encontrados)
    retornando uma mensagem descritiva sem quebrar a execução do agente.
    """
    def web_search(self, query: str, max_results: int = 5) -> str:
        try:
            return super().web_search(query=query, max_results=max_results)
        except Exception as exc:
            return f"Nenhum resultado encontrado na busca web para: '{query}'."

    def search_news(self, query: str, max_results: int = 5) -> str:
        try:
            return super().search_news(query=query, max_results=max_results)
        except Exception as exc:
            return f"Nenhum resultado encontrado nas notícias web para: '{query}'."


# RAG Vector Knowledge Base configuration (LanceDb + GeminiEmbedder)
DOCUMENTS_DIR: Path = Path("data/documents")
LANCE_DB_DIR: str = "data/lancedb"
TABLE_NAME: str = "investimentos_knowledge"

if not DOCUMENTS_DIR.exists():
    DOCUMENTS_DIR.mkdir(parents=True, exist_ok=True)

vector_db: LanceDb = LanceDb(
    table_name=TABLE_NAME,
    uri=LANCE_DB_DIR,
    search_type=SearchType.vector,
    embedder=GeminiEmbedder()
)

knowledge_base: Knowledge = Knowledge(vector_db=vector_db)


storage = SqliteDb(db_file="data/agent_storage.db")

agente = Agent(
    name="Agente de Investimentos",
    description=INVESTMENT_AGENT_DESCRIPTION,
    instructions=INVESTMENT_AGENT_INSTRUCTIONS,
    model=Gemini("gemini-3.5-flash"),
    knowledge=knowledge_base,
    search_knowledge=True,
    tools=[
        SafeDuckDuckGoTools(),
        YFinanceTools(
            enable_stock_price=True,
            enable_company_info=True,
            enable_company_news=True,
            enable_analyst_recommendations=True
        )
    ],

    markdown=True,
    db=storage,
    session_id="investimentos",
    add_history_to_context=True,
    num_history_runs=500
)


if __name__ == "__main__":
    print("=" * 70)
    print("  Iniciado sessão de conversa com o agente de investimentos.")
    print("  Digite 'sair', 'exit' ou 'quit' para encerrar a conversa.")
    print("=" * 70)

    while True:
        try:
            user_input: str = input("\n[Você] > ").strip()
            if not user_input:
                continue
            if user_input.lower() in {"sair", "exit", "quit"}:
                print("Encerrando sessão. Até logo!")
                break

            print("\n[Agente ERP] > ", end="", flush=True)
            agente.print_response(user_input, stream=True, session_id="investimentos")
        except (KeyboardInterrupt, EOFError):
            print("\nSessão interrompida pelo usuário.")
            break
        except Exception as exc:
            print("Error executing query: %s", exc)
