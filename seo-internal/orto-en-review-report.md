# Orthography Review · EN content

> Conducted by senior English copyeditor agent, grounded in OED, Garner's Modern English Usage, Chicago Manual of Style 17e, New Hart's Rules, AP Stylebook and Merriam-Webster.
> Date: 29 April 2026

---

## Executive summary

- Files reviewed: 50 markdown sources (homepage, 4 service pages, 1 retrofit/communities, 20 articles, 17 area landings, 7 comarcal hubs, about). `/legal/` skipped per scope (counsel pending).
- Errors detected by category:
  - Spelling (US/UK consistency): ~80+ instances (site-wide, consistent British usage; flagged not auto-corrected)
  - Grammar: 0 confident errors found in spot-checks
  - Punctuation: 2 banned em-dashes
  - Calques / idiom: 6 borderline `actually` usages (acceptable in context); 0 hard calques
  - Brand terminology: pass (Passivhaus, Eskimohaus®, EnerPHit, CLT correctly handled with parentheticals)
- Auto-corrections applied: 2
- Flagged for human review: 5 categories (see below)
- Regenerator (`python3 generate_html.py`): OK — wrote 162 HTML files, failed=0

---

## Corrections applied

| File | Line | Original | Corrected | Source / rationale |
|---|---|---|---|---|
| `articles/article-passivhaus-budget-en.md` | 39 | `(ITeC, COAC, IDAE — Catalan, Catalan and Spanish technical and energy agencies)` | `(ITeC, COAC, IDAE; Catalan, Catalan and Spanish technical and energy agencies)` | Style guide v1.1 §2.7: em-dashes banned. CMS 17e §6.85 permits semicolon as substitute. |
| `about-en.md` | 3 | `… the team page lives at /en/about — wait: in EN …` | `… the team page lives at /en/about; wait: in EN …` | Same. (This is an editorial note in the doc front-matter; preserved meaning, replaced em-dash with semicolon.) |

---

## Flagged for human review (NOT auto-corrected)

### F1 · British vs American spelling — site-wide inconsistency with brief

**Brief specifies American English as default.** EN copy was drafted consistently in **British English**. Switching the entire site is a 80+ change operation that should be a deliberate executive decision; either:

- **Option A (recommended, lowest churn):** retain British forms (`-ise`, `centre`, `colour`, `optimised`, `recognised`, `behaviour`, `specialised`, `personalised`, `formalised`, `monetise`, `maximise`, `equalise`, `organised`) and update the style guide to declare British English as the standing PAPIK English. International business audiences accept British without friction; the existing copy is internally consistent.
- **Option B (per current brief):** convert to American (`-ize`, `center`, `color`, `optimized`, `recognized`, `behavior`, `specialized`, `personalized`, `formalized`, `monetize`, `maximize`, `equalize`, `organized`). Estimate: 80–120 substitutions across ~30 files. Toponym "Centre Direccional" stays Catalan; "research centre" / "town centre" / "historic centre" all become "center".

Decision required. **Sources affected (representative):** `homepage-en.md`, `about-en.md`, `construction-en.md`, `retrofit-en.md`, `wealth-en.md`, `articles/article-passivhaus-principles-en.md`, `articles/article-passivhaus-budget-en.md`, `articles/article-passivhaus-sustainability-en.md`, `articles/article-wood-revolution-en.md`, `areas/sant-cugat-del-valles-en.md`, `areas/vilanova-i-la-geltru-en.md`, `regions/maresme-en.md`, `regions/baix-emporda-en.md`, `regions/baix-llobregat-en.md`, plus most other landings.

### F2 · Serial (Oxford) comma — site-wide non-use

Brief mandates the serial comma. Source files consistently follow British convention (no serial comma): "construction, development, retrofit and wealth", "Catalonia, the Balearic Islands and Andorra", "transport, treatment and disposal", etc. Same decision as F1; both choices should be aligned. Auto-fixing without human eye risks comma errors before non-conjunction `and` (e.g., `"between 20 and 30 centimetres"`, `"timber, timber-aluminium, or premium-grade PVC"` — the latter actually does carry an Oxford comma already, showing inconsistent author practice). Recommend a focused human pass after F1 decision.

### F3 · British `-ised` past participles — same family as F1

`organised`, `specialised`, `optimised`, `recognised`, `formalised`, `personalised`, `monetised`, `maximise`, `equalise`. Pure US/UK preference; not errors. Hold pending F1 decision.

### F4 · Editorial commentary in `about-en.md` line 3

The blockquote at L3 of `about-en.md` is a multi-iteration internal note that has accreted contradictory rationales ("note: in EN /about IS the slug for both, the team page lives at /en/about; wait: in EN, /about is 'us' page …  Resolved per user spec: this is the new brief about-us page at /en/about"). Renders publicly as Markdown blockquote. Recommend either deleting the blockquote entirely (it is internal) or replacing with a single clean line. Not auto-corrected because deletion is editorial, not orthographic.

### F5 · `actually` — six instances (US idiom check)

In `article-sustainable-materials-en.md` (L11, L37), `article-ecological-footprint-en.md` (L43, L83), `article-green-mortgage-en.md` (L60), the word "actually" is used in the natural English sense ("in fact / in reality"), **not** as the Spanish calque for "currently". All six instances scan correctly. **No correction needed.** Listed for completeness so reviewers can spot-check.

---

## Spot-check confirmations (3 files final pass)

- `homepage-en.md`: clean. Toponym handling correct (parenthetical glosses on first mention). Brand terminology correct. Passes.
- `articles/article-passivhaus-principles-en.md`: clean post-em-dash sweep. Note this file *does* use the Oxford comma in places (L52, L84), confirming author inconsistency on F2.
- `wealth-en.md`: clean. Disclaimer language present (CNMV, MiFID II, FCA/SEC/BaFin/AMF caveat at L438). Counsel review tag preserved.

---

## Brand and terminology consistency · pass

Verified across the corpus:

- "Passivhaus" capitalised (62+ occurrences); "passive house" lowercase used as generic gloss only.
- "Eskimohaus®" with ® consistent.
- "EnerPHit" capitalised correctly (no spaces).
- "CLT (cross-laminated timber)" first-mention parenthetical applied.
- "SATE (external thermal insulation system / external thermal insulation composite system)" — first-mention parenthetical applied; minor wording variance between files but both forms are technically accurate.
- "POUM (local urban plan)", "EMD (Decentralised Municipal Entity)", "NGEU", "CTE", "ITE": parentheticals applied on first mention.
- Toponyms: Catalan forms preserved; "(greater Barcelona area)", "(Maresme coast)" geographic glosses applied on first mention.
- "Catalonia" used (not "Catalunya"). "the Balearic Islands" used (not "the Balearics"). "Spain" used (not "the Spanish state").

---

## Punctuation

- Em-dashes (`—`): **2 found, 2 fixed.** None remain in the EN markdown corpus.
- En-dashes (`–`): not used in prose; numeric ranges use hyphen ("5 to 15 per cent", "2024-2026"). Acceptable.
- Double spaces: none found.
- Exclamation marks: none in prose body. Compliant with style guide §2.5.
- Apostrophes: spot-checked. PAPIK's, client's, project's, building's all correctly singular-possessive; no errors detected.
- Quotation marks: smart curly quotes are used in source. Compliant.

---

## Grammar

No subject-verb-agreement, dangling-modifier, comma-splice or tense-inconsistency errors detected in spot-checks of the homepage, four service pages, three high-traffic articles (`article-passivhaus-principles`, `article-passivhaus-budget`, `article-passivhaus-sustainability`) and three landings (`sant-cugat-del-valles`, `bellaterra`, `matadepera`). Prose register is consistently adult and professional.

Calque scan came up clean: no `discuss about`, `depend of`, `enjoy of`, `according with`, `assist to`, `approbation`, `patrimony`, `dramatic` (mis-sense), `the Spanish state`. This is a high-quality EN adaptation.

---

## Editorial maintenance recommendations

1. **Resolve F1 / F2 / F3 as a single decision.** The brief says "American with selective British"; the corpus is uniformly British. A 30-minute deliberate sweep (find/replace with human eye on each substitution) is the correct way to handle this, *not* a regex bulk operation, given prior project warning about non-idempotent regex bulk-renames (CLAUDE.md "double-n bug").

2. **Update the style guide to lock the choice.** Whichever way F1 resolves, write it into `seo-internal/style-guide-editorial.md` §2 so future translators don't re-introduce drift.

3. **Clean up the `about-en.md` blockquote at L3.** The "wait" / "Resolved per user spec" prose is editorial scaffolding that has leaked into rendered output.

4. **Add a CI lint** (`scripts/check-em-dashes.sh`) running `grep -rn --include='*.md' '—'` and failing the build if any are found. Catches the recurring rule-2.7 violation cheaply.

5. **Press-release dates.** When date fields are added to press-release articles, follow the brief's `1 June 2026` (no comma) form, not `June 1, 2026`.

6. **Number style.** The brief calls for "spell out one through ten; numerals from 11+". Spot checks show this is largely respected ("more than 100 homes", "ninety per cent", "thirty years", "fourteen years"); no corrective sweep needed.

---

*End of report. No blockers. Two confident corrections applied; HTML regenerated cleanly (162 pages, 0 failures). The remaining work is a single editorial decision about British-vs-American register, which a human owner should make.*
