"""Pattern tables + regexes — the executable expression of `_shared/patterns/`.

WHY a separate data module: keeping the rule *data* apart from the scan *logic*
(detector.py) mirrors how the skill keeps the catalog (`_shared/patterns/`)
apart from the polish prose. When a tell moves in/out of the catalog, only this
file changes. Each block names the catalog category it enforces.

Ported directly from `avoid-ai-writing/detector/patterns.js` (MIT). Regex
syntax translated JS -> Python `re`; behaviour kept identical. `re.I` = case
insensitive, `re.M` = multiline (`^`/`$` per line).
"""

import re

# --- Tier 1: AI vocabulary, replace on sight (catalog L1) -----------------
# Single words. Value = the plain-word suggestion the skill would offer.
TIER1 = {
    "delve": "explore, dig into, look at",
    "tapestry": "describe the actual complexity",
    "paradigm": "model, approach, framework",
    "embark": "start, begin",
    "beacon": "rewrite entirely",
    "robust": "strong, reliable, solid",
    "comprehensive": "thorough, complete, full",
    "cutting-edge": "latest, newest, advanced",
    "pivotal": "important, key, critical",
    "underscores": "highlights, shows",
    "meticulous": "careful, detailed, precise",
    "meticulously": "carefully, precisely",
    "seamless": "smooth, easy, without friction",
    "seamlessly": "smoothly, easily",
    "game-changer": "describe what changed",
    "game-changing": "describe what changed",
    "utilize": "use",
    "nestled": "is located, sits",
    "vibrant": "describe what makes it active",
    "thriving": "growing, active",
    "showcasing": "showing, demonstrating",
    "bustling": "busy, active",
    "intricate": "complex, detailed",
    "intricacies": "complexities, details",
    "ever-evolving": "changing, growing",
    "enduring": "lasting, long-running",
    "daunting": "hard, difficult",
    "holistic": "complete, full, whole",
    "holistically": "completely, fully",
    "actionable": "practical, useful, concrete",
    "impactful": "effective, significant",
    "learnings": "lessons, findings, takeaways",
    "synergy": "describe the combined effect",
    "synergies": "describe the combined effect",
    "interplay": "relationship, connection",
    "commence": "start, begin",
    "ascertain": "find out, determine",
    "endeavor": "effort, attempt, try",
    "symphony": "describe the coordination",
    "embrace": "adopt, accept, use",
}

# Multi-word Tier 1 phrases. (pattern, suggestion).
TIER1_PHRASES = [
    (re.compile(r"\bdelve\s+into\b", re.I), "explore, dig into"),
    (re.compile(r"\blandscape\b", re.I), "field, space, industry"),
    (re.compile(r"\brealm\b", re.I), "area, field, domain"),
    (re.compile(r"\btestament\s+to\b", re.I), "shows, proves"),
    (re.compile(r"\bleverage\b", re.I), "use"),
    (re.compile(r"\bwatershed\s+moment\b", re.I), "turning point, shift"),
    (re.compile(r"\bdeep\s+dive\b", re.I), "look at, examine"),
    (re.compile(r"\bdive\s+into\b", re.I), "look at, examine"),
    (re.compile(r"\bunpack(?:ing)?\b", re.I), "explain, break down"),
    (re.compile(r"\bthought\s+leader(?:ship)?\b", re.I), "expert, authority"),
    (re.compile(r"\bbest\s+practices\b", re.I), "what works, proven methods"),
    (re.compile(r"\bat\s+its\s+core\b", re.I), "cut, just state it"),
    (re.compile(r"\bin\s+order\s+to\b", re.I), "to"),
    (re.compile(r"\bdue\s+to\s+the\s+fact\s+that\b", re.I), "because"),
    (re.compile(r"\bserves\s+as\b", re.I), "is"),
    (re.compile(r"\bboasts\b", re.I), "has"),
]

# --- Tier 2: flag in clusters of 2+ per paragraph (catalog L1 tier 2) -----
TIER2 = {
    "harness": "use, take advantage of",
    "navigate": "work through, handle",
    "navigating": "working through, handling",
    "foster": "encourage, support, build",
    "elevate": "improve, raise, strengthen",
    "unleash": "release, enable, unlock",
    "streamline": "simplify, speed up",
    "empower": "enable, let, allow",
    "bolster": "support, strengthen",
    "spearhead": "lead, drive, run",
    "resonate": "connect with, appeal to",
    "resonates": "connects with, appeals to",
    "revolutionize": "change, transform",
    "facilitate": "enable, help, allow",
    "facilitates": "enables, helps, allows",
    "underpin": "support, form the basis of",
    "nuanced": "specific, subtle, detailed",
    "crucial": "important, key, necessary",
    "multifaceted": "describe the actual facets",
    "ecosystem": "system, community, network",
    "myriad": "many, numerous",
    "plethora": "many, a lot of",
    "encompass": "include, cover, span",
    "catalyze": "start, trigger, accelerate",
    "reimagine": "rethink, redesign, rebuild",
    "galvanize": "motivate, rally, push",
    "augment": "add to, expand, supplement",
    "cultivate": "build, develop, grow",
    "illuminate": "clarify, explain, show",
    "elucidate": "explain, clarify",
    "transformative": "describe what changed",
    "transformation": "describe what changed",
    "cornerstone": "foundation, basis, key part",
    "paramount": "most important, top priority",
    "poised": "ready, set, about to",
    "burgeoning": "growing, emerging",
    "nascent": "new, early-stage",
    "quintessential": "typical, classic, defining",
    "overarching": "main, central, broad",
    "underpinning": "basis, foundation",
}

# --- Tier 3: flag only at high density (catalog L1 tier 3) -----------------
TIER3 = [
    "significant", "significantly", "innovative", "innovation",
    "effective", "effectively", "dynamic", "scalable",
    "compelling", "unprecedented", "exceptional", "remarkable",
    "sophisticated", "instrumental",
    "world-class", "state-of-the-art", "best-in-class",
]
# Lookup tolerant of hyphen-stripped forms ("state-of-the-art" / "stateoftheart").
TIER3_LOOKUP = {}
for _w in TIER3:
    TIER3_LOOKUP[_w] = _w
    _dashless = _w.replace("-", "")
    if _dashless != _w:
        TIER3_LOOKUP[_dashless] = _w

# Multi-word Tier 3 boilerplate (significance-attribution / consultant-speak).
TIER3_PHRASES = [
    re.compile(r"\bemerging\s+(?:sector|space|category|industry)\b", re.I),
    re.compile(r"\bthe\s+integration\s+of\b", re.I),
    re.compile(r"\bthe\s+intersection\s+of\b", re.I),
    re.compile(r"\bcommunity-?driven\b", re.I),
    re.compile(r"\blong-?term\s+sustainability\b", re.I),
    re.compile(r"\buser\s+engagement\b", re.I),
    re.compile(r"\bdesigned\s+for\s+long-?term\b", re.I),
]

# --- Phrase-list categories -----------------------------------------------
# Each maps to a catalog category; see CATEGORIES.md for the SKILL <-> type map.
TRANSITIONS = [  # hedging-filler: signposting
    re.compile(r"\bmoreover\b", re.I),
    re.compile(r"\bfurthermore\b", re.I),
    re.compile(r"\badditionally\b", re.I),
    re.compile(r"\bin\s+today'?s\b", re.I),
    re.compile(r"\bin\s+an\s+era\s+where\b", re.I),
    re.compile(r"\bit'?s\s+worth\s+noting\s+that\b", re.I),
    re.compile(r"\bnotably\b", re.I),
    re.compile(r"\bin\s+conclusion\b", re.I),
    re.compile(r"\bin\s+summary\b", re.I),
    re.compile(r"\bwhen\s+it\s+comes\s+to\b", re.I),
    re.compile(r"\bat\s+the\s+end\s+of\s+the\s+day\b", re.I),
    re.compile(r"\bthat\s+(?:being\s+)?said\b", re.I),
]

CHATBOT_ARTIFACTS = [  # communication-artifacts: chatbot tics
    re.compile(r"\bi\s+hope\s+this\s+helps\b", re.I),
    re.compile(r"\bcertainly!\b", re.I),
    re.compile(r"\babsolutely!\b", re.I),
    re.compile(r"\bgreat\s+question!\b", re.I),
    re.compile(r"\bfeel\s+free\s+to\s+reach\s+out\b", re.I),
    re.compile(r"\blet\s+me\s+know\s+if\s+you\s+need\s+anything\b", re.I),
    re.compile(r"\bin\s+this\s+article,?\s+we\s+will\s+explore\b", re.I),
    re.compile(r"\blet'?s\s+dive\s+in!?\b", re.I),
]

SYCOPHANTIC = [  # communication-artifacts: sycophancy
    re.compile(r"\byou'?re\s+absolutely\s+right\b", re.I),
    re.compile(r"\bthat'?s\s+a\s+really\s+insightful\b", re.I),
    re.compile(r"\bthat'?s\s+a\s+great\s+question\b", re.I),
    re.compile(r"\bexcellent\s+question\b", re.I),
]

FILLERS = [  # hedging-filler: filler phrases
    re.compile(r"\bit\s+is\s+important\s+to\s+note\s+that\b", re.I),
    re.compile(r"\bin\s+terms\s+of\b", re.I),
    re.compile(r"\bthe\s+reality\s+is\s+that\b", re.I),
    re.compile(r"\bit'?s\s+important\s+to\s+note\s+that\b", re.I),
]

GENERIC_CONCLUSIONS = [  # hedging-filler: generic conclusions
    re.compile(r"\bthe\s+future\s+looks\s+bright\b", re.I),
    re.compile(r"\bonly\s+time\s+will\s+tell\b", re.I),
    re.compile(r"\bone\s+thing\s+is\s+certain\b", re.I),
    re.compile(r"\bas\s+we\s+move\s+forward\b", re.I),
]

LETS_PATTERNS = [  # hedging-filler: "let's" openers
    re.compile(r"\blet'?s\s+explore\b", re.I),
    re.compile(r"\blet'?s\s+take\s+a\s+look\b", re.I),
    re.compile(r"\blet'?s\s+break\s+this\s+down\b", re.I),
    re.compile(r"\blet'?s\s+examine\b", re.I),
    re.compile(r"\blet'?s\s+(?:consider|discuss|delve|unpack|walk\s+through)\b", re.I),
]

REASONING_ARTIFACTS = [  # communication-artifacts: reasoning-chain leaks
    re.compile(r"\blet\s+me\s+think\s+step\s+by\s+step\b", re.I),
    re.compile(r"\bbreaking\s+this\s+down\b", re.I),
    re.compile(r"\bto\s+approach\s+this\s+systematically\b", re.I),
    re.compile(r"\bhere'?s\s+my\s+thought\s+process\b", re.I),
    re.compile(r"\bfirst,?\s+let'?s\s+consider\b", re.I),
    re.compile(r"\bworking\s+through\s+this\s+logically\b", re.I),
]

ACKNOWLEDGMENT_LOOPS = [  # communication-artifacts: acknowledgment loops
    re.compile(r"\byou'?re\s+asking\s+about\b", re.I),
    re.compile(r"\bthe\s+question\s+of\s+whether\b", re.I),
    re.compile(r"\bto\s+answer\s+your\s+question\b", re.I),
]

SIGNIFICANCE_INFLATION = [  # significance-attribution: significance inflation
    re.compile(r"\bmarking\s+a\s+(?:pivotal|significant|important)\s+moment\b", re.I),
    re.compile(r"\ba\s+watershed\s+moment\s+for\b", re.I),
    re.compile(r"\bin\s+the\s+evolution\s+of\b", re.I),
    re.compile(r"\ba\s+(?:pivotal|defining)\s+moment\s+in\b", re.I),
]

VAGUE_ATTRIBUTIONS = [  # significance-attribution: vague attribution
    re.compile(r"\bexperts\s+(?:believe|say|suggest|agree)\b", re.I),
    re.compile(r"\bstudies\s+(?:show|suggest|indicate)\b", re.I),
    re.compile(r"\bresearch\s+(?:shows|suggests|indicates)\b", re.I),
    re.compile(r"\bindustry\s+leaders\s+(?:agree|believe|say)\b", re.I),
]

HOLLOW_INTENSIFIERS = [  # lexical-tells: hollow intensifiers
    re.compile(r"\bgenuine(?:ly)?\b", re.I),
    re.compile(r"\btruly\b", re.I),
    re.compile(r"\bquite\s+frankly\b", re.I),
    re.compile(r"\bto\s+be\s+honest\b", re.I),
    re.compile(r"\blet'?s\s+be\s+clear\b", re.I),
]

EMOTIONAL_FLATLINE = [  # communication-artifacts: emotional flatline
    re.compile(r"\bwhat\s+surprised\s+me\s+most\b", re.I),
    re.compile(r"\bi\s+was\s+fascinated\s+to\b", re.I),
    re.compile(r"\bwhat\s+struck\s+me\s+was\b", re.I),
    re.compile(r"\bi\s+was\s+excited\s+to\s+learn\b", re.I),
    re.compile(r"\bthe\s+most\s+interesting\s+(?:part|thing|aspect|piece)\b", re.I),
    re.compile(r"^\s*interesting\s+(?:part|thing|aspect|piece)(?:\s+of\s+(?:the\s+)?\w+)?\s*:", re.I | re.M),
]

NOVELTY_INFLATION = [  # significance-attribution: novelty inflation
    re.compile(r"\bthe\s+failure\s+mode\s+nobody'?s?\s+naming\b", re.I),
    re.compile(r"\ba\s+problem\s+nobody\s+talks\s+about\b", re.I),
    re.compile(r"\bthe\s+insight\s+everyone'?s?\s+missing\b", re.I),
    re.compile(r"\bwhat\s+nobody\s+tells\s+you\b", re.I),
]

CUTOFF_DISCLAIMERS = [  # communication-artifacts: cutoff disclaimers
    re.compile(r"\bas\s+of\s+my\s+last\s+update\b", re.I),
    re.compile(r"\bas\s+of\s+my\s+(?:knowledge\s+)?(?:cut-?off|last\s+training)\b", re.I),
    re.compile(r"\bi\s+don'?t\s+have\s+access\s+to\s+real-?time\s+(?:data|information)\b", re.I),
    re.compile(r"\bas\s+an?\s+(?:ai|artificial\s+intelligence|large\s+language|ai\s+language)\s+(?:language\s+)?model\b", re.I),
    re.compile(r"\bi\s+(?:am|'m)\s+an?\s+(?:ai|artificial\s+intelligence|large\s+language)\s+(?:assistant|model)?\b", re.I),
    re.compile(r"\bmy\s+training\s+data\s+(?:only\s+)?(?:goes\s+up\s+to|extends\s+to|ends\s+(?:in|at))\b", re.I),
]

# AI-tool fingerprints (punctuation-formatting: placeholders / citation / UTM).
AI_PLACEHOLDERS = [
    re.compile(r"\[(?:Your|Insert|Add|Enter|Describe|Specify|Choose|Pick)[^\]\n]{1,80}\]", re.I),
    re.compile(r"\[(?:Recipient|Sender|Topic|Subject|Salutation|Closing|Position|Department|Project Name|Company Name|Date)(?:\s+[^\]\n]{0,60})?\]", re.I),
    re.compile(r"\[(?:INSERT|FILL\s+IN|ADD|TODO|TBD|PLACEHOLDER)[^\]\n]{0,80}\]"),
    re.compile(r"<!--\s*(?:add|fill\s+in|insert|todo|placeholder)[^>]{0,120}-->", re.I),
]
AI_CITATION_MARKUP = [
    re.compile(r"\bcite(?:turn|news|search|navigation)\d+(?:search|turn|news|navigation)\d+", re.I),
    re.compile(r"contentReference\s*\[oaicite:[^\]]+\]\s*\{[^}]*\}", re.I),
    re.compile(r"\boai_citation\b", re.I),
    re.compile(r"\bgrok_card\b", re.I),
]
AI_UTM_SOURCE = [
    re.compile(r"[?&]utm_source=(?:chatgpt|openai|copilot|claude|grok|gemini|perplexity)(?:\.com|\.ai)?\b", re.I),
    re.compile(r"[?&]referrer=(?:chatgpt|copilot|grok|claude|gemini|perplexity)\.(?:com|ai)\b", re.I),
]

TEMPLATE_PHRASES = [  # structural-tells: template phrases
    re.compile(r"\ba\s+\w+\s+step\s+(?:towards?|forward\s+for)\b", re.I),
    re.compile(r"\bwhether\s+you'?re\s+\w+\s+or\s+\w+", re.I),
    re.compile(r"\bi\s+recently\s+had\s+the\s+pleasure\s+of\b", re.I),
]

FALSE_CONCESSION = [  # structural-tells: false concession
    re.compile(r"\bwhile\s+\w+\s+is\s+impressive\b", re.I),
    re.compile(r"\balthough\s+\w+\s+has\s+made\s+strides\b", re.I),
    re.compile(r"\bdespite\s+\w+\s+challenges?\b", re.I),
]

RHETORICAL_QUESTIONS = [  # structural-tells: rhetorical question openers
    re.compile(r"\bbut\s+what\s+does\s+this\s+mean\s+for\b", re.I),
    re.compile(r"\bso\s+why\s+should\s+you\s+care\b", re.I),
    re.compile(r"\bwhat'?s\s+next\?", re.I),
]

HEDGE_STACK = [  # hedging-filler: stacked hedging
    re.compile(r"\b(?:could|may|might)\s+(?:\w+\s+){0,2}(?:potentially|eventually|ultimately|possibly|conceivably)\b", re.I),
    re.compile(r"\b(?:potentially|eventually|ultimately)\s+(?:could|may|might)\b", re.I),
]

FUTURE_NARRATIVE = [  # hedging-filler: future-narrative closers
    re.compile(r"\b(?:may|could|will|is\s+(?:poised|set)\s+to)\s+become\s+(?:one\s+of\s+)?(?:the\s+)?(?:most\s+)?\w+\s+(?:narratives?|stories|developments?|trends?|movements?|chapters?|themes?|forces?)\b", re.I),
    re.compile(r"\bone\s+of\s+the\s+most\s+important\s+(?:narratives?|stories|trends?|themes?)\s+of\s+the\s+(?:next|coming)\s+\w+\b", re.I),
]

REAL_ACTUAL_INFLATION = [  # significance-attribution: real/actual inflation
    re.compile(r"\b(?:real|actual|genuine|true)\s+(?:on-?chain\s+)?(?:tokenomics|economics|utility|adoption|sustainability|impact|revenue|fundamentals|demand|value|innovation|traction)\b", re.I),
]

FORMULAIC_OPENERS = [  # structural-tells: formulaic challenges / essay openers
    re.compile(r"\bin\s+the\s+(?:rapidly\s+|ever-?\s*)?(?:evolving|changing|expanding|growing|shifting)\s+(?:world|landscape|realm|space|field|domain|era)\s+of\b", re.I),
    re.compile(r"\bin\s+(?:an?|the)\s+(?:digital\s+)?age\s+(?:where|of)\b", re.I),
    re.compile(r"\bhas\s+emerged\s+as\s+(?:a|the|one\s+of)\s+(?:leading|key|major|critical|essential|fundamental|pivotal|prominent|dominant|important)\s+\w+", re.I),
    re.compile(r"\bhas\s+become\s+increasingly\s+(?:important|critical|popular|relevant|prominent|essential)\b", re.I),
]

# Title-case section header (punctuation-formatting). Gated off in 'technical'.
TITLE_CASE_HEADER = re.compile(
    r"^([A-Z][a-z]+(?:\s+(?:[A-Z][a-z]+|and|or|of|the|in|for|to|a|an))+\s+[A-Z][a-z]+)\s*$",
    re.M,
)

CONFIDENCE_CALIBRATION = [  # hedging-filler: confidence-calibration phrases
    re.compile(r"\binterestingly\b", re.I),
    re.compile(r"\bsurprisingly\b", re.I),
    re.compile(r"\bimportantly\b", re.I),
    re.compile(r"\bcertainly\b", re.I),
    re.compile(r"\bundoubtedly\b", re.I),
    re.compile(r"\bwithout\s+a\s+doubt\b", re.I),
]

# --- Per-category score weights (ported from JS ISSUE_WEIGHTS) -------------
# Non-flat on purpose: a cutoff disclaimer (LLM self-ID) is far stronger
# evidence than one vague attribution. Structural/cluster signals weigh high
# because they would otherwise be washed out by the length divisor on short
# social posts.
ISSUE_WEIGHTS = {
    "tier1": 5, "tier2": 3, "tier3": 2, "transition": 2,
    "chatbot": 8, "sycophantic": 8, "filler": 2, "generic-conclusion": 3,
    "lets-construction": 2, "reasoning-artifact": 6, "acknowledgment-loop": 3,
    "significance-inflation": 4, "vague-attribution": 5, "hollow-intensifier": 2,
    "emotional-flatline": 2, "novelty-inflation": 3, "cutoff-disclaimer": 10,
    "template-phrase": 3, "false-concession": 2, "rhetorical-question": 2,
    "confidence-calibration": 2, "em-dash": 4, "uniformity": 5, "formatting": 3,
    "tier3-phrase": 3, "tier3-phrase-cluster": 12, "hashtag-stuff": 12,
    "bullet-np-list": 10, "hedge-stack": 6, "future-narrative": 12,
    "real-actual-inflation": 5, "formulaic-opener": 8, "title-case-header": 4,
    "low-ttr": 3, "ai-placeholder": 10, "ai-citation-markup": 15,
    "ai-utm-source": 12,
}
