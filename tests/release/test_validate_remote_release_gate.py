from __future__ import annotations

import importlib.util
import subprocess
import sys
from pathlib import Path


MODULE_PATH = Path(__file__).resolve().parents[2] / "scripts" / "release" / "validate_remote_release_gate.py"
SPEC = importlib.util.spec_from_file_location("validate_remote_release_gate", MODULE_PATH)
assert SPEC is not None
validator = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
sys.modules[SPEC.name] = validator
SPEC.loader.exec_module(validator)


def run(cmd: list[str], cwd: Path) -> None:
    subprocess.run(cmd, cwd=cwd, check=True)


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def init_repo(repo: Path, paths: dict[str, str]) -> None:
    run(["git", "init"], repo)
    run(["git", "config", "user.email", "test@example.com"], repo)
    run(["git", "config", "user.name", "Test User"], repo)
    for relative_path, text in paths.items():
        write(repo / relative_path, text)
    run(["git", "add", "."], repo)
    run(["git", "commit", "-m", "init"], repo)


def base_contract() -> dict:
    return {
        "contract_version": "0.1",
        "contract_id": "TEST",
        "created_at": "2026-06-15-18-28",
        "ultra_goal": "test goal",
        "goals": [{"id": "G1", "statement": "goal", "verification": "path"}],
        "non_goals": [{"id": "NG1", "statement": "non goal"}],
        "included_scope": [{"id": "INC1", "paths": ["src/rag/bootstrap.py"], "reason": "required"}],
        "excluded_scope": [{"id": "EXC1", "tracked_forbidden_globs": ["logs/**", "*.log"], "reason": "runtime"}],
        "gates": [
            {"id": "GATE-CONTRACT-SHAPE", "type": "contract_shape", "goal_ids": ["G1"]},
            {"id": "GATE-REQUIRED-PATHS", "type": "required_paths_exist", "goal_ids": ["G1"]},
            {"id": "GATE-FORBIDDEN-TRACKED", "type": "forbidden_tracked_absent", "goal_ids": ["G1"]},
            {
                "id": "GATE-FILE-CONTAINS",
                "type": "file_contains",
                "goal_ids": ["G1"],
                "files": {"src/rag/bootstrap.py": ["_resolve_persist_directory"]},
            },
            {
                "id": "GATE-NO-STALE",
                "type": "no_stale_text_patterns",
                "goal_ids": ["G1"],
                "paths": ["plans/doc.md"],
                "patterns": ["old/path.md"],
            },
            {
                "id": "GATE-HISTORY",
                "type": "required_subjects_in_history",
                "goal_ids": ["G1"],
                "subjects": [],
            },
        ],
    }


def result_by_id(results: list, gate_id: str):
    return next(result for result in results if result.gate_id == gate_id)


def test_validate_passes_for_clean_scope(tmp_path: Path) -> None:
    init_repo(
        tmp_path,
        {
            "src/rag/bootstrap.py": "def _resolve_persist_directory(): pass\n",
            "plans/doc.md": "new/path.md\n",
        },
    )

    results = validator.validate(base_contract(), tmp_path)

    assert all(result.passed for result in results)


def test_contract_shape_requires_gate_goal_links(tmp_path: Path) -> None:
    init_repo(
        tmp_path,
        {
            "src/rag/bootstrap.py": "def _resolve_persist_directory(): pass\n",
            "plans/doc.md": "new/path.md\n",
        },
    )
    contract = base_contract()
    contract["gates"][1].pop("goal_ids")

    results = validator.validate(contract, tmp_path)

    result = result_by_id(results, "GATE-CONTRACT-SHAPE")
    assert not result.passed
    assert "gates[1]: missing_or_empty_goal_ids" in result.details


def test_contract_shape_fails_unreferenced_goal(tmp_path: Path) -> None:
    init_repo(
        tmp_path,
        {
            "src/rag/bootstrap.py": "def _resolve_persist_directory(): pass\n",
            "plans/doc.md": "new/path.md\n",
        },
    )
    contract = base_contract()
    contract["goals"].append({"id": "G2", "statement": "extra", "verification": "none"})

    results = validator.validate(contract, tmp_path)

    result = result_by_id(results, "GATE-CONTRACT-SHAPE")
    assert not result.passed
    assert "unreferenced_goal:G2" in result.details


def test_required_path_must_be_tracked(tmp_path: Path) -> None:
    init_repo(
        tmp_path,
        {
            "plans/doc.md": "new/path.md\n",
        },
    )
    write(tmp_path / "src/rag/bootstrap.py", "def _resolve_persist_directory(): pass\n")

    results = validator.validate(base_contract(), tmp_path)

    result = result_by_id(results, "GATE-REQUIRED-PATHS")
    assert not result.passed
    assert result.message == "required paths exist but are not tracked"
    assert result.details == ["src/rag/bootstrap.py"]


def test_required_history_subject_fails_when_missing(tmp_path: Path) -> None:
    init_repo(
        tmp_path,
        {
            "src/rag/bootstrap.py": "def _resolve_persist_directory(): pass\n",
            "plans/doc.md": "new/path.md\n",
        },
    )
    contract = base_contract()
    contract["gates"][-1]["subjects"] = ["missing subject"]

    results = validator.validate(contract, tmp_path)

    result = result_by_id(results, "GATE-HISTORY")
    assert not result.passed
    assert result.details == ["missing subject"]


def test_file_marker_missing_fails(tmp_path: Path) -> None:
    init_repo(
        tmp_path,
        {
            "src/rag/bootstrap.py": "def other(): pass\n",
            "plans/doc.md": "new/path.md\n",
        },
    )

    results = validator.validate(base_contract(), tmp_path)

    result = result_by_id(results, "GATE-FILE-CONTAINS")
    assert not result.passed
    assert "src/rag/bootstrap.py: missing '_resolve_persist_directory'" in result.details


def test_forbidden_tracked_file_fails(tmp_path: Path) -> None:
    init_repo(
        tmp_path,
        {
            "src/rag/bootstrap.py": "def _resolve_persist_directory(): pass\n",
            "plans/doc.md": "new/path.md\n",
            "logs/run.log": "runtime\n",
        },
    )

    results = validator.validate(base_contract(), tmp_path)

    result = result_by_id(results, "GATE-FORBIDDEN-TRACKED")
    assert not result.passed
    assert "logs/run.log matches logs/**" in result.details


def test_stale_text_pattern_fails(tmp_path: Path) -> None:
    init_repo(
        tmp_path,
        {
            "src/rag/bootstrap.py": "def _resolve_persist_directory(): pass\n",
            "plans/doc.md": "old/path.md\n",
        },
    )

    results = validator.validate(base_contract(), tmp_path)

    result = result_by_id(results, "GATE-NO-STALE")
    assert not result.passed
    assert "plans/doc.md: contains 'old/path.md'" in result.details


def test_unknown_gate_type_fails(tmp_path: Path) -> None:
    init_repo(
        tmp_path,
        {
            "src/rag/bootstrap.py": "def _resolve_persist_directory(): pass\n",
            "plans/doc.md": "new/path.md\n",
        },
    )
    contract = base_contract()
    contract["gates"].append({"id": "GATE-UNKNOWN", "type": "not_a_gate", "goal_ids": ["G1"]})

    results = validator.validate(contract, tmp_path)

    result = result_by_id(results, "GATE-UNKNOWN")
    assert not result.passed
    assert result.message == "unknown gate type: not_a_gate"
