"""analyze() — scan text for AI tells, score it, classify it.

Port of `avoid-ai-writing/detector/patterns.js > analyzeText`. Same scoring
model: collect raw issues -> dedup by (type, text) -> sum category weights ->
normalize by log2(words/50) so longer texts don't accumulate unboundedly.

Return shape (dict):
  score        : int 0-100
  label        : human-readable band ("Clean" .. "Heavy AI patterns")
  issues       : list of {type, text, severity, suggestion}
  stats        : {wordCount, contextMode, tier counts, ...}
  classification: HUMAN_ONLY | MIXED | AI_ONLY  (GPTZero-shaped, FN-biased)
  confidence   : low | medium | high

WHY FN-biased: a false "this is AI" on real human writing destroys trust worse
than a missed AI passage. Ambiguity routes to MIXED, never AI_ONLY.

LIMITATION (review m4): word counting assumes whitespace-delimited scripts
(`\S+`). CJK / non-space-delimited text (Chinese, Japanese) collapses to a tiny
word count and returns UNSCORED ("Too short") rather than a real score. That is
NOT a clean-text signal — it means "unsupported script." Bilingual/CJK scoring
is v2 (see voice-onboard + scenario-presets, which scope bilingual to v2).
"""

import math
import re

from . import patterns as P

MAX_WORDS = 10000  # bail above this rather than regex-scanning a pasted novel

_WORD_RE = re.compile(r"\S+")
_TOKEN_RE = re.compile(r"[\w'-]+")


def _tokenize(text):
    return _TOKEN_RE.findall(text.lower())


def _count_words(text):
    return len(_WORD_RE.findall(text))


def _paragraphs(text):
    return [p for p in re.split(r"\n\s*\n", text) if p.strip()]


def _sentences(text):
    return [s for s in re.split(r"[.!?]+", text) if len(s.strip()) > 5]


def _match(text, regexes, category, severity):
    """Run a list of compiled regexes, return one issue per match."""
    out = []
    for rx in regexes:
        for m in rx.finditer(text):
            out.append({"type": category, "text": m.group(0),
                        "severity": severity, "suggestion": None})
    return out


def get_label(score):
    if score == 0:
        return "Clean"
    if score <= 15:
        return "Minimal AI signals"
    if score <= 35:
        return "Some AI patterns"
    if score <= 60:
        return "Moderate AI signals"
    if score <= 80:
        return "Strong AI signals"
    return "Heavy AI patterns"


def _dedup(issues):
    """Dedup by (type, lowercased text) so repeated hits count once.

    Mirrors the JS: the score reflects the *distinct* signals a user sees, not
    raw match count — otherwise one repeated phrase inflates the number.
    """
    seen = set()
    out = []
    for it in issues:
        key = (it["type"], (it["text"] or "").lower())
        if key in seen:
            continue
        seen.add(key)
        out.append(it)
    return out


def analyze(text, context_mode="general"):
    if not text or not text.strip():
        return _unscored("Empty", 0)

    word_count = _count_words(text)
    if word_count < 10:
        return _unscored("Too short", word_count)
    if word_count > MAX_WORDS:
        return _unscored("Text too long", word_count)

    valid_modes = {"general", "technical", "marketing", "personal"}
    if context_mode not in valid_modes:
        context_mode = "general"

    tokens = _tokenize(text)
    paragraphs = _paragraphs(text)
    sentences = _sentences(text)
    issues = []

    # 1. Tier 1 single words (one issue per distinct word).
    tier1_found = set()
    for tok in tokens:
        if tok in P.TIER1 and tok not in tier1_found:
            tier1_found.add(tok)
            issues.append({"type": "tier1", "text": tok, "severity": "high",
                           "suggestion": P.TIER1[tok]})
    # Tier 1 multi-word phrases.
    for rx, sugg in P.TIER1_PHRASES:
        for m in rx.finditer(text):
            low = m.group(0).lower()
            if low in tier1_found:
                continue
            tier1_found.add(low)
            issues.append({"type": "tier1", "text": m.group(0),
                           "severity": "high", "suggestion": sugg})

    # 2. Tier 2 clusters — only flag when 2+ distinct hits in one paragraph.
    tier2_clusters = 0
    for para in paragraphs:
        found = []
        for tok in _tokenize(para):
            if tok in P.TIER2 and tok not in found:
                found.append(tok)
        if len(found) >= 2:
            tier2_clusters += 1
            for w in found:
                issues.append({"type": "tier2", "text": w, "severity": "medium",
                               "suggestion": P.TIER2[w]})

    # 3. Tier 3 density — flag at 3% of words, floor of 3 occurrences.
    tier3_counts = {}
    for tok in tokens:
        canon = P.TIER3_LOOKUP.get(tok)
        if canon:
            tier3_counts[canon] = tier3_counts.get(canon, 0) + 1
    density_threshold = max(3, math.floor(word_count * 0.03))
    for word, count in tier3_counts.items():
        if count >= density_threshold:
            issues.append({"type": "tier3", "text": f'"{word}" x{count}',
                           "severity": "low",
                           "suggestion": f"Overused ({count} times in {word_count} words)"})

    # 4. Phrase-list categories.
    issues += _match(text, P.TRANSITIONS, "transition", "medium")
    issues += _match(text, P.CHATBOT_ARTIFACTS, "chatbot", "critical")
    issues += _match(text, P.SYCOPHANTIC, "sycophantic", "critical")
    issues += _match(text, P.FILLERS, "filler", "medium")
    issues += _match(text, P.GENERIC_CONCLUSIONS, "generic-conclusion", "medium")
    issues += _match(text, P.LETS_PATTERNS, "lets-construction", "medium")
    issues += _match(text, P.REASONING_ARTIFACTS, "reasoning-artifact", "critical")
    issues += _match(text, P.ACKNOWLEDGMENT_LOOPS, "acknowledgment-loop", "medium")
    issues += _match(text, P.SIGNIFICANCE_INFLATION, "significance-inflation", "high")
    issues += _match(text, P.VAGUE_ATTRIBUTIONS, "vague-attribution", "critical")
    issues += _match(text, P.HOLLOW_INTENSIFIERS, "hollow-intensifier", "medium")
    issues += _match(text, P.EMOTIONAL_FLATLINE, "emotional-flatline", "low")
    issues += _match(text, P.NOVELTY_INFLATION, "novelty-inflation", "medium")
    issues += _match(text, P.CUTOFF_DISCLAIMERS, "cutoff-disclaimer", "critical")
    issues += _match(text, P.AI_PLACEHOLDERS, "ai-placeholder", "critical")
    issues += _match(text, P.AI_CITATION_MARKUP, "ai-citation-markup", "critical")
    issues += _match(text, P.AI_UTM_SOURCE, "ai-utm-source", "critical")
    issues += _match(text, P.TEMPLATE_PHRASES, "template-phrase", "high")
    issues += _match(text, P.FALSE_CONCESSION, "false-concession", "medium")
    issues += _match(text, P.RHETORICAL_QUESTIONS, "rhetorical-question", "medium")
    issues += _match(text, P.HEDGE_STACK, "hedge-stack", "high")
    issues += _match(text, P.FUTURE_NARRATIVE, "future-narrative", "high")
    issues += _match(text, P.REAL_ACTUAL_INFLATION, "real-actual-inflation", "medium")
    issues += _match(text, P.FORMULAIC_OPENERS, "formulaic-opener", "high")

    # Title-case headers — skip in technical mode (API docs use Title Case).
    if context_mode != "technical":
        for m in P.TITLE_CASE_HEADER.finditer(text):
            txt = m.group(0)
            toks = txt.split()
            # Keep only the AI mid-sentence shape (has "And"/"Of"/etc.), drop
            # plain headline-style proper-noun titles.
            if len(toks) >= 4 and re.search(r"\b(?:And|Or|Of|The|In|For|To|A|An)\b", txt):
                issues.append({"type": "title-case-header", "text": txt,
                               "severity": "medium", "suggestion": None})

    # Confidence calibration — only when it stacks (3+ raw hits).
    conf = _match(text, P.CONFIDENCE_CALIBRATION, "confidence-calibration", "low")
    if len(conf) >= 3:
        issues += conf

    # Tier 3 multi-word phrases: per-phrase repetition + cross-phrase cluster.
    distinct_phrases_hit = 0
    for rx in P.TIER3_PHRASES:
        spans = rx.findall(text)
        matches = list(rx.finditer(text))
        if not matches:
            continue
        distinct_phrases_hit += 1
        if len(matches) >= 2:
            issues.append({"type": "tier3-phrase",
                           "text": f'"{matches[0].group(0).lower()}" x{len(matches)}',
                           "severity": "medium", "suggestion": None})
    if distinct_phrases_hit >= 3:
        issues.append({"type": "tier3-phrase-cluster",
                       "text": f"{distinct_phrases_hit} distinct boilerplate phrases",
                       "severity": "high", "suggestion": None})

    # Hashtag stuffing — 6+ tags reads as bot output.
    hashtags = re.findall(r"(?:^|\W)#\w[\w-]*", text)
    if len(hashtags) >= 6:
        issues.append({"type": "hashtag-stuff", "text": f"{len(hashtags)} hashtags",
                       "severity": "medium", "suggestion": None})

    # Bullet list of bare noun phrases (5+ short verbless items).
    _detect_bullet_np(text, issues)

    # Em-dash overuse — rate normalized per 1000 words.
    em_dash_count = len(re.findall(r"—|(?<=\s)--(?=\s|$)", text))
    if word_count and em_dash_count / (word_count / 1000.0) > 1:
        issues.append({"type": "em-dash",
                       "text": f"{em_dash_count} em dashes in {word_count} words",
                       "severity": "medium", "suggestion": None})

    # Sentence-length uniformity (burstiness — catalog rhythm-stylometric).
    if len(sentences) >= 5:
        lengths = [_count_words(s) for s in sentences]
        avg = sum(lengths) / len(lengths)
        var = sum((l - avg) ** 2 for l in lengths) / len(lengths)
        cv = (math.sqrt(var) / avg) if avg > 0 else 0
        if cv < 0.25 and avg > 10:
            issues.append({"type": "uniformity",
                           "text": f"Sentence lengths cluster around {round(avg)} words",
                           "severity": "medium", "suggestion": None})

    # Type-token ratio (low vocabulary diversity) — conservative, 200+ tokens.
    if len(tokens) >= 200:
        ttr = len(set(tokens)) / len(tokens)
        if ttr < 0.4:
            issues.append({"type": "low-ttr",
                           "text": f"Vocabulary diversity {ttr*100:.1f}%",
                           "severity": "low", "suggestion": None})

    # Bold overuse.
    bold = re.findall(r"\*\*[^*]+\*\*", text)
    if len(bold) > 3:
        issues.append({"type": "formatting", "text": f"{len(bold)} bold phrases",
                       "severity": "medium", "suggestion": None})

    # --- Score from the deduped list ---
    deduped = _dedup(issues)
    raw_score = sum(P.ISSUE_WEIGHTS.get(it["type"], 2) for it in deduped)
    length_factor = max(1.0, math.log2(word_count / 50.0))
    score = min(100, round(raw_score / length_factor))
    label = get_label(score)

    tier1_count = sum(1 for i in deduped if i["type"] == "tier1")
    tier2_count = sum(1 for i in deduped if i["type"] == "tier2")
    tier3_count = sum(1 for i in deduped if i["type"] == "tier3")

    classification, confidence = _classify(
        score, deduped, word_count, tier1_count, tier2_clusters)

    return {
        "score": score,
        "label": label,
        "issues": deduped,
        "stats": {
            "wordCount": word_count,
            "contextMode": context_mode,
            "tier1Count": tier1_count,
            "tier2Count": tier2_count,
            "tier2Clusters": tier2_clusters,
            "tier3Count": tier3_count,
            "patternCount": len(deduped) - tier1_count - tier2_count - tier3_count,
        },
        "classification": classification,
        "confidence": confidence,
    }


def _detect_bullet_np(text, issues):
    """Flag 5+ consecutive short (<=6 word) verbless bullet items."""
    lines = re.split(r"\r?\n", text)
    bullet_re = re.compile(r"^\s*(?:\*|-|•|\+)\s+(.+)$")
    verb_re = re.compile(
        r"\b(?:is|are|was|were|has|have|had|will|would|should|must|do|does|"
        r"did|can|could|may|might|am|been|being)\b", re.I)
    fence_re = re.compile(r"^\s*(?:```|~~~)")
    run = []
    blank = 0
    in_fence = False

    def flush():
        nonlocal run, blank
        if len(run) >= 5:
            bare = [it for it in run
                    if 0 < len(it.split()) <= 6 and not verb_re.search(it)]
            if len(bare) >= 5 and len(bare) / len(run) >= 0.75:
                issues.append({"type": "bullet-np-list",
                               "text": f"{len(run)}-item bullet list of bare noun phrases",
                               "severity": "high", "suggestion": None})
        run = []
        blank = 0

    for line in lines:
        if fence_re.match(line):
            flush()
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        m = bullet_re.match(line)
        if m:
            run.append(m.group(1).strip())
            blank = 0
        elif line.strip() == "":
            blank += 1
            if blank >= 2:
                flush()
        else:
            flush()
    flush()


def _classify(score, issues, word_count, tier1_count, tier2_clusters):
    """GPTZero-shaped trinary classification + confidence. FN-biased."""
    types = {i["type"] for i in issues}
    has_cutoff = "cutoff-disclaimer" in types
    has_reasoning = "reasoning-artifact" in types
    has_chatbot = "chatbot" in types
    has_transition = "transition" in types
    dense_ai_vocab = (word_count >= 150 and tier1_count >= 5
                      and tier2_clusters >= 2 and has_transition)
    strong = ((1 if has_cutoff else 0)
              + (1 if (has_reasoning and has_chatbot) else 0)
              + (1 if dense_ai_vocab else 0))

    if score < 15 and strong == 0:
        classification = "HUMAN_ONLY"
    elif strong >= 1 or score >= 70:
        classification = "AI_ONLY"
    else:
        classification = "MIXED"

    if strong >= 2 or has_cutoff or (score < 8 and word_count >= 100):
        confidence = "high"
    elif strong >= 1 or score < 20:
        confidence = "medium"
    else:
        confidence = "low"
    return classification, confidence


def _unscored(label, word_count):
    return {
        "score": 0, "label": label, "issues": [],
        "stats": {"wordCount": word_count}, "classification": "UNSCORED",
        "confidence": "low",
        "tooShort": label in ("Empty", "Too short"),
        "tooLong": label == "Text too long",
    }
