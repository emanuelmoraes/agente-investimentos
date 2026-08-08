""" Agente para gestão de investimentos """

from agno.agent import Agent
from agno.models.google import Gemini
import os
from dotenv import load_dotenv
from agno.db.sqlite import SqliteDb
from agno.tools.duckduckgo import DuckDuckGoTools
from agno.tools.yfinance import YFinanceTools

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


storage = SqliteDb(db_file="data/agent_storage.db")

agente = Agent(
    name="Agente de Investimentos",
    description="Agente para gestão de investimentos",
    instructions="""
    Você é um agente especializado em investimentos.
    Seu objetivo é analisar as carteiras de ações dos usuários e fornecer recomendações de investimento.
    Você deve considerar:
    - Perfil de risco do usuário (conservador, moderado, arrojado)
    - Objetivos do investimento (curto prazo, médio prazo, longo prazo)
    - Tipo de investimento (ações, renda fixa, fundos, etc)
    - Diversificação da carteira
    - Rentabilidade histórica
    - Risco associado
    Use as ferramentas de busca web (DuckDuckGo) e de dados financeiros (YFinance) para buscar dados atualizados do mercado e cotações de ações em tempo real sempre que solicitado ou relevante.
    Para ações/FIIs brasileiros no YFinance, adicione o sufixo '.SA' ao ticker (ex: BBIG11.SA, PETR4.SA).
    """,
    model=Gemini("gemini-3.5-flash"),
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

