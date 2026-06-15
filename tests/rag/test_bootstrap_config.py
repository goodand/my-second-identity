from unittest.mock import patch

from src.rag import bootstrap as bootstrap_module


def test_init_vectorstore_uses_config_default_path(monkeypatch):
    monkeypatch.delenv("MSI_CHROMA_PERSIST_DIRECTORY", raising=False)

    with (
        patch.object(bootstrap_module, "OpenAIEmbeddings") as embeddings_cls,
        patch.object(bootstrap_module, "Chroma") as chroma_cls,
    ):
        embeddings_cls.return_value = object()
        bootstrap_module.init_vectorstore()

    assert chroma_cls.call_args.kwargs["persist_directory"] == "local_chroma_db"


def test_init_vectorstore_uses_env_path_override(monkeypatch):
    monkeypatch.setenv("MSI_CHROMA_PERSIST_DIRECTORY", "/tmp/custom_chroma")

    with (
        patch.object(bootstrap_module, "OpenAIEmbeddings") as embeddings_cls,
        patch.object(bootstrap_module, "Chroma") as chroma_cls,
    ):
        embeddings_cls.return_value = object()
        bootstrap_module.init_vectorstore()

    assert chroma_cls.call_args.kwargs["persist_directory"] == "/tmp/custom_chroma"
