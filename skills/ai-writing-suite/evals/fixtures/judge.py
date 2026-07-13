"""Optional LLM-judge for the before/after fixtures (Phase 2a wire-in).

DEV-ONLY + OPT-IN. This module is the ONLY place the eval can talk to a model.
It is never imported at module load and never reached by the deterministic CI
path: `run_all.sh` runs `python3 -m fixtures.run_fixtures` (no `--judge`) with no
key, so CI stays Python-3-stdlib-only and green. This module uses only the stdlib
(`urllib` + `json` + `os`) — wiring a judge adds NO pip line to CI.

Honesty stance (inherited from run_fixtures.run_judge): we NEVER fabricate a
verdict. If the judge is not configured, the caller SKIPs.

Three-state gate (`score()`):
  1. NOT configured (any of URL/MODEL/KEY missing, or AIWS_JUDGE_RUN != "1")
     -> return None  ->  caller SKIPs (process exits 0; the offline honesty path).
  2. configured + opted in
     -> ONE HTTP POST; return the model's raw text.
  3. configured but the call fails (transport / auth / HTTP 4xx-5xx)
     -> raise JudgeError (LOUD; the caller exits nonzero). An auth failure must
        NOT be laundered into a SKIP (CLAUDE.md: "FAIL LOUDLY if config and
        runtime disagree").

Provider is PURELY env-driven — NO baked-in vendor — to keep the
host-provides-the-model philosophy and avoid a second-vendor dependency:

  AIWS_JUDGE_URL    full chat/completions endpoint URL (e.g. an OpenAI-compatible
                    .../v1/chat/completions)
  AIWS_JUDGE_MODEL  model id to send
  AIWS_JUDGE_KEY    the API key (read once, sent as a Bearer header, never logged)
  AIWS_JUDGE_RUN    must be "1" to actually spend — a stray key in the env alone
                    will NOT trigger a billed call.

  AIWS_REWRITER_MODEL  OPTIONAL. The model id that produced the `after` rewrites.
                    Purely advisory: when set AND it shares a model family with
                    AIWS_JUDGE_MODEL, score() prints a ONE-LINE self-preference
                    warning to stderr (once per run). Never gates, never blocks,
                    never a required var — leaving it unset just skips the check.

Cross-family note: if your rewrites come from Claude, point AIWS_JUDGE_MODEL at a
different model family to avoid judge self-preference (~10-25% PASS inflation).
For v1 the fixtures' `after` strings are hand-written (not model output), so this
is a recommendation, not a hard requirement — see evals/README.md. When the host
DOES wire a rewriter model, set AIWS_REWRITER_MODEL and the same-family check
(model_family / same_family_warning below) surfaces the risk automatically.
"""

import json
import os
import re
import sys
import urllib.error
import urllib.request

# no_fabrication is ALWAYS required for an overall PASS, even when a fixture's
# rubric_focus does not list it (rubric.md: "Verdict aggregation"). This is the
# single load-bearing asymmetry the judge exists to enforce.
ALWAYS_REQUIRED = "no_fabrication"

# One attempt, generous timeout. No retry/backoff in v1 — retry logic is the part
# a minimal-debugger owner can't maintain, and a clean loud failure is better than
# silent flakiness (the liveness check in run_judge surfaces a dead provider).
_TIMEOUT_S = 60

# Matches a NORMALIZED rubric line: "<snake_case_dim>: PASS|FAIL|N/A [— reason]".
# Leading list markers / **bold** are stripped before matching (see parse below),
# so common model formatting ("- **meaning_preserved**: PASS") still parses. N/A is
# a third state for conditional dims (e.g. payoff_clear when no removal happened);
# aggregate() treats it as vacuously satisfied. "N/A" is tried before "NA".
_DIM_LINE = re.compile(r"^([a-z][a-z_]+)\s*:\s*(PASS|FAIL|N/A|NA)\b", re.IGNORECASE)

# The quoted-evidence segment the rubric now asks each verdict to carry:
#   "<dim>: PASS|FAIL — <reason> | EVIDENCE: \"<verbatim quote>\"".
# Tolerant of straight and smart quotes. Non-greedy to the first closing quote —
# good enough for an advisory surface (an embedded quote just truncates the shown
# snippet, it never changes a verdict). Matched against the RAW line, not the
# bullet-cleaned one, so evidence text keeps its own punctuation/asterisks.
_EVIDENCE_RE = re.compile(r"""EVIDENCE\s*:\s*["“'‘](.+?)["”'’]""", re.IGNORECASE)

# Coarse model_id -> vendor "family" map for the judge self-preference check.
# Longest/most-specific prefixes are fine here because none overlap. o-series
# reasoning models (o1/o3/o4) fold into openai — self-preference is a vendor-level
# concern, not a per-model one. Anything unrecognized -> "unknown" (never warned
# on, so a new provider degrades to silence, not a false alarm).
_FAMILY_PREFIXES = (
    ("claude", "anthropic"),
    ("gpt", "openai"),
    ("o1", "openai"),
    ("o3", "openai"),
    ("o4", "openai"),
    ("gemini", "google"),
    ("gemma", "google"),
    ("llama", "meta"),
    ("mixtral", "mistral"),
    ("mistral", "mistral"),
    ("deepseek", "deepseek"),
    ("qwen", "qwen"),
    ("grok", "xai"),
)

# Fire the same-family warning at most once per process (score() runs per fixture).
_FAMILY_WARNING_EMITTED = False


class JudgeError(RuntimeError):
    """Transport/auth/HTTP failure — must reach the user loudly, never a SKIP."""


def is_configured():
    """True only when fully configured AND explicitly opted in to spend.

    Requiring AIWS_JUDGE_RUN=="1" on top of the credentials means a stray
    API key already in the environment cannot, by itself, trigger a billed call.
    """
    return bool(os.environ.get("AIWS_JUDGE_URL")
                and os.environ.get("AIWS_JUDGE_MODEL")
                and os.environ.get("AIWS_JUDGE_KEY")
                and os.environ.get("AIWS_JUDGE_RUN") == "1")


def score(prompt):
    """Return the model's raw text for `prompt`, or None if not configured.

    State 1 (not configured) -> None (caller SKIPs).
    State 2 (configured)     -> one POST, return raw text (or None if the 200
                               response carries no extractable text — the caller
                               treats that as unparseable and the liveness check
                               in run_judge turns a whole-suite failure loud).
    State 3 (call fails)     -> raise JudgeError.
    """
    if not is_configured():
        return None  # honesty stance: no fabrication, caller SKIPs

    _maybe_warn_same_family()  # advisory stderr note; never blocks the call

    url = os.environ["AIWS_JUDGE_URL"]
    model = os.environ["AIWS_JUDGE_MODEL"]
    key = os.environ["AIWS_JUDGE_KEY"]

    body = json.dumps({
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0,
    }).encode("utf-8")

    req = urllib.request.Request(url, data=body, method="POST")
    req.add_header("Content-Type", "application/json")
    req.add_header("Authorization", f"Bearer {key}")  # never logged/printed

    try:
        with urllib.request.urlopen(req, timeout=_TIMEOUT_S) as resp:
            payload = json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        # 401/403/429/5xx etc. Surface the status, never the key. Loud, not SKIP.
        raise JudgeError(
            f"judge HTTP {e.code} from provider — check "
            f"AIWS_JUDGE_URL / AIWS_JUDGE_KEY / AIWS_JUDGE_MODEL") from None
    except (urllib.error.URLError, TimeoutError, OSError) as e:
        raise JudgeError(f"judge transport error: {e}") from None

    return _extract_text(payload)


def _extract_text(payload):
    """Pull assistant text out of a provider response envelope, tolerantly.

    Handles the two common shapes (OpenAI chat-completions, Anthropic messages)
    plus a couple of fallbacks. Returns None if no text is found — run_judge's
    liveness check turns an all-None run (with a key present) into a loud nonzero
    exit ("provider envelope likely changed"), so a silent shape drift can't
    masquerade as 'all SKIPPED'.
    """
    if not isinstance(payload, dict):
        return None
    # OpenAI-style: choices[0].message.content
    choices = payload.get("choices")
    if isinstance(choices, list) and choices:
        msg = choices[0].get("message") if isinstance(choices[0], dict) else None
        if isinstance(msg, dict) and isinstance(msg.get("content"), str):
            return msg["content"]
        # some completion APIs put text directly on the choice
        if isinstance(choices[0], dict) and isinstance(choices[0].get("text"), str):
            return choices[0]["text"]
    # Anthropic-style: content[0].text
    content = payload.get("content")
    if isinstance(content, list) and content and isinstance(content[0], dict):
        if isinstance(content[0].get("text"), str):
            return content[0]["text"]
    # Last-ditch flat fields.
    for k in ("output_text", "text", "completion"):
        if isinstance(payload.get(k), str):
            return payload[k]
    return None


def parse_dimensions(model_text):
    """Rich parse of a model verdict into per-dimension records.

    Returns {dimension: {"verdict": 'PASS'|'FAIL'|'N/A',
                         "evidence": <str or None>,
                         "evidence_missing": <bool>}}.

    Same line grammar as parse_dimension_lines (leading bullets/numbering and
    **bold** stripped, "N/A"/"NA" normalized, the model's self-reported 'VERDICT:'
    line ignored) PLUS the optional quoted-evidence segment the rubric now asks
    for:

        <dim>: PASS|FAIL — <one-line reason> | EVIDENCE: "<verbatim quote>"

    A graded (PASS/FAIL) line carrying no parseable quote is still VALID but sets
    evidence_missing=True — the judge is ADVISORY, so a quote-less verdict degrades
    to a warning (see evidence_warnings), never a crash and never an auto-FAIL. N/A
    lines describe a not-applicable dimension with nothing to quote, so they are
    never flagged. Backward compatible: an old-format line with no EVIDENCE segment
    parses exactly as before, just with evidence=None (evidence_missing True only if
    it was graded). Evidence is read from the RAW line so its own punctuation
    survives the bullet/bold cleaning applied to the verdict half.
    """
    out = {}
    if not isinstance(model_text, str):
        return out
    for raw in model_text.splitlines():
        stripped = raw.strip()
        # Strip leading bullets/numbering and any ** bold markers, then match.
        line = stripped.lstrip("-*0123456789. \t").replace("*", "")
        m = _DIM_LINE.match(line)
        if not m:
            continue
        dim = m.group(1).lower()
        if dim == "verdict":  # never trust the model's self-reported overall line
            continue
        val = m.group(2).upper()
        verdict = "N/A" if val in ("N/A", "NA") else val
        ev_m = _EVIDENCE_RE.search(stripped)
        evidence = ev_m.group(1).strip() if ev_m else None
        if not evidence:
            evidence = None
        evidence_missing = verdict in ("PASS", "FAIL") and evidence is None
        out[dim] = {"verdict": verdict, "evidence": evidence,
                    "evidence_missing": evidence_missing}
    return out


def parse_dimension_lines(model_text):
    """Parse a model verdict into {dimension: 'PASS'|'FAIL'|'N/A'}.

    Verdict-only projection of parse_dimensions() — this is the shape aggregate()
    consumes, kept byte-for-byte compatible with the pre-evidence format (any
    trailing '— reason | EVIDENCE: "..."' is ignored here; use parse_dimensions to
    read the quote). Tolerates common model formatting: leading list markers
    ("- ", "* ", "1. ") and **bold** around the dimension name. Both "N/A" and "NA"
    normalize to 'N/A'. IGNORES the model's self-reported final 'VERDICT:' line.
    Returns {} when nothing parses.
    """
    return {dim: rec["verdict"] for dim, rec in parse_dimensions(model_text).items()}


def evidence_warnings(model_text):
    """List dimensions whose graded (PASS/FAIL) verdict shipped no quoted evidence.

    Advisory only: the rubric asks every PASS/FAIL to cite a verbatim snippet, but
    a missing quote never changes a verdict or the exit code — it is surfaced so a
    caller (e.g. run_fixtures.run_judge) can print a one-line warning. Returns [] on
    a fully-cited verdict.
    """
    return [dim for dim, rec in parse_dimensions(model_text).items()
            if rec["evidence_missing"]]


def model_family(model_id):
    """Map a model id to a coarse vendor family for the self-preference check.

    Tolerates a leading "provider/" segment (OpenRouter-style "anthropic/claude-…")
    by matching the last path segment. Unrecognized -> "unknown" (never warned on).
    Pure: no env, no I/O.
    """
    if not isinstance(model_id, str) or not model_id.strip():
        return "unknown"
    name = model_id.strip().lower().rsplit("/", 1)[-1]
    for prefix, family in _FAMILY_PREFIXES:
        if name.startswith(prefix):
            return family
    return "unknown"


def same_family_warning(judge_model, rewriter_model):
    """Return a one-line self-preference warning iff judge & rewriter share a KNOWN
    family, else None. Pure (no env, no I/O). A missing/empty rewriter model or an
    "unknown" family on either side -> None (check disabled, no false alarm).
    """
    if not judge_model or not rewriter_model:
        return None
    jf = model_family(judge_model)
    rf = model_family(rewriter_model)
    if jf == "unknown" or jf != rf:
        return None
    return (f"WARNING: judge model '{judge_model}' and rewriter model "
            f"'{rewriter_model}' are the same family ({jf}) — judge self-preference "
            f"can inflate PASS ~10-25%. Point AIWS_JUDGE_MODEL at a different family "
            f"for an independent verdict.")


def _maybe_warn_same_family():
    """Print the same-family warning to stderr at most once per process. Reads
    AIWS_JUDGE_MODEL vs the optional AIWS_REWRITER_MODEL; advisory, never blocks.
    """
    global _FAMILY_WARNING_EMITTED
    if _FAMILY_WARNING_EMITTED:
        return
    _FAMILY_WARNING_EMITTED = True  # mark before printing: warn once, even on retry
    msg = same_family_warning(os.environ.get("AIWS_JUDGE_MODEL"),
                              os.environ.get("AIWS_REWRITER_MODEL"))
    if msg:
        print(msg, file=sys.stderr)


def majority_vote(per_rep_results):
    """Merge N per-rep dimension dicts into one by majority vote per dimension.

    For v1 reps=1 this just returns a copy. Ties (or a 50/50 split) resolve to
    FAIL — the conservative choice for a judge whose job is to catch problems.
    """
    if not per_rep_results:
        return {}
    if len(per_rep_results) == 1:
        return dict(per_rep_results[0])
    dims = set().union(*(d.keys() for d in per_rep_results))
    merged = {}
    for d in dims:
        passes = sum(1 for r in per_rep_results if r.get(d) == "PASS")
        fails = sum(1 for r in per_rep_results if r.get(d) == "FAIL")
        if passes == 0 and fails == 0:
            merged[d] = "N/A"  # only N/A (or absent) votes -> not applicable
        else:
            merged[d] = "PASS" if passes > fails else "FAIL"
    return merged


def _rep_complete(rep, required):
    """A rep is complete iff every required dimension is PRESENT. A conditional dim
    may be 'N/A' (not applicable) and still counts as present/satisfied — EXCEPT
    no_fabrication, the load-bearing dim, which must be a genuine PASS/FAIL: an N/A
    there is treated as missing, so it can never launder into a verdict.
    """
    for dim in required:
        if dim not in rep:
            return False
        if dim == ALWAYS_REQUIRED and rep[dim] == "N/A":
            return False
    return True


def aggregate(per_rep_results, rubric_focus):
    """Recompute the overall verdict in Python from per-dimension results.

    A verdict counts only from reps that scored EVERY required dimension, where
    required = the fixture's rubric_focus PLUS no_fabrication (always). Reps
    missing a required dimension are INCOMPLETE and discarded — never silently
    treated as a PASS for the dimension they skipped. Returns None (-> SKIP, never
    a fake PASS) when no complete rep exists, so a missing load-bearing call can
    never produce a fabricated PASS.

    N/A handling: a conditional dimension the judge marks 'N/A' (e.g. payoff_clear
    when nothing was removed) is VACUOUSLY SATISFIED — it counts as present for
    completeness but is DROPPED from the verdict, so it neither fabricates a PASS
    nor swallows a real FAIL from the other dimensions into a silent SKIP. overall
    PASS iff every graded (PASS/FAIL) required dimension, majority-voted across the
    complete reps, is PASS.
    """
    required = set(rubric_focus) | {ALWAYS_REQUIRED}
    complete = [r for r in per_rep_results if _rep_complete(r, required)]
    if not complete:
        return None  # no complete verdict — SKIP, do not fabricate
    merged = majority_vote(complete)
    graded = [dim for dim in required if merged.get(dim) in ("PASS", "FAIL")]
    return "PASS" if all(merged[dim] == "PASS" for dim in graded) else "FAIL"
