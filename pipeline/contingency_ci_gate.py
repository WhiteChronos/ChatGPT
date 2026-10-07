from __future__ import annotations

import argparse
from dataclasses import asdict, dataclass
import glob
import json
from pathlib import Path
import subprocess


@dataclass(frozen=True)
class GateCommand:
    name: str
    argv: tuple[str, ...]


@dataclass(frozen=True)
class GateCommandResult:
    name: str
    argv: tuple[str, ...]
    returncode: int
    stdout: str
    stderr: str


@dataclass(frozen=True)
class GateResult:
    profile: str
    passed: bool
    failed_command_index: int | None
    results: tuple[GateCommandResult, ...]


_PYTHON_GOVERNANCE = (
    GateCommand("pytest", ("python", "-m", "pytest", "-q")),
    GateCommand("engineering-compatibility", ("python", "pipeline/engineering_compatibility_gate.py")),
    GateCommand(
        "protocol-zero",
        ("python", "pipeline/protocol_zero_gate.py", "datasheet/projects/example-project.json"),
    ),
)
_BROKER = (
    GateCommand("broker", ("node", "--test", "plugins/subagent-broker/tests/*.test.mjs")),
)


def commands_for_profile(profile: str) -> tuple[GateCommand, ...]:
    if profile == "python-governance":
        return _PYTHON_GOVERNANCE
    if profile == "broker":
        return _BROKER
    if profile == "full-contingency":
        return _PYTHON_GOVERNANCE + _BROKER
    raise ValueError(f"unknown contingency profile: {profile}")


def _expanded_argv(repo_root: Path, argv: tuple[str, ...]) -> list[str]:
    expanded: list[str] = []
    for value in argv:
        if any(ch in value for ch in "*?["):
            matches = sorted(glob.glob(str(repo_root / value)))
            expanded.extend(str(Path(match).relative_to(repo_root)) for match in matches)
        else:
            expanded.append(value)
    return expanded


def run_profile(repo_root: Path, profile: str) -> GateResult:
    repo_root = Path(repo_root).resolve()
    results: list[GateCommandResult] = []
    for index, command in enumerate(commands_for_profile(profile)):
        argv = _expanded_argv(repo_root, command.argv)
        proc = subprocess.run(argv, cwd=repo_root, check=False, text=True, capture_output=True)
        results.append(
            GateCommandResult(
                name=command.name,
                argv=tuple(argv),
                returncode=proc.returncode,
                stdout=proc.stdout,
                stderr=proc.stderr,
            )
        )
        if proc.returncode != 0:
            return GateResult(profile, False, index, tuple(results))
    return GateResult(profile, True, None, tuple(results))


def _dry_run_payload(profile: str) -> dict[str, object]:
    return {
        "profile": profile,
        "dry_run": True,
        "commands": [
            {"name": c.name, "argv": list(c.argv)}
            for c in commands_for_profile(profile)
        ],
    }


def _result_payload(result: GateResult) -> dict[str, object]:
    return {
        "profile": result.profile,
        "dry_run": False,
        "passed": result.passed,
        "failed_command_index": result.failed_command_index,
        "results": [asdict(item) for item in result.results],
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--profile", required=True, choices=("python-governance", "broker", "full-contingency"))
    parser.add_argument("--repo-root", default=".")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    if args.dry_run:
        payload = _dry_run_payload(args.profile)
        print(json.dumps(payload, sort_keys=True) if args.json else payload)
        return 0
    result = run_profile(Path(args.repo_root), args.profile)
    payload = _result_payload(result)
    print(json.dumps(payload, sort_keys=True) if args.json else payload)
    return 0 if result.passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
