""" Ingestion script to build/update the Agno RAG Vector Database (Agno 3.x) """

import sys
from pathlib import Path
from dotenv import load_dotenv
from agno.knowledge import Knowledge
from agno.knowledge.embedder.google import GeminiEmbedder
from agno.vectordb.lancedb import LanceDb, SearchType

load_dotenv()

# Define Paths
DOCUMENTS_DIR: Path = Path("data/documents")
LANCE_DB_DIR: str = "data/lancedb"
TABLE_NAME: str = "investimentos_knowledge"

# Initialize VectorDb and Embedder
vector_db: LanceDb = LanceDb(
    table_name=TABLE_NAME,
    uri=LANCE_DB_DIR,
    search_type=SearchType.vector,
    embedder=GeminiEmbedder()
)

# Unified Knowledge Base in Agno 3.x
knowledge: Knowledge = Knowledge(vector_db=vector_db)


def run_ingestion(recreate: bool = False) -> None:
    """
    Ingest documents from data/documents into LanceDb vector database using Agno 3.x.
    """
    if not DOCUMENTS_DIR.exists():
        DOCUMENTS_DIR.mkdir(parents=True, exist_ok=True)
        print(f"Diretório '{DOCUMENTS_DIR}' criado. Adicione arquivos (.pdf, .txt, .md) para vetorização.")
        return

    doc_files: list[Path] = [
        f for f in DOCUMENTS_DIR.iterdir()
        if f.is_file() and f.suffix.lower() in {".pdf", ".txt", ".md", ".docx", ".csv"}
    ]

    if not doc_files:
        print(f"Nenhum arquivo de documento encontrado no diretório '{DOCUMENTS_DIR}'.")
        print("Formatos suportados: .pdf, .txt, .md, .docx, .csv")
        return

    print(f"Encontrados {len(doc_files)} arquivo(s) para ingestão: {[f.name for f in doc_files]}")

    if recreate:
        print("Limpando base vetorial anterior (--recreate)...")
        try:
            knowledge.remove_all_content()
        except Exception as exc:
            print(f"Aviso ao limpar base: {exc}")

    print(f"Iniciando indexação no LanceDb via Agno 3.x...")
    knowledge.insert(path=str(DOCUMENTS_DIR), upsert=True)
    print("Indexacao concluida com sucesso! A base de conhecimento esta pronta para uso.")


if __name__ == "__main__":
    recreate_flag: bool = "--recreate" in sys.argv
    run_ingestion(recreate=recreate_flag)
