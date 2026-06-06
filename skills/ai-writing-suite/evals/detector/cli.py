"""Command-line entry: `python3 -m detector.cli <file>` (or `-` for stdin).

WHY a CLI: lets a human or a CI step run the detector on any draft without
importing the package. Prints the score band, classification, and flagged spans
grouped by type — the same view comms-polish surfaces in `detect` mode.

Run from the `evals/` directory:
    python3 -m detector.cli path/to/draft.md
    cat draft.md | python3 -m detector.cli -
"""

import sys

from .detector import analyze


def _read(arg):
    if arg == "-":
        return sys.stdin.read()
    with open(arg, "r", encoding="utf-8") as fh:
        return fh.read()


def main(argv=None):
    argv = argv if argv is not None else sys.argv[1:]
    if not argv:
        print("usage: python3 -m detector.cli <file|->", file=sys.stderr)
        return 2

    result = analyze(_read(argv[0]))
    print(f"Score:          {result['score']}/100  ({result['label']})")
    print(f"Classification: {result['classification']}  "
          f"(confidence: {result['confidence']})")
    print(f"Words:          {result['stats'].get('wordCount', 0)}")
    print(f"Distinct tells: {len(result['issues'])}")
    if result["issues"]:
        print("\nFlagged:")
        # Group by type so the output reads as a fix list, not a flat dump.
        by_type = {}
        for it in result["issues"]:
            by_type.setdefault(it["type"], []).append(it["text"])
        for typ in sorted(by_type):
            spans = ", ".join(by_type[typ][:8])
            more = "" if len(by_type[typ]) <= 8 else f" (+{len(by_type[typ]) - 8} more)"
            print(f"  [{typ}] {spans}{more}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
