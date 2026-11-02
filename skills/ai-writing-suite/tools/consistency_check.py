#!/usr/bin/env python3
"""Thin CLI over `aiws.consistency`: list numeric self-contradictions in a document.

Run:  python3 tools/consistency_check.py <file>   (or - for stdin)
Exit 0 = nothing found, 1 = conflicts listed, 2 = usage error.
It reports and never edits; which number is right is the author's call.
"""
import os
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
_SUITE_ROOT = os.path.normpath(os.path.join(_HERE, ".."))
if _SUITE_ROOT not in sys.path:
    sys.path.insert(0, _SUITE_ROOT)

from aiws.consistency import check  # noqa: E402


def main(argv):
    if len(argv) != 1:
        print("usage: consistency_check.py <file|->", file=sys.stderr)
        return 2
    text = sys.stdin.read() if argv[0] == "-" else open(argv[0], encoding="utf-8").read()
    conflicts = check(text)
    for kind, detail in conflicts:
        print(f"[{kind}] {detail}")
    if not conflicts:
        print("No numeric conflicts found (judgment checks still apply: defined terms, lead promises).")
    return 1 if conflicts else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
