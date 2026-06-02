#!/usr/bin/env python3
import argparse
import re
import sys
from pathlib import Path


REQUIRED_SECTIONS = [
    "GOAL",
    "CONTEXT",
    "CONSTRAINTS",
    "ORACLE",
    "DONE WHEN",
    "VERIFY",
    "ITERATION POLICY",
    "STOP RULES",
    "OUTPUT",
]

HARD_MAX_CHARS = 3999
RUNTIME_TARGET_CHARS = 3400
HEADING_RE = re.compile(r"^([A-Z][A-Z0-9 ]+):\s*$")
GOAL_COMMAND_RE = re.compile(r"^/goal(?:\s|$)")


def read_input(path: str | None) -> str:
    if path:
        return Path(path).read_text(encoding="utf-8")
    return sys.stdin.read()


def normalize_heading(value: str) -> str:
    return re.sub(r"\s+", " ", value.strip().upper())


def command_tail(text: str) -> str:
    stripped = text.lstrip()
    if not GOAL_COMMAND_RE.match(stripped):
        return stripped
    return stripped[len("/goal") :].lstrip()


def validate_goal_command(text: str) -> None:
    stripped = text.lstrip()
    if not GOAL_COMMAND_RE.match(stripped):
        raise ValueError("contract must start with /goal")

    tail = command_tail(text)
    if tail.startswith("-"):
        raise ValueError("goal objective starts with a flag-like token")


def find_sections(text: str) -> dict[str, list[str]]:
    sections: dict[str, list[str]] = {}
    current = None
    for line in text.splitlines():
        match = HEADING_RE.match(line.strip())
        if match:
            current = normalize_heading(match.group(1))
            sections.setdefault(current, [])
        elif current:
            sections[current].append(line)
    return sections


def validate_sections(sections: dict[str, list[str]]) -> None:
    for section in REQUIRED_SECTIONS:
        if section not in sections:
            raise ValueError(f"missing required section: {section}")
        if not any(line.strip() for line in sections[section]):
            raise ValueError(f"empty required section: {section}")


def validate_lengths(text: str, strict_runtime_target: bool) -> None:
    length = len(text)
    if length > HARD_MAX_CHARS:
        raise ValueError(f"contract exceeds hard max: chars={length} max={HARD_MAX_CHARS}")

    if strict_runtime_target and length > RUNTIME_TARGET_CHARS:
        raise ValueError(
            f"runtime objective exceeds target: chars={length} target={RUNTIME_TARGET_CHARS}"
        )


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate an agent goal contract.")
    parser.add_argument("path", nargs="?", help="Contract path. Reads stdin when omitted.")
    parser.add_argument(
        "--strict-runtime-target",
        action="store_true",
        help="Reject text above the default runtime target of 3400 chars.",
    )
    return parser.parse_args(argv)


def main(argv: list[str]) -> int:
    args = parse_args(argv)
    try:
        text = read_input(args.path)
        validate_goal_command(text)
        validate_lengths(text, args.strict_runtime_target)
        section_map = find_sections(text)
        validate_sections(section_map)
    except OSError as error:
        print(f"status=error message={error}", file=sys.stderr)
        return 1
    except ValueError as error:
        print(f"status=error message={error}", file=sys.stderr)
        return 1

    print(f"status=ok section_count={len(section_map)} chars={len(text)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
