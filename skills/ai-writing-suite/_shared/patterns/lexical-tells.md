# Lexical Tells (word-level)

Word- and phrase-level habits. These are the easiest to spot and the easiest to
over-correct, so flag in clusters, not in isolation: one "however" is nothing; a
paragraph of delve + leverage + robust + tapestry is a confession.

---

### L1 — AI vocabulary words (tiered)

| Severity | Enforcement |
| --- | --- |
| medium | regex |

- **Tell:** A small set of words appears 5-20x more often in post-2023 model
  output than in human prose, and tends to cluster.
- **Fix:** Replace with the plain word. Flag by tier, not on sight, to cut
  false positives on second-language and technical writing.
- **Sources:** avoid-ai (tiered table), blader (P7), aboudjem (§7), stop-slop.

**Tier 1 — replace on sight** (appears ~5-20x more in AI text):
delve / delve into, landscape (metaphor), tapestry, realm, paradigm, embark,
beacon, testament to, robust, comprehensive, cutting-edge, leverage (verb),
pivotal, underscores, meticulous, seamless, game-changer, utilize, nestled,
vibrant, thriving, showcasing, deep dive / dive into, unpack, bustling,
intricate / intricacies, ever-evolving, enduring, daunting, holistic,
actionable, impactful, learnings, thought leader, best practices, at its core,
synergy, interplay, in order to, due to the fact that, serves as, features
(verb), boasts, commence, ascertain, endeavor, embrace (metaphor).

**Tier 2 — flag when 2+ appear in one paragraph** (fine alone, suspect together):
harness, navigate / navigating, foster, elevate, unleash, streamline, empower,
bolster, spearhead, resonate, revolutionize, facilitate, underpin, nuanced,
crucial, multifaceted, ecosystem (metaphor), myriad, plethora, encompass,
catalyze, reimagine, galvanize, augment, cultivate, illuminate, elucidate,
juxtapose, transformative, cornerstone, paramount, poised, burgeoning, nascent,
quintessential, overarching, underpinning.

**Tier 3 — flag only at high density** (normal words AI just overuses):
significant(ly), innovative / innovation, effective(ly), dynamic, scalable,
compelling, unprecedented, exceptional, remarkable, sophisticated, instrumental,
world-class / state-of-the-art / best-in-class.

**Replace-on-sight table (Tier 1 → plain swap).** Deterministic suggestions, not guesses —
reach for these instead of inventing a substitution. This table mirrors
`evals/detector/patterns.py` `TIER1`; a dev sync-test (`evals/test_catalog_sync.py`) fails
if the two drift (regenerate from `patterns.py` in v2).

| AI word | Plain swap |
| --- | --- |
| delve | explore, dig into, look at |
| tapestry | describe the actual complexity |
| paradigm | model, approach, framework |
| embark | start, begin |
| beacon | rewrite entirely |
| robust | strong, reliable, solid |
| comprehensive | thorough, complete, full |
| cutting-edge | latest, newest, advanced |
| pivotal | important, key, critical |
| underscores | highlights, shows |
| meticulous | careful, detailed, precise |
| meticulously | carefully, precisely |
| seamless | smooth, easy, without friction |
| seamlessly | smoothly, easily |
| game-changer | describe what changed |
| game-changing | describe what changed |
| utilize | use |
| nestled | is located, sits |
| vibrant | describe what makes it active |
| thriving | growing, active |
| showcasing | showing, demonstrating |
| bustling | busy, active |
| intricate | complex, detailed |
| intricacies | complexities, details |
| ever-evolving | changing, growing |
| enduring | lasting, long-running |
| daunting | hard, difficult |
| holistic | complete, full, whole |
| holistically | completely, fully |
| actionable | practical, useful, concrete |
| impactful | effective, significant |
| learnings | lessons, findings, takeaways |
| synergy | describe the combined effect |
| synergies | describe the combined effect |
| interplay | relationship, connection |
| commence | start, begin |
| ascertain | find out, determine |
| endeavor | effort, attempt, try |
| symphony | describe the coordination |
| embrace | adopt, accept, use |

Common Tier-1 phrases: `delve into` → explore / dig into · `landscape` → field / space ·
`realm` → area / field · `testament to` → shows / proves · `leverage` → use · `deep dive`
/ `dive into` → look at / examine · `unpack` → explain / break down · `best practices` →
what works · `in order to` → to · `due to the fact that` → because · `serves as` → is ·
`boasts` → has.

> The tier idea comes from avoid-ai (adapted from brandonwise/humanizer vocab
> research). Tiering is what keeps this rule from flattening legitimate prose.

---

### L2 — Copula avoidance

| Severity | Enforcement |
| --- | --- |
| low | judge |

- **Tell:** The model dodges plain "is" / "are" / "has" with fancier verbs to
  sound sophisticated: serves as, stands as, marks, represents, boasts,
  features, offers, presents.
- **Fix:** Use the copula. "Gallery 825 *is* the exhibition space," not "Gallery
  825 *serves as* the exhibition space." Only keep the fancier verb if it adds
  real meaning.
- **Sources:** blader (P8), aboudjem (§8), avoid-ai, anti-vibe.

---

### L3 — Synonym / noun-phrase cycling (elegant variation)

| Severity | Enforcement |
| --- | --- |
| medium | judge |

- **Tell:** Repetition-penalty training makes models rename the same thing to
  avoid repeating a word: "the protagonist… the main character… the central
  figure… the hero," or whole noun phrases: "the artist… the non-conformist
  painter… the visionary creator."
- **Fix:** Pick the clearest term and repeat it. Humans repeat words; repetition
  reads as precision, not poverty.
- **Sources:** blader (P11 word-level + P31 noun-phrase), aboudjem (§11),
  avoid-ai, anti-vibe.

> blader split this into two ids (word-level P11 vs noun-phrase P31). Merged
> here because the fix is identical; the distinction is noted for lineage only.

---

### L4 — False ranges

| Severity | Enforcement |
| --- | --- |
| medium | judge |

- **Tell:** "From X to Y" where X and Y are not on a real spectrum, faking
  breadth: "from the Big Bang to dark matter," "from onboarding to billing."
- **Fix:** List the actual items, or pick the one that matters. Don't fake a
  range.
- **Sources:** blader (P12), aboudjem (§12), avoid-ai, anti-vibe.

---

### L5 — Hyphenated-pair overuse

| Severity | Enforcement |
| --- | --- |
| low | judge |

- **Tell:** Two problems. (a) Density: stacking compound modifiers on one noun
  ("a high-quality, well-architected, future-proof solution"). (b) The
  attributive/predicate error: a compound is hyphenated *before* the noun ("a
  high-quality report") but not *after* a linking verb ("the report is high
  quality"). Models frequently hyphenate the predicate form.
- **Fix:** Cut to the modifier that matters; drop the hyphen in predicate
  position.
- **Sources:** aboudjem (§26), avoid-ai (adapted from blader P26).

---

### L6 — Hollow / "real-actual" intensifiers

| Severity | Enforcement |
| --- | --- |
| low | regex |

- **Tell:** Empty intensifiers padding a claim: genuine, real, truly, quite
  frankly, to be honest. Plus the noun-modifier form where real / actual /
  genuine / true latches onto an abstract noun to imply the rest of the field is
  fake without saying what makes this one real ("real on-chain tokenomics,"
  "genuine utility").
- **Fix:** Cut the intensifier and state the specific claim. **Carve-out:** keep
  it when the sentence names the contrast ("actual revenue from customers, not
  grants") — that is honest contrastive writing, not a tell.
- **Sources:** avoid-ai (hollow intensifiers + real/actual inflation), stop-slop.
