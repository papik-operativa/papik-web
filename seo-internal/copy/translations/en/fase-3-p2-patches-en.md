# Patches EN · phase 3 P2 · 6 articles · cultural adaptation from v2 CA

> English version with the three amendments applied. These 6 articles were already in good editorial shape in v1, which is why this document defines only the necessary modifications (not full rewrites). All copy suggestions are in v1.1 register.

---

## Cross-cutting application to all 6

Each of the 6 articles must incorporate the same structural additions.

### Visible byline in the UI under the H1

```html
<div class="article-byline">
  Technical team · PAPIK Group
  <span class="separator">·</span>
  <time datetime="[YYYY-MM-DD]">[Publication date]</time>
  <span class="separator">·</span>
  Approximate reading time [X] min
</div>
```

### `Article` JSON-LD schema

Inserted in the `<head>` of each article. The template to use is the following, with the marked fields replaced by real values before publishing.

```html
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "Article",
  "headline": "[EXACT H1]",
  "description": "[META DESCRIPTION]",
  "image": "https://papik.cat/img/articles/[slug]/hero.jpg",
  "datePublished": "[YYYY-MM-DD]",
  "dateModified": "[YYYY-MM-DD]",
  "author": {
    "@type": "Organization",
    "name": "PAPIK Group",
    "url": "https://papik.cat"
  },
  "publisher": { "@id": "https://papik.cat/#org" },
  "mainEntityOfPage": {
    "@type": "WebPage",
    "@id": "[CANONICAL URL]"
  },
  "articleSection": "[SECTION]",
  "wordCount": [INT],
  "inLanguage": "en-US",
  "isAccessibleForFree": true
}
</script>
```

In addition, each article adds `BreadcrumbList` (Home, Blog, [article title]) as a universal schema.

### v1.1 verification of the body copy

Regardless of the specific changes, the dev or copywriter must review the body of each article to detect and remove em-dashes (which are replaced with commas, colons or full stops depending on context), apply the adult register without didactic phrases such as "imagine", "let's see" or "it is important to highlight", and convert vertical lists into argumentative paragraphs except in the cases foreseen by the style guide (numbered processes, heterogeneous taxonomies, operational checklists).

---

## 1 · article-casa-montseny · P2

**Current title:** "A sustainable house on the slopes of the Montseny | PAPIK" (56 chars). Kept.

**Current meta description:** within range. Kept.

**Specific changes:**

Add byline with publication date in the UI. Add `Article` schema with `articleSection: "Case studies"`. Reinforce the final cross-linking with three recommended links: the rewritten article on [Sustainable materials](/en/article-sustainable-materials), the rewritten article on [The ecological footprint of building and living in your home](/en/article-ecological-footprint), and the link to the gallery [See other projects in the area](/projectes). Add CTA at the end if not already present: "Request a visit to a similar project site → contact".

If the content mentions the figure of "23.90 tonnes of CO₂ saved", verify with PAPIK that the figure comes from the PHPP calculation of the project itself (not a general extrapolation). If valid, keep it with an internal citation to the simulation; if not, soften to "significant cumulative savings" without a specific figure.

**Estimated effort:** 20 minutes.

---

## 2 · article-hipoteca-energetica · P2

**Current title:** "What is the green mortgage? | PAPIK" (48 chars). Below the optimal range by two characters.

**Proposed title:** "What is the green mortgage and when it is worth it | PAPIK" (54 chars). This title slightly broadens the promised content without exceeding the ideal range.

**Proposed meta description:** "What a green mortgage is and what savings it brings over the years for high energy efficiency homes. Detailed guide by PAPIK." (147 chars).

**Specific changes:**

Rename title according to the proposal. Add byline with date. Add `Article` schema with `articleSection: "Financing and mortgages"`. Add a prominent cross-link to the rewritten article [Green mortgage for Passivhaus: the agreement between PAPIK and Banc Sabadell](/article-nota-premsa-papik-sabadell), since this article complements the general content on green mortgages with the specific case of the PAPIK and Sabadell agreement. Consider adding an FAQ block with 3 or 4 questions (what it is exactly, how to apply, what differentiates it from a conventional mortgage, typical requirements) accompanied by `FAQPage` schema.

**Estimated effort:** 35 minutes.

---

## 3 · article-principis-passivhaus · P2

**Current title:** "The five Passivhaus principles | PAPIK" (55 chars). Kept.

**Current meta description:** within range. Kept.

**Specific changes:**

Add byline with date. Add `Article` schema with `articleSection: "Passivhaus technical"`. Reinforce internal linking, since this article is the pillar of the Passivhaus cluster and must connect with the other technical articles: [Key Passivhaus technologies 2026](/en/article-passivhaus-technologies), [Passivhaus innovations 2026](/en/article-passivhaus-innovations), [Why you breathe better in a Passivhaus house?](/article-ventilacio-passivhaus) and [Sustainability and Passivhaus](/article-sostenibilitat-passivhaus). Add CTA at the end: "Configure the budget for my Passivhaus house → /pressupost".

**Estimated effort:** 20 minutes.

---

## 4 · article-revolucio-fusta · P2

**Current title:** "The wood revolution · super-resistant wooden houses | PAPIK" (60 chars). Within range, but the word "revolution" may be a baseless superlative if the article does not cite a specific scientific study.

**Mandatory prior action:** verify with the original author the source of the figure cited in the body of the article (reference to "self-densified wood with nine times higher resistance" or similar). If the source is solid (specific academic study with DOI or URL), add an inline citation to the text and keep the title with the word "revolution" justified by the data. If the source is weak or non-existent, soften the body of the text to a more moderate construction such as "wood with significantly higher resistance" and adjust the title to "Super-resistant wood: the future of construction materials | PAPIK" (62 chars).

**Specific changes:**

Once the above points are resolved, add byline with date. Add `Article` schema with `articleSection: "Materials and technology"`. Add cross-links to [Sustainable materials](/en/article-sustainable-materials) and [Passivhaus innovations 2026](/en/article-passivhaus-innovations). Add CTA at the end.

**Estimated effort:** 30 minutes (depends on source verification).

⚠ PAPIK action: clarify with the original author the source of the "9× resistance" figure before applying the patch.

---

## 5 · article-sostenibilitat-passivhaus · P2

**Current title:** "Passivhaus and sustainability · how to minimise the ecological footprint | PAPIK" (58 chars). Within range, kept.

**Alternative proposed title (only if simplification is desired):** "Passivhaus and sustainability: minimising the ecological footprint | PAPIK" (61 chars). Replaces the middle dot with a colon, in line with the v1.1 rule that limits the middle dot as an ornamental device.

**Current meta description:** within range. Kept.

**Specific changes:**

Add byline with date. Add `Article` schema with `articleSection: "Passivhaus technical"`. Prominent cross-link to [The ecological footprint of building and living in your home](/en/article-ecological-footprint), which is the complementary article with the detailed LCA calculation. Add cross-links to [The five Passivhaus principles](/en/article-passivhaus-principles) and [Sustainable materials](/en/article-sustainable-materials). Add CTA at the end: "Configure the budget for my project → /pressupost".

**Estimated effort:** 20 minutes.

---

## 6 · article-ventilacio-passivhaus · P2

**Current title:** "Why you breathe better in a Passivhaus house? | PAPIK" (60 chars). Within range, kept.

**Current meta description:** within range. Kept.

**Mandatory prior action:** locate a specific source for the figure "5 times more polluted" if it appears in the body of the text. Valid sources for this claim are the IAQ (Indoor Air Quality) studies by the EPA (Environmental Protection Agency of the United States), the indoor air quality reports by the WHO (World Health Organization), or the BPIE (Building Performance Institute Europe) studies on European homes. If located, add an inline citation to the text in the format "(EPA · indoor air quality studies, 2023)" or equivalent. If it cannot be located, adjust the text to a more general construction such as "up to several times more polluted than the outside" without a specific figure.

**Specific changes:**

Once the above points are resolved, add byline with date. Add `Article` schema and consider `FAQPage` for the usual questions about ventilation. Add cross-links to [Key Passivhaus technologies 2026](/en/article-passivhaus-technologies) and [The five Passivhaus principles](/en/article-passivhaus-principles). Add CTA at the end: "Configure the budget for my house with HRV → /pressupost".

**Estimated effort:** 30 minutes.

⚠ PAPIK action: validate the source of the "5×" figure before publishing.

---

## Total effort summary phase 3 P2

The complete application of the patches to the 6 articles requires between 2 hours 35 minutes and 3 hours in total, broken down as follows:

The casa-montseny article needs 20 minutes (schema, byline and cross-links). The hipoteca-energetica article needs 35 minutes (refinement of title and meta description, schema, cross-link to Sabadell). The principis-passivhaus article needs 20 minutes (schema, byline and cluster linking). The revolucio-fusta article needs 30 minutes depending on source verification. The sostenibilitat-passivhaus article needs 20 minutes (schema and linking to petjada-ecologica). The ventilacio-passivhaus article needs 30 minutes depending on source verification.

---

## Pending external validations

Three points require external verification before publishing, with a direct response from PAPIK:

The source of the "9× resistance" figure in article-revolucio-fusta. What is the original study or technical article from which this figure comes?

The source of the "5× indoor pollution" figure in article-ventilacio-passivhaus. EPA, WHO, BPIE or another source?

The validation of "23.90 tonnes CO₂" in article-casa-montseny against the PHPP calculation of the specific project. Does the figure come from a real simulation calculation or is it a general extrapolation?

If in any case the source cannot be located, soften the copy to a more general version without a specific figure. The rule is: no quantitative data in public copy without a verifiable source.

---

## Practical application · how the dev does this

For each article in phase 3 P2, the process to follow is the following.

First, open the file `/public/article-[slug].html`. Second, apply the specific changes according to this patches document. Third, verify on the CA that the byline and the date are visible in the UI, not only in the schema. Fourth, validate the schema with Google's Rich Results Test. Fifth, verify that the cross-links work correctly and do not lead to 404s. Sixth, replicate all changes in the ES version (`/es/article-[slug-translated].html`) if it exists. Seventh, regenerate the sitemap.xml by running `python3 generate_sitemap.py`. Eighth, commit with a clear message such as "P2 patches v1.1: schema, byline, cross-links · 6 existing articles".

Each patch is applicable in less than 30 minutes per article. The total for the 6 articles is between 2 and 3 hours, with an exceptional SEO impact to time invested ratio.

---

## Changes from patches v1

The copy suggestions in this v2 document are all in v1.1 register. Middle dots have been removed as ornamental separators within sentences and replaced with commas or full stops depending on context. The didactic phrases present in v1 (such as "vamos a ver" in Spanish or "vegem" in Catalan in some copy proposals) have been removed. The vertical lists of frequent errors and types of changes to apply have been converted to continuous text or argumentative paragraphs. The "patches per article" structure is kept because it is an operational format inherent to the document (each article has its own specific changes) and not an ornamental list.

---

## Closing of the v1.1 batch

This document closes the v1.1 batch at 100%. The 23 CA copy files (including this patches document) are now aligned with the v1.1 editorial style manual. The next logical move is the translation into ES of the 22 v1.1 files with lexical adaptations, and subsequently the creation of EN versions with cultural adaptation in line with the planning of week 4 (S4) of the pre-launch calendar.
