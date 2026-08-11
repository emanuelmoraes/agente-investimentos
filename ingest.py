""" Ingestion script to build/update the Agno RAG Vector Database """

import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from agno.knowledge.embedder.google import GeminiEmbedder
from agno.vectordb.lancedb import LanceDb, SearchType
from agno.knowledge.pdf import PDFKnowledgeBase
from agno.knowledge.text import TextKnowledgeBase
from agno.knowledge.combined import CombinedKnowledgeBase


load_dotenv()

# Define Paths
DOCUMENTS_DIR = Path("data/documents")
LANCE_DB_DIR = "data/lancedb"
TABLE_NAME = "investimentos_knowledge"

# Initialize VectorDb and Embedder
vector_db = LanceDb(
    table_name=TABLE_NAME,
    uri=LANCE_DB_DIR,
    search_type=SearchType.vector,
    embedder=GeminiEmbedder()
)



def run_ingestion(recreate: bool = False):
    """
    Ingest documents from data/documents into LanceDb vector database.
    """
    if not DOCUMENTS_DIR.exists():
        DOCUMENTS_DIR.mkdir(parents=True, exist_ok=True)
        print(f"Diretório '{DOCUMENTS_DIR}' criado. Adicione arquivos PDF/TXT para vetorização.")
        return

    txt_files = list(DOCUMENTS_DIR.glob("*.txt")) + list(DOCUMENTS_DIR.glob("*.md"))
    pdf_files = list(DOCUMENTS_DIR.glob("*.pdf"))

    knowledge_bases = []

    if txt_files:
        print(f"Encontrados {len(txt_files)} arquivo(s) de texto: {[f.name for f in txt_files]}")
        txt_kb = TextKnowledgeBase(
            path=DOCUMENTS_DIR,
            formats=[".txt", ".md"],
            vector_db=vector_db
        )
        knowledge_bases.append(txt_kb)

    if pdf_files:
        print(f"Encontrados {len(pdf_files)} arquivo(s) PDF: {[f.name for f in pdf_files]}")
        pdf_kb = PDFKnowledgeBase(
            path=DOCUMENTS_DIR,
            vector_db=vector_db
        )
        knowledge_bases.append(pdf_kb)

    if not knowledge_bases:
        print(f"Nenhum arquivo (.txt, .md, .pdf) encontrado no diretório '{DOCUMENTS_DIR}'.")
        return

    if len(knowledge_bases) == 1:
        target_kb = knowledge_bases[0]
    else:
        target_kb = CombinedKnowledgeBase(
            sources=knowledge_bases,
            vector_db=vector_db
        )

    print(f"Iniciando indexação no LanceDb (recreate={recreate})...")
    target_kb.load(recreate=recreate)
    print("✨ Indexação concluída com sucesso! A base de conhecimento está pronta para uso.")


if __name__ == "__main__":
    recreate_flag = "--recreate" in sys.argv
    run_ingestion(recreate=recreate_flag)
