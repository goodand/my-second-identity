"""bootstrap.py — Chroma 벡터스토어를 graph.py에 주입하는 진입점."""
import os
import yaml
from pathlib import Path
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings

from src.rag.graph import configure_vectorstore

_CONFIG_PATH = Path(__file__).parent.parent.parent / "configs" / "rag.yaml"


def load_config() -> dict:
    with open(_CONFIG_PATH) as f:
        return yaml.safe_load(f)


def init_vectorstore() -> Chroma:
    cfg = load_config()
    vs_cfg = cfg["vector_store"]
    persist_directory = os.environ.get(
        vs_cfg.get("persist_directory_env", "MSI_CHROMA_PERSIST_DIRECTORY"),
        vs_cfg["persist_directory"],
    )
    embedding = OpenAIEmbeddings(model=vs_cfg["embedding_model"])
    store = Chroma(
        persist_directory=persist_directory,
        embedding_function=embedding,
    )
    return store


def bootstrap() -> None:
    """앱 시작 시 한 번 호출. 벡터스토어를 graph에 주입."""
    store = init_vectorstore()
    configure_vectorstore(korean_store=store)


if __name__ == "__main__":
    bootstrap()
    from src.rag.graph import graph
    result = graph.invoke({"user_query": "RAG 시스템이란 무엇인가?"})
    print(result["final_answer"])
