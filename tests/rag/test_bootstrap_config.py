from pathlib import Path
from unittest.mock import patch

from src.rag import bootstrap as bootstrap_module


def test_init_vectorstore_resolves_config_default_path_from_repo_root(monkeypatch):
    monkeypatch.delenv("MSI_CHROMA_PERSIST_DIRECTORY", raising=False)

    with (
        patch.object(bootstrap_module, "OpenAIEmbeddings") as embeddings_cls,
        patch.object(bootstrap_module, "Chroma") as chroma_cls,
    ):
        embeddings_cls.return_value = object()
        bootstrap_module.init_vectorstore()

    assert chroma_cls.call_args.kwargs["persist_directory"] == str(
        (bootstrap_module._PROJECT_ROOT / "local_chroma_db").resolve()
    )


def test_init_vectorstore_uses_absolute_env_path_override(monkeypatch):
    monkeypatch.setenv("MSI_CHROMA_PERSIST_DIRECTORY", "/tmp/custom_chroma")

    with (
        patch.object(bootstrap_module, "OpenAIEmbeddings") as embeddings_cls,
        patch.object(bootstrap_module, "Chroma") as chroma_cls,
    ):
        embeddings_cls.return_value = object()
        bootstrap_module.init_vectorstore()

    assert chroma_cls.call_args.kwargs["persist_directory"] == "/tmp/custom_chroma"


def test_relative_persist_directory_helper_is_repo_root_relative(monkeypatch):
    monkeypatch.delenv("MSI_CHROMA_PERSIST_DIRECTORY", raising=False)

    resolved = bootstrap_module._resolve_persist_directory(
        {
            "persist_directory": "nested/chroma",
            "persist_directory_env": "MSI_CHROMA_PERSIST_DIRECTORY",
        }
    )

    assert Path(resolved) == (bootstrap_module._PROJECT_ROOT / "nested/chroma").resolve()
