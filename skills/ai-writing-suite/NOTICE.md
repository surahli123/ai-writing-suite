# Attribution & Licenses

AI Writing Suite is a consolidated writing-assistant skill that absorbs and extends patterns, templates, and methodologies from seven open-source projects, all MIT-licensed. This document preserves the copyright and license notice for each source.

## Source Projects

### 1. anti-vibe-writing

**Author:** weijt606  
**Repository:** [weijt606/anti-vibe-writing](https://github.com/weijt606/anti-vibe-writing)  
**License:** MIT  
**Copyright:** Copyright (c) 2026 weijt606

**Contribution:** Bilingual (Chinese/English) pattern sets, scenario presets (tweet, LinkedIn, README, memo templates), learning-mode framework, host-profile voice template structure, and final-pass checklist.

**Used in:** `comms-polish` scenario presets, `voice-onboard` host-profile template.

---

### 2. avoid-ai-writing

**Author:** Conor Bronsdon  
**Repository:** [conorbronsdon/avoid-ai-writing](https://github.com/conorbronsdon/avoid-ai-writing)  
**License:** MIT  
**Copyright:** Copyright (c) 2026 Conor Bronsdon

**Contribution:** Programmatic JavaScript detector with test suite, tiered AI-vocabulary taxonomy (Tier 1/2/3 classification), CATEGORIES taxonomy for AI-writing patterns, multi-surface packaging patterns (Claude plugin, Cursor `.mdc` format), and sync tooling scaffold.

**Used in:** AI-tell pattern catalog (lexical tells, significance attribution, structural patterns), detector foundation (v2), packaging and sync conventions.

---

### 3. AI-Vibe-Writing-Skills

**Author:** AI Vibe Writing Skill Contributors  
**Repository:** [donghuixin/AI-Vibe-Writing-Skills](https://github.com/donghuixin/AI-Vibe-Writing-Skills)  
**License:** MIT  
**Copyright:** Copyright (c) 2024 AI Vibe Writing Skill Contributors

**Contribution:** Local AI-detector methodology, style-extractor and reviewer agent prompts, soft/hard memory patterns for voice learning, and self-improvement loop structure.

**Used in:** `voice-onboard` distillation prompts, `comms-polish` voice-matching review, self-improvement memory patterns.

---

### 4. nature-skills

**Author:** Yuan Yizhe  
**Repository:** [Yuan1z0825/nature-skills](https://github.com/Yuan1z0825/nature-skills)  
**License:** MIT  
**Copyright:** Copyright (c) 2026 Yuan Yizhe

**Contribution:** Academic and technical writing polish rubric, structural editing patterns (from `nature-writing` and `nature-polishing` subskills), Codex plugin manifest conventions.

**Used in:** AI-tell pattern catalog (rhythm, stylometry, structural tells), `comms-polish` scoring and review rubric, Codex packaging conventions.

---

### 5. stop-slop

**Author:** Hardik Pandya  
**Repository:** [stop-slop](https://github.com/stop-slop)  
**License:** MIT  
**Copyright:** Copyright (c) Hardik Pandya

**Contribution:** Eight core directness rules, scoring rubric, and baseline calibration methodology.

**Used in:** Consolidated pattern catalog, eval baseline calibration, detection scoring.

---

### 6. blader/humanizer

**Author:** Brandon Wise  
**Repository:** [blader/humanizer](https://github.com/blader/humanizer)  
**License:** MIT  
**Copyright:** Copyright (c) Brandon Wise

**Contribution:** 43-pattern humanizer catalog with Tell / Fix / example structure and voice calibration framework.

**Used in:** Consolidated pattern catalog (`_shared/patterns/`), core detection baseline. *Note: Patterns P31-P43 were re-derived cleanly from intent due to formatting corruption in the original source; lineage and attribution preserved.*

---

### 7. aboudjem/humanizer-skill

**Author:** Aboudjem  
**Repository:** [Aboudjem/humanizer-skill](https://github.com/Aboudjem/humanizer-skill)  
**License:** MIT  
**Copyright:** Copyright (c) Aboudjem

**Contribution:** 30-pattern catalog derived from Wikipedia's "Signs of AI writing," with structured Tell / Fix / example format.

**Used in:** Consolidated pattern catalog (`_shared/patterns/`), detection baseline, pattern structure conventions.

---

## Consolidated Pattern Catalog

The file `_shared/patterns/00-index.md` serves as the single source of truth for all AI-writing patterns used by `comms-polish`. It deduplicates and cross-references patterns from all seven sources above, with each pattern tagged by its source origin (via `Sources` field) so lineage is traceable.

See `_shared/patterns/00-index.md` for:
- **Source legend:** mapping of source tags (e.g., `blader`, `aboudjem`, `stop-slop`, `avoid-ai`, `anti-vibe`, `ai-vibe`, `nature`) to source projects and licenses.
- **Pattern IDs:** stable identifiers for each pattern, not source-specific numbering.
- **Deduplicated catalog:** seven overlapping lists merged into one, with every pattern preserving its source credits.

---

## License Summary

All source material is MIT-licensed. Under MIT, this work is permitted to:
- Reproduce, prepare derivative works of, distribute, and sublicense the material
- **On the condition that:** copyright notices and license text are included in any distribution

**Full MIT License text:** See `LICENSE` in the repository root.

---

## How to Use This Notice

When redistributing or forking AI Writing Suite:
1. Keep this file (`NOTICE.md`) intact in every distribution.
2. Keep the `LICENSE` file in the repository root.
3. Preserve the source tags in `_shared/patterns/00-index.md` so pattern lineage remains traceable.
4. Update the source legend in `_shared/patterns/00-index.md` if you add new sources.

---

## No Private Material

This package contains **no private prompts, local user configuration, secrets, or installed-skill internals**. All content is:
- Derived from the seven source projects above, or
- Newly written for the OSS suite, or
- Scaffolding and metadata to make the skill portable across Claude, Codex, Cursor, and RovoDev.

The company version (not in this public repo) layers a proprietary **DS Comms Playbook** into the `_shared/knowledge/` slot via a Confluence page, keeping the playbook private while reusing the public engine.

---

## Questions or Corrections?

If a copyright holder is incorrectly attributed, or if a source should be added, please open an issue or contact the repository maintainer.
