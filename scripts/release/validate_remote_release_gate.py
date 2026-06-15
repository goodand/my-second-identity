#!/usr/bin/env python3
"""Validate the remote-release ultra-goal scope contract.

The validator is intentionally non-mutating. It reads a JSON contract, checks
the current repository tree and git index/history, and returns exit code 0 only
when all gates pass.
"""

from __future__ import annotations

import argparse
import fnmatch
import json
import subprocess
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any


REQUIRED_TOP_LEVEL_KEYS = {
    "contract_version",
    "contract_id",
    "created_at",
    "ultra_goal",
    "goals",
    "non_goals",
    "included_scope",
    "excluded_scope",
    "gates",
}


@dataclass
class CheckResult:
    gate_id: str
    status: str
    message: str
    details: list[str]

    @property
    def passed(self) -> bool:
        return self.status == "pass"


def load_contract(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as f:
        return json.load(f)


def repo_path(repo: Path, relative_path: str) -> Path:
    return repo / relative_path


def run_git(repo: Path, args: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", *args],
        cwd=repo,
        check=False,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )


def git_ls_files(repo: Path) -> list[str]:
    proc = run_git(repo, ["ls-files"])
    if proc.returncode != 0:
        raise RuntimeError(proc.stderr.strip() or "git ls-files failed")
    return [line.strip() for line in proc.stdout.splitlines() if line.strip()]


def git_log_subjects(repo: Path) -> list[str]:
    proc = run_git(repo, ["log", "--format=%s", "--max-count=300"])
    if proc.returncode != 0:
        raise RuntimeError(proc.stderr.strip() or "git log failed")
    return [line.strip() for line in proc.stdout.splitlines() if line.strip()]


def normalize_path(path: str) -> str:
    return path.replace("\\", "/").strip("/")


def matches_glob(path: str, pattern: str) -> bool:
    normalized_path = normalize_path(path)
    normalized_pattern = normalize_path(pattern)
    if fnmatch.fnmatchcase(normalized_path, normalized_pattern):
        return True
    if normalized_pattern.startswith("**/"):
        return fnmatch.fnmatchcase(normalized_path, normalized_pattern[3:])
    return False


def all_included_paths(contract: dict[str, Any]) -> list[str]:
    paths: list[str] = []
    for scope in contract.get("included_scope", []):
        paths.extend(scope.get("paths", []))
    return paths


def all_forbidden_globs(contract: dict[str, Any]) -> list[str]:
    globs: list[str] = []
    for scope in contract.get("excluded_scope", []):
        globs.extend(scope.get("tracked_forbidden_globs", []))
    return globs


def check_contract_shape(gate: dict[str, Any], contract: dict[str, Any], repo: Path) -> CheckResult:
    del repo
    missing = sorted(REQUIRED_TOP_LEVEL_KEYS - set(contract))
    empty_lists = [
        key
        for key in ("goals", "non_goals", "included_scope", "excluded_scope", "gates")
        if not isinstance(contract.get(key), list) or not contract.get(key)
    ]
    unnamed_items: list[str] = []
    for key in ("goals", "non_goals", "included_scope", "excluded_scope", "gates"):
        for idx, item in enumerate(contract.get(key, [])):
            if not isinstance(item, dict) or not item.get("id"):
                unnamed_items.append(f"{key}[{idx}]")
    details = missing + [f"empty_or_invalid:{key}" for key in empty_lists] + unnamed_items
    if details:
        return CheckResult(gate["id"], "fail", "contract shape is invalid", details)
    return CheckResult(gate["id"], "pass", "contract shape is valid", [])


def check_required_paths_exist(gate: dict[str, Any], contract: dict[str, Any], repo: Path) -> CheckResult:
    paths = gate.get("paths") or all_included_paths(contract)
    missing = [path for path in paths if not repo_path(repo, path).exists()]
    if missing:
        return CheckResult(gate["id"], "fail", "required paths are missing", missing)
    return CheckResult(gate["id"], "pass", f"{len(paths)} required paths exist", [])


def check_forbidden_tracked_absent(gate: dict[str, Any], contract: dict[str, Any], repo: Path) -> CheckResult:
    patterns = gate.get("tracked_forbidden_globs") or all_forbidden_globs(contract)
    tracked = git_ls_files(repo)
    violations = [
        f"{path} matches {pattern}"
        for path in tracked
        for pattern in patterns
        if matches_glob(path, pattern)
    ]
    if violations:
        return CheckResult(gate["id"], "fail", "forbidden tracked files found", violations)
    return CheckResult(gate["id"], "pass", f"no tracked files match {len(patterns)} forbidden globs", [])


def check_required_subjects_in_history(gate: dict[str, Any], contract: dict[str, Any], repo: Path) -> CheckResult:
    del contract
    subjects = gate.get("subjects", [])
    history = set(git_log_subjects(repo))
    missing = [subject for subject in subjects if subject not in history]
    if missing:
        return CheckResult(gate["id"], "fail", "required commit subjects are missing from history", missing)
    return CheckResult(gate["id"], "pass", f"{len(subjects)} required commit subjects found", [])


def check_file_contains(gate: dict[str, Any], contract: dict[str, Any], repo: Path) -> CheckResult:
    del contract
    files = gate.get("files", {})
    missing: list[str] = []
    for relative_path, needles in files.items():
        path = repo_path(repo, relative_path)
        if not path.exists():
            missing.append(f"{relative_path}: file missing")
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        for needle in needles:
            if needle not in text:
                missing.append(f"{relative_path}: missing {needle!r}")
    if missing:
        return CheckResult(gate["id"], "fail", "required file markers are missing", missing)
    return CheckResult(gate["id"], "pass", f"{len(files)} files contain required markers", [])


def check_no_stale_text_patterns(gate: dict[str, Any], contract: dict[str, Any], repo: Path) -> CheckResult:
    del contract
    paths = gate.get("paths", [])
    patterns = gate.get("patterns", [])
    hits: list[str] = []
    for relative_path in paths:
        path = repo_path(repo, relative_path)
        if not path.exists():
            hits.append(f"{relative_path}: file missing")
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        for pattern in patterns:
            if pattern in text:
                hits.append(f"{relative_path}: contains {pattern!r}")
    if hits:
        return CheckResult(gate["id"], "fail", "stale text patterns found", hits)
    return CheckResult(gate["id"], "pass", f"no stale patterns found in {len(paths)} files", [])


CHECKS = {
    "contract_shape": check_contract_shape,
    "required_paths_exist": check_required_paths_exist,
    "forbidden_tracked_absent": check_forbidden_tracked_absent,
    "required_subjects_in_history": check_required_subjects_in_history,
    "file_contains": check_file_contains,
    "no_stale_text_patterns": check_no_stale_text_patterns,
}


def validate(contract: dict[str, Any], repo: Path) -> list[CheckResult]:
    results: list[CheckResult] = []
    for gate in contract.get("gates", []):
        gate_type = gate.get("type")
        check = CHECKS.get(gate_type)
        if check is None:
            results.append(CheckResult(gate.get("id", "<missing-id>"), "fail", f"unknown gate type: {gate_type}", []))
            continue
        try:
            results.append(check(gate, contract, repo))
        except Exception as exc:  # pragma: no cover - defensive error surface
            results.append(CheckResult(gate.get("id", "<missing-id>"), "fail", str(exc), []))
    return results


def print_text(results: list[CheckResult]) -> None:
    for result in results:
        print(f"{result.status.upper()} {result.gate_id}: {result.message}")
        for detail in result.details:
            print(f"  - {detail}")
    failed = sum(1 for result in results if not result.passed)
    passed = len(results) - failed
    print(f"SUMMARY: {passed} passed, {failed} failed")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--contract", required=True, type=Path)
    parser.add_argument("--repo", default=Path("."), type=Path)
    parser.add_argument("--json", action="store_true", help="emit machine-readable JSON")
    args = parser.parse_args(argv)

    repo = args.repo.resolve()
    contract = load_contract(args.contract)
    results = validate(contract, repo)
    failed = [result for result in results if not result.passed]

    if args.json:
        payload = {
            "status": "fail" if failed else "pass",
            "results": [asdict(result) for result in results],
        }
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        print_text(results)

    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
