# Legal Review · PAPIK Web v1.1

> WARNING / DISCLAIMER · This is an AI-generated shadow legal review for internal triage purposes. It does NOT constitute legal advice and does NOT replace the mandatory pre-publication review by qualified Spanish counsel specialized in LSSI-CE, RGPD/LOPDGDD, CNMV/MiFID II, and Ley de Propiedad Horizontal (LPH). Its purpose is to surface potential compliance gaps and prioritize the issues that the human lawyer must focus on before publication. No reliance should be placed on this memorandum for any operational, contractual or commercial decision.

Date: 2026-04-28
Reviewer (shadow): AI legal-review agent acting as Spanish digital + real-estate + financial-law firm equivalent.
Reviewed material: 12 files (6 legal placeholders CA + ES, plus 6 pages with regulatory disclaimers — `/patrimonis`, `/rehabilitacio/comunitats`, `/rehabilitacio`, articles Sabadell, Ponsa, hipoteca energètica).

---

## Executive summary

Overall compliance posture is **well above the average for a Spanish construction-sector website at draft stage**. The legal placeholders (Avís legal, Política de privacitat, Política de cookies) are structurally sound and follow the canonical LSSI-CE / RGPD / LOPDGDD scaffolding, but they are explicitly marked as `[XXX]` placeholders and CANNOT be published as-is — every identification field, the DPO determination, the international transfers section, and the cookie inventory are open. The pages with sectoral disclaimers (Patrimonis, Comunitats, Rehabilitació, the three articles) reflect notable regulatory awareness: the copy actively avoids the most dangerous patterns (no "invertir" CTAs, no published mortgage rates, no nominal identification of co-investment partners other than Ponsa, no promised yield). The principal residual exposure concerns (i) the Ponsa article (publication of the 2 M€ figure plus surname, requires CNMV-specialized counsel sign-off), (ii) the absence of a DPO/contact point and of a defined international-transfers regime, (iii) the cookie banner's actual technical implementation (which the report cannot audit), and (iv) some softening of the LPH quorum language. **Status: REVISE BEFORE COUNSEL REVIEW** for the items flagged CRITICAL/HIGH below; thereafter ready for qualified counsel sign-off. Estimated counsel time: **9–13 hours** total across the four specializations.

---

## Severity classification

- **CRITICAL** — non-compliant if published as-is; will trigger immediate AEPD/CNMV exposure or legal liability.
- **HIGH** — compliance gap with known enforcement risk; counsel must address before publication.
- **MEDIUM** — best-practice gap; counsel should address, not necessarily blocking.
- **LOW** — drafting suggestion / clarification.

---

## Findings by file

### 1. Avís legal CA (`avis-legal-ca-v2.md`) + Aviso legal ES (`aviso-legal-es.md`)

**Posture: STRUCTURALLY OK · CRITICAL gaps in placeholder data · HIGH gaps in two specific clauses.**

CA and ES versions are mirror translations and share findings.

- **CRITICAL · Placeholder identification data.** All Art. 10 LSSI-CE fields are `[XXX]`: denominación social, NIF, domicilio social, teléfono, email, datos registrales (tomo, folio, hoja). LSSI-CE Art. 10.1.a–c requires these to be "permanent, easy, direct and free of charge". Cannot publish without filling. **Action**: legal/admin must populate from registro mercantil certificate.
- **HIGH · "Eskimohaus®" trademark assertion (Section 4).** Both versions assert the registered trademark unilaterally. Verify: (i) actual OEPM/EUIPO registration number, (ii) classes registered, (iii) ownership in the same legal entity that owns the website — if Eskimohaus® is held by a different group entity than the website operator, the language must be adjusted ("propietat de [entitat titular] del PAPIK Group" or similar). This is a frequent corporate-group mismatch and should be confirmed.
- **HIGH · Submission to jurisdiction (Section 9).** The clause submits disputes to the courts of `[CIUTAT DE LA SEU FISCAL]` "with express waiver of any other forum". Under Art. 90.2 TRLGDCU and Art. 25 LEC, a B2C jurisdiction-waiver clause is **abusive and null** when imposed on a consumer. The text already contains the consumer carve-out in the second paragraph, which is good, but the wording would be stronger if the carve-out were placed in the same paragraph and the "renuncia expressa" applies only to non-consumer relationships.
- **MEDIUM · Section 5 limitation of liability.** "PAPIK Group no es responsabiliza de los daños... salvo en los casos en que dicha responsabilidad resulte exigible por disposición legal imperativa" — fine for the website use case, but note that under Art. 1.105 CC and consumer protection rules a generic exclusion is limited; current wording is acceptable but counsel should validate.
- **MEDIUM · Identification of regulated activity.** LSSI-CE Art. 10.1.d–f require disclosure of authorisations, professional codes, and regulated profession data. None are listed; this is correct **only if** PAPIK does not require any registration as constructor/promoter (e.g. Registro de Empresas Acreditadas — REA — applicable to construction sector, mandatory in Catalonia and Spain). Counsel should confirm whether REA registration / promotor inmobiliario registry data should appear.
- **LOW · Arbitration clause absent.** Not mandatory; consider whether to mention adhesion to Confianza Online / arbitraje de consumo.

### 2. Política de privacitat CA (`politica-privacitat-ca-v2.md`) + Política de privacidad ES (`politica-privacidad-es.md`)

**Posture: STRUCTURALLY SOLID · CRITICAL placeholders · HIGH gap on DPO and international transfers · MEDIUM gaps elsewhere.**

- **CRITICAL · Placeholder identification.** Responsable identification fields blank. Same as Aviso legal. Cannot publish.
- **CRITICAL · International transfers (Section 6).** Section is left as `[XXX]` but the Cookies policy (Section 7) explicitly states transfers to Google, Meta, US providers occur. The two documents will be **internally inconsistent** if transfers are denied here while affirmed there. After Schrems II (CJEU C-311/18) and the EU-US Data Privacy Framework (2023), counsel must (a) confirm whether the chosen tooling (GA4, Meta Pixel, hosting) operates under the DPF certification, (b) document SCCs where DPF does not apply, and (c) include a Transfer Impact Assessment (TIA) reference. **Critical because mis-disclosure of transfers is one of the top AEPD enforcement themes (2023–2025)**.
- **HIGH · DPO designation.** Section 1 leaves DPO mention "if applicable". Under Art. 37 RGPD + Art. 34 LOPDGDD, designation is mandatory if (i) public authority, (ii) core activities require regular and systematic monitoring on a large scale, or (iii) core activities involve large-scale processing of special categories. PAPIK as constructora premium **likely does NOT trigger mandatory DPO** under Art. 37 RGPD (no large-scale special data, no systematic monitoring as core activity), **but Art. 34 LOPDGDD lists 16 specific cases** that include real-estate developers in some interpretations. **Counsel decision required** — the Spanish AEPD has fined construction/promotion firms for absent DPO under Art. 34.j LOPDGDD when activity includes habitual financing intermediation. Given that PAPIK promotes mortgage facilitation (Sabadell article), this risk should be specifically analysed.
- **HIGH · Legitimate interest balancing test (Section 3, finalitat E).** The text invokes Art. 6.1.f for "agregated statistics" but provides no record of the LIA (legitimate interest assessment). RGPD Recital 47 + EDPB Guidelines 2024 require a documented balancing test available on request. **Action**: counsel + DPO must produce the LIA document and store it; the policy can remain as-is but the underlying record must exist.
- **HIGH · Article 14 RGPD (data not obtained from the data subject).** Policy only addresses Art. 13 (direct collection). If PAPIK obtains data from third parties — e.g. property administrators referring communities, real-estate brokers passing leads, banks referring mortgage candidates — Art. 14 informational obligations apply with different deadlines (max 1 month). **The Comunitats and Sabadell pages strongly suggest this data flow exists.** Section dedicated to Art. 14 is missing.
- **MEDIUM · Information layer coherence (Art. 11 LOPDGDD).** The policy is the "second layer". The "first layer" must appear on each form. Operative note in the file flags this — counsel must verify each form (contact, budget, calculator, NDA request, comunitat diagnosis) embeds the short notice + link.
- **MEDIUM · Conservation of "leads" (Section 4).** "Hasta 12 meses salvo que el usuario consienta expresamente un plazo superior" — acceptable. However Art. 32 LSSI-CE for marketing communications and the LSSI 14-day soft-opt-out window are not addressed. Counsel should review whether soft opt-in for ex-customers (Art. 21.2 LSSI-CE) is being used and disclosed.
- **MEDIUM · Right to lodge complaint with AEPD.** Disclosed (Section 8) — OK. Add explicit reference that AEPD has online complaints portal `https://sedeagpd.gob.es/sede-electronica-web`.
- **LOW · Form-level granular consent.** Should specify that consent for marketing is separated from consent to process data for the requested service (granularity requirement, EDPB Guidelines 5/2020).

### 3. Política de cookies CA (`politica-cookies-ca-v2.md`) + Política de cookies ES (`politica-cookies-es.md`)

**Posture: STRUCTURALLY OK · CRITICAL operational gap (cookie inventory + banner) · HIGH gap on consent storage.**

- **CRITICAL · Cookie inventory missing.** Section 3 is fully bracketed `[NOMBRE_COOKIE]`. AEPD Guía sobre el uso de cookies 2024 (rev. November 2023) requires actual cookies, owner, purpose, retention, type. Cannot publish without scan.
- **CRITICAL · Banner implementation cannot be audited from copy alone.** The policy describes the three equivalent options correctly (accept / reject / configure), but enforcement depends on the actual banner. AEPD has issued multiple resolutions in 2023–2025 fining sites where:
  - reject button is visually less prominent than accept,
  - "configure" requires more clicks than "accept all",
  - cookies are dropped before consent (especially Google Analytics, Meta Pixel),
  - "continue browsing" or scroll is treated as consent (now expressly forbidden).
  **Action**: dev + counsel jointly must validate live banner. The site cannot be considered compliant on cookies until banner is verified.
- **HIGH · Consent registry (timestamp + version).** Operative notes mention this but the published policy itself does not state HOW long the consent record is kept and where (controller log). Best practice (and AEPD recommendation) is to disclose a consent-retention term (typically 24 months) in the policy.
- **HIGH · International transfers (Section 7).** Acknowledges transfers to US (Google, Meta) under SCC/adequacy. Need to confirm: (i) whether providers are DPF-certified as of publication date — DPF list is dynamic; (ii) whether Google Analytics is configured in EU-only mode + IP anonymisation; (iii) whether Meta Pixel uses CAPI server-side with hashing. The cookie policy should explicitly cite the DPF mechanism if used.
- **MEDIUM · Period for revocation.** Policy says user "can modify preferences at any time from the footer panel" — confirm the revocation must be **as easy as the original consent** (Art. 7.3 RGPD); that means a one-click revocation path, not a multi-step settings menu.
- **MEDIUM · Children's cookies.** AEPD 2024 guide requires specific reference if site is targeted to or used by minors; PAPIK is B2B/premium-residential, not for minors — explicit statement to that effect would close any ambiguity.
- **LOW · Browser deactivation links.** Provided but become outdated — already noted in copy. Acceptable.

### 4. `/patrimonis` disclaimer (CNMV / MiFID II) — `patrimonis-ca-v2.md`

**Posture: GOOD · the most regulatorily sensitive page; copy is well-disciplined; a few residual risks.**

- **HIGH · Public-offering threshold (Art. 35 TRLMV / Reglamento (UE) 2017/1129 Prospectus).** The page is informational and avoids public-solicitation language. CTA is "sol·licitar conversa confidencial", correct. **However**, the open availability of the page on the public website (indexed, `robots: index, follow` in the meta tags template) means a regulator could still consider it public communication. Counsel should validate whether `noindex` or login-gating is preferable for this page given the "private bilateral vehicle" positioning. **At minimum**, the page must not present any specific vehicle, ticket size, or expected return — current copy correctly avoids all three.
- **HIGH · Disclaimer text adequacy.** Current text covers (a) no public offering, (b) no financial instrument, (c) no MiFID II advice, (d) PAPIK not registered as ESI/IIC manager, (e) bilateral vehicles + independent counsel. **Missing**: explicit statement that the page is **not directed to retail investors** as defined by Art. 205 TRLMV / MiFID II Annex II — recommended to add.
- **MEDIUM · "Vehicle" terminology.** The page uses "vehicle de coinversió" repeatedly — neutral term, good. Avoid in any future revision the words "fondo", "participación", "rentabilidad esperada", "TIR" — current text correctly avoids these.
- **MEDIUM · FAQ "PAPIK aporta capital propi al vehicle? En alguns casos sí" (Block 7).** This is fine but the same FAQ creates the impression that PAPIK can be a co-investor. Combined with the Ponsa article (publicly disclosing one specific vehicle), a regulator may scrutinise whether PAPIK's repeated participation across multiple vehicles constitutes habitual professional financial intermediation. **Counsel must validate the structural test** (Art. 144 TRLMV) — specifically whether PAPIK's role triggers habitualidad.
- **MEDIUM · Use of "track record" + cases table (Block 5).** Cases are anonymised (geographic zone + scale + state). Acceptable — but ensure no internal documentation under NDA reveals investor identities to subsequent prospects without consent.
- **LOW · "Track record" phrasing.** Typical of fund material. Counsel may suggest "experiència" or "trajectòria" as safer Catalan equivalent free of financial-services connotation.
- **LOW · No FinancialProduct schema.** Operative note correctly forbids it. Confirmed compliant.

### 5. `/rehabilitacio/comunitats` disclaimer (LPH Art. 17) — `comunitats-ca-v2.md`

**Posture: OK with HIGH wording risk on quorum citation.**

- **HIGH · Quorum citation (Block 2.5 + Block 8 FAQ + Disclaimer).** The copy states: "la Llei 49/1960 de Propietat Horitzontal (article 17.2) estableix la majoria de tres cinquenes parts dels propietaris i de les seves quotes". This is the **classic quorum** but the regulatory landscape for energy retrofits has shifted:
  - Real Decreto-ley 19/2021 (rehabilitación NGEU) modified Art. 17.2 LPH, easing the quorum for **specific** energy-efficiency works funded by NGEU (in some cases reducible to **simple majority** for certain mejoras).
  - Ley 10/2022 (medidas urgentes rehabilitación) introduced further tweaks.
  - The page acknowledges "en alguns supòsits aplica majoria simple" but does not cite the specific RDL/Ley. **Counsel should rewrite to cite Ley 49/1960 modified by RDL 19/2021 and Ley 10/2022** to be both accurate and authoritative, since this is the single most operationally relevant question community administrators ask.
  - The phrase "Aquesta pàgina és informativa i no constitueix assessorament jurídic" in the disclaimer is appropriate and protects PAPIK from professional-advice claims.
- **MEDIUM · "Departament tècnic delegat" framing.** Operative note correctly forbids co-branding. The phrase "departament tècnic delegat dels administradors de finques" is borderline — could be misread as PAPIK being subordinated to the administrator (good), or as the administrator being legally responsible for PAPIK's technical work (bad, mixes liability). Counsel should validate the contractual framework (services contract or subcontract).
- **MEDIUM · NGEU subsidy percentages (Block 2.2).** The page states three brackets: 30–45% saving = 40% subsidy, 45–60% = 65%, >60% = 80%. These match RD 853/2021 (Programa 3) but the regulation has been amended (RD 691/2023, plus subsequent BOE updates). **Counsel must verify percentages are still current as of publication date** — the operative note already requires this, good.
- **MEDIUM · Discretion on "subvenció obtinguda en rang 60-70%" (Block 7 cases).** Good practice: range, not exact. Maintain.
- **LOW · Form pre-qualification (Block 6) — data minimisation.** "Adreça aproximada (zona o municipi · NO carrer concret)" — well done. Aligned with Art. 5.1.c RGPD.

### 6. `/rehabilitacio` disclaimer (NGEU) — `rehabilitacio-ca-v2.md`

**Posture: OK with MEDIUM gaps on date/normative drift.**

- **MEDIUM · Programme expiration (Hero).** "SUBVENCIONS NEXT GENERATION VIGENTS FINS DESEMBRE 2026". Programmes 3/4/5 currently target 31/12/2026. Counsel must verify there has not been a fresh extension or restriction in the BOE between draft date and publication. Operative checklist already requires this, good.
- **MEDIUM · "Fins al 80%" headline number.** Compliant only if the 80% bracket is still in force AND the user reads the qualifier "segons l'estalvi energètic aconseguit". Some AEPD/Consumo precedents have penalised promotional use of maximum-bracket numbers without immediate qualifier. Current copy provides qualifier in next line — acceptable.
- **MEDIUM · "Revalorització +15-25%" (Block 1, Card 3).** Cites "Sociedad de Tasación, Idealista Data". Good practice (source citation reduces deceptive-advertising risk under Ley General de Publicidad and LCGC). Counsel should verify the cited studies are accessible publicly and recent.
- **MEDIUM · Calculator (Block 2).** Functional disclaimer is appropriate ("estimació orientativa"). When deployed, calculator output PDF must include same disclaimer as page footer + privacy notice on the form data (operative note flags this).
- **LOW · "Hipoteca verda" cross-link.** OK.
- **LOW · No financial-product schema.** Confirmed.

### 7. Articles Sabadell + Ponsa + Hipoteca energètica (group review · financial-law adjacency)

**Posture: GOOD overall · the Ponsa article is the highest-risk individual document of the entire set · the others are low-risk if disclaimers stay.**

#### 7a. `article-nota-premsa-papik-sabadell-ca-v2.md`

- **MEDIUM · "Hipoteca verda" + Ley 5/2019 (LCCI).** The article correctly says "PAPIK actua com a facilitador del canal, no com a part del contracte de préstec". This is the key sentence. It must remain. **Verify**: PAPIK does not perform any act that would qualify as "intermediario de crédito inmobiliario" under Art. 4.5 Ley 5/2019, which would trigger Banco de España registration. Mere referral of clients is generally outside the scope **if** PAPIK does not receive remuneration tied to mortgage formalisation. Counsel must confirm the contractual framework with Sabadell to ensure no such linkage exists, or that registration is in place.
- **MEDIUM · "Condicions privades i exclusives".** Correct strategy — no rates, no LTV, no terms published. Maintain absolutely.
- **MEDIUM · Disclaimer adequacy.** Current disclaimer states "no constitueix oferta vinculant de finançament". Should additionally mention: "ni assessorament financer regulat als efectes de MiFID II o de la Ley 5/2019" — recommended addition.
- **LOW · Schema marker.** Operative note correctly forbids `FinancialProduct`. Good.

#### 7b. `article-nota-premsa-papik-ponsa-ca-v2.md`

- **HIGH · Publication of "Família Ponsa" surname + "2 milions d'euros anuals".** The operative note states this is "a explicit decision of the client". From a strict legal-risk standpoint:
  - **Data protection / privacy of the Ponsa family.** Identifying a specific family by surname and associating them with a monetary commitment is processing of personal data of a private third party. RGPD applies. **Action required**: written documented consent from Ponsa family representatives authorising this exact phrasing and figure. Without that, publication is a CRITICAL gap.
  - **CNMV exposure.** Naming a specific co-investor and a specific yearly figure can be argued to fall short of public solicitation, but it edges close to disclosing a financial relationship that, repeated across other communiqués, builds up a pattern of public marketing of a private investment activity. **Counsel specialised in CNMV must validate this article specifically** — it is the highest-risk document of the entire set.
  - **Suggested mitigation** (if Ponsa consent exists): add a stronger disclaimer paragraph explicitly stating "L'esment de la família Ponsa es realitza amb el seu consentiment exprés. Aquest article no constitueix oferta de subscripció ni promoció de cap producte d'inversió, ni invitació a tercers a participar en el vehicle privat descrit".
- **HIGH · Article 14 RGPD obligation.** Indirect: PAPIK has the family's data and is processing it. Need a documented basis (Art. 6.1.a — consent — most defensible).
- **MEDIUM · "Acord estratègic per al desenvolupament conjunt".** Wording acceptable. The repeated reference to `/patrimonis` from this article reinforces a "service marketed publicly" reading — counsel should evaluate whether to remove or weaken those cross-links.
- **MEDIUM · "Capital pacient amb mandat sostenible".** Marketing language but not a financial promise. Acceptable.
- **LOW · Disclaimer.** Current disclaimer is correctly drafted. Add the "amb consentiment exprés" element noted above.

#### 7c. `article-hipoteca-energetica-ca-v2.md`

- **MEDIUM · Comparative figures (Sections 2–3).** Numbers (4.300 €/yr vs 540 €/yr; Passivhaus = 90% less; revaluation +15–25%) must be (i) supported by internal documentation ready for inspection (Ley 34/1988 General de Publicidad Art. 3 — deceptive advertising), (ii) qualified by methodology if challenged. Citations to "Sociedad de Tasación / Idealista Data" partially satisfy this. The €/kWh = 0,18 figure should be footnoted to a date ("preu mitjà residencial 2024 segons CNMC / Eurostat").
- **MEDIUM · "Hipoteca verda" facilitator language.** Same comment as Sabadell article. Maintain "PAPIK manté un acord amb Banc Sabadell per facilitar..." phrasing.
- **MEDIUM · Disclaimer adequacy.** Current disclaimer uses "cap menció d'entitats financeres no constitueix oferta vinculant ni assessorament financer regulat" — solid. Could be strengthened by adding an explicit reference to Ley 5/2019 LCCI as recommended for the Sabadell article.
- **LOW · "Assegurança contra la inflació energètica" metaphor.** Counsel may want to soften — "assegurança" in Spanish/Catalan financial context has regulated meaning; use "protecció" instead.

---

## Compliance gaps requiring counsel decision

| # | Item | Severity | Recommendation |
|---|------|---------|----------------|
| 1 | DPO designation under Art. 37 RGPD + Art. 34 LOPDGDD | HIGH | Counsel decision; document analysis in the Registro de Actividades de Tratamiento (RAT). |
| 2 | International transfers regime (GA4, Meta Pixel, hosting) | CRITICAL | Counsel + DPO must produce TIA + DPF/SCC documentation; harmonise privacy + cookies policies. |
| 3 | Ponsa article: surname + 2M€ figure | CRITICAL/HIGH | Obtain written consent from Ponsa representatives; CNMV-specialised counsel must sign off on the specific text. |
| 4 | LPH quorum citation (RDL 19/2021 + Ley 10/2022) | HIGH | Rewrite Block 2.5 + FAQ to cite specific reform statutes for energy works funded by NGEU. |
| 5 | NGEU percentages drift | MEDIUM | Quarterly verification policy + 7-day update commitment when BOE publishes amendment. |
| 6 | Cookies banner technical implementation | CRITICAL | Dev + counsel joint live audit before publication. |
| 7 | Mortgage facilitation under Ley 5/2019 | MEDIUM | Confirm PAPIK does not receive Sabadell remuneration tied to mortgage formalisation; if it does, registration as intermediario may be required. |
| 8 | Public-offering threshold for `/patrimonis` | HIGH | Decision: keep page indexed with current language, gate behind login, or noindex it. |
| 9 | Eskimohaus® trademark ownership chain | HIGH | Verify OEPM/EUIPO registration matches website operator entity. |
| 10 | Art. 14 RGPD section (data not from data subject) | HIGH | Add new section to privacy policy covering data received via administrators, brokers, banks. |
| 11 | LIA (Legitimate Interest Assessment) records | HIGH | Document and retain LIA for analytics processing. |
| 12 | Identification fields placeholders | CRITICAL | Populate all `[XXX]` from Registro Mercantil certificate; sign-off by counsel. |

---

## Specific text suggestions

### S1. Aviso legal · Section 9 (jurisdiction)

- **Location**: `aviso-legal-es.md` Section 9 + `avis-legal-ca-v2.md` Section 9.
- **Current**: "las partes se someten a los juzgados y tribunales de [CIUDAD], con renuncia expresa a cualquier otro fuero que pudiera corresponder. Si el usuario es consumidor [...] aplicará la jurisdicción correspondiente a su domicilio."
- **Proposed**: "En las relaciones con usuarios que no tengan la condición de consumidor, las partes se someten a los juzgados y tribunales de [CIUDAD]. Cuando el usuario tenga la condición de consumidor conforme al TRLGDCU, será competente el órgano jurisdiccional correspondiente a su domicilio, sin que dicha previsión pueda ser objeto de renuncia."
- **Rationale**: avoid the abusiveness presumption of Art. 90.2 TRLGDCU.

### S2. Política de privacidad · new Section 1.bis (DPO)

- **Location**: after Section 1.
- **Proposed (if no DPO designated)**: "PAPIK Group ha analizado la procedencia de designar Delegado de Protección de Datos (DPO) conforme al artículo 37 RGPD y al artículo 34 LOPDGDD. Tras dicho análisis, [no resulta obligatoria la designación / se ha designado a [NOMBRE], cuyos datos de contacto son [EMAIL DPO]]. En todo caso, las consultas en materia de protección de datos pueden dirigirse a [EMAIL]."
- **Rationale**: documents the analysis was performed, even if no DPO designated.

### S3. Política de privacidad · new Section 5.bis (Art. 14 RGPD)

- **Location**: after Section 5.
- **Proposed**: "Cuando PAPIK Group reciba datos personales de fuentes distintas al propio interesado (por ejemplo, datos facilitados por administradores de fincas, mediadores inmobiliarios o entidades financieras en el marco de operaciones gestionadas con su autorización), informará al interesado en los términos previstos en el artículo 14 RGPD en el plazo máximo de un mes desde la obtención de los datos."
- **Rationale**: closes Art. 14 gap.

### S4. Comunitats · Block 2.5 + Block 8 FAQ (LPH quorum)

- **Location**: `comunitats-ca-v2.md` 2.5 and FAQ Q1.
- **Current**: "la Llei 49/1960 de Propietat Horitzontal (article 17.2) estableix la majoria de tres cinquenes parts..."
- **Proposed**: "La Llei 49/1960 de Propietat Horitzontal, modificada per Reial Decret-llei 19/2021 i per Llei 10/2022, regula les majories aplicables segons el tipus d'obra. Per a obres de millora d'eficiència energètica que aprofitin subvencions públiques, l'article 17.2 LPH estableix com a regla general la majoria de tres cinquenes parts dels propietaris i de les seves quotes. La normativa especial vigent pot reduir aquest quòrum a majoria simple per a determinades actuacions energètiques, motiu pel qual cada cas concret s'ha de revisar amb l'administrador i la documentació jurídica de la comunitat."
- **Rationale**: accuracy + authority + maintains the existing "no asesoramiento" caveat.

### S5. Patrimonis · Disclaimer addendum

- **Location**: `patrimonis-ca-v2.md` Disclaimer block.
- **Add (after current text)**: "Aquest contingut no està dirigit a inversors minoristes en els termes definits per la Directiva 2014/65/UE (MiFID II) i pel Text Refós de la Llei del Mercat de Valors. La participació en qualsevol vehicle de coinversió privada queda reservada a perfils professionalitzats que comptin amb assessorament jurídic, fiscal i financer independent."
- **Rationale**: closes retail-investor exposure.

### S6. Ponsa article · Disclaimer addendum (only if consent obtained)

- **Location**: `article-nota-premsa-papik-ponsa-ca-v2.md` Disclaimer block.
- **Add**: "L'esment de la família Ponsa s'efectua amb el seu consentiment exprés i no constitueix oferta de subscripció, promoció de cap producte d'inversió, ni invitació a tercers a participar en el vehicle privat descrit. Cap acció d'aquest article no genera dret subjectiu de tercers a participar en col·laboracions similars."
- **Rationale**: hardens the CNMV defensive perimeter.

### S7. Sabadell + Hipoteca energètica · Disclaimer harmonisation

- **Location**: both articles' disclaimer blocks.
- **Add to both**: "PAPIK Group no actua com a intermediari de crèdit immobiliari als efectes de la Llei 5/2019, de 15 de març, reguladora dels contractes de crèdit immobiliari. La intermediació, en cas que es produeixi, queda reservada a entitats inscrites davant les autoritats competents."
- **Rationale**: clarifies LCCI status.

### S8. Cookies policy · Add explicit consent retention statement

- **Location**: Section 4 (Consentimiento del usuario).
- **Add**: "PAPIK Group conserva el registre del seu consentiment durant un termini màxim de 24 mesos, després del qual se sol·licitarà novament. Pot revocar el seu consentiment amb la mateixa facilitat amb què el va atorgar, des del panell accessible al peu del lloc web."
- **Rationale**: aligns with AEPD 2024 guidance + Art. 7.3 RGPD revocability.

---

## Items requiring counsel validation (cannot resolve at template level)

1. **DPO designation** — requires assessment of PAPIK's actual processing scale + whether Art. 34.j LOPDGDD applies given mortgage facilitation activity.
2. **Public-offering threshold for `/patrimonis`** — structural CNMV question depending on volume of bilateral vehicles, recurrence, and audience targeting.
3. **NGEU normative currency** — counsel must confirm RD 853/2021 + RD 691/2023 + any 2025–2026 amendments are still in force at publication; reviewer cannot validate as of 2026-04-27 without targeted research.
4. **LPH quorum case-by-case** — only a qualified LPH lawyer can validate the operational application of the reduced-quorum reforms to specific energy retrofits.
5. **Ley 5/2019 intermediary qualification** — depends on the actual contractual arrangement between PAPIK and Banc Sabadell, particularly remuneration structure.
6. **Eskimohaus® trademark ownership** — requires OEPM/EUIPO check.
7. **Schrems II / TIA** — requires DPO + counsel joint analysis of GA4, Meta Pixel, hosting providers as configured.
8. **Ponsa family consent + CNMV sign-off** — requires both written consent and CNMV-specialised counsel review of the specific article text.
9. **REA registration / promotor data in Aviso legal** — depends on whether PAPIK is registered as Empresa Acreditada in construction sector.
10. **B2C consumer-protection wording in Aviso legal** — counsel decision on whether to add additional consumer-protection clauses given the dual B2B/B2C nature of the site.

---

## Compliance posture by topic

| Topic | Posture | Counsel review urgency |
|---|---|---|
| LSSI-CE Art. 10 (Aviso legal) | Structurally OK · placeholder gaps | High (placeholder fill is blocking) |
| RGPD Art. 13 (Política de privacidad) | Structurally OK · Art. 14 missing · DPO undecided | High |
| LOPDGDD specifics (DPO, Art. 11 layered info) | Gaps | High |
| Cookies AEPD 2024 (policy) | OK | Medium |
| Cookies AEPD 2024 (banner technical) | Cannot audit from copy | Critical (live audit before publish) |
| CNMV / MiFID II (Patrimonis + Ponsa) | Acceptable but Ponsa is borderline | High (Ponsa specifically) |
| LPH Art. 17 (Comunitats) | Wording incomplete on reformed quorum | High |
| NGEU normative (RD 853/2021 + RD 691/2023 + posterior) | Acceptable + dependent on date verification | Medium |
| Mortgage / Ley 5/2019 LCCI (Sabadell + Hipoteca energètica) | Acceptable with disclaimer addendum recommended | Medium |
| Trademark Eskimohaus® | Asserted, ownership chain not verified | Medium |
| Consumer protection (TRLGDCU jurisdiction clause) | Adjustable | Low/Medium |

---

## Final recommendation

**REVISE BEFORE COUNSEL REVIEW.** Apply the following before opening counsel review file:

1. Populate all `[XXX]` identification fields in Aviso legal + Política de privacidad + Política de cookies (admin / financial team).
2. Apply text suggestions S1, S2, S3, S4, S5, S7, S8 (drafting).
3. Decide on Ponsa article publication — if proceeding, obtain written consent and apply S6.
4. Run cookie scan; complete Section 3 of the cookies policy with actual inventory.
5. Run live banner audit against AEPD 2024 guide.

After items 1–5, the package is **READY for qualified counsel review**.

---

## Estimated counsel review time

| Specialisation | Scope | Hours |
|---|---|---|
| LSSI-CE / e-commerce | Aviso legal full pass + jurisdiction clause + REA check | 1.5 |
| RGPD / LOPDGDD (DPO recommended) | Privacy policy + Art. 14 addition + DPO analysis + LIA review + form audit | 3.0 |
| RGPD + AEPD cookies guide | Cookies policy + live banner audit + TIA / DPF documentation | 2.0 |
| CNMV / MiFID II | `/patrimonis` + Ponsa article (most sensitive) + Sabadell article cross-check | 2.5 |
| LPH / horizontal property | `/rehabilitacio/comunitats` + reformed quorum citation rewrite | 1.0 |
| Ley 5/2019 LCCI | Sabadell + Hipoteca energètica + intermediary qualification analysis | 1.0 |
| Trademark | Eskimohaus® ownership verification (OEPM/EUIPO) | 0.5 |
| Coordination / final sign-off memo | Cross-document consistency check, sign-off | 1.0 |
| **Total** | | **12.5 h** (range 9–13 h depending on TIA depth) |

---

*End of memorandum.*
