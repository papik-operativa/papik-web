# Copy EN · Cookie policy · `/en/cookie-policy` · placeholder v0.1 pending legal review

> WARNING · PLACEHOLDER · `[XXX]` fields and the cookie table must be completed by legal counsel and the development team before publication. Structure based on Spanish Data Protection Agency (AEPD) guidance and the EU General Data Protection Regulation (GDPR, Regulation EU 2016/679). DO NOT publish without sign-off from the designated lawyer.

---

## META TAGS

```html
<title>Cookie policy · PAPIK Group</title>
<meta name="description" content="PAPIK Group cookie policy: types of cookies used, purposes and how to manage them.">
<meta name="robots" content="index, follow">

<link rel="canonical" href="https://papik.cat/en/cookie-policy">
<link rel="alternate" hreflang="ca" href="https://papik.cat/politica-de-cookies">
<link rel="alternate" hreflang="es" href="https://papik.cat/es/politica-de-cookies">
<link rel="alternate" hreflang="en" href="https://papik.cat/en/cookie-policy">
<link rel="alternate" hreflang="x-default" href="https://papik.cat/politica-de-cookies">
<meta property="og:locale" content="en_US">
<meta property="article:section" content="Legal">
```

---

## H1

Cookie policy

## Last updated

`[DATE OF LEGAL APPROVAL · format DD/MM/YYYY]`

---

## 0 · Notice for international visitors

This site is operated by a Spanish company. Spanish Information Society Services Law (LSSI-CE), the EU General Data Protection Regulation (GDPR) and ePrivacy rules apply. Non-EU residents should review the international transfers section carefully, since some third-party cookies may transmit data outside the European Economic Area.

---

## 1 · What cookies are

Cookies are small text files that websites store on the user's device (computer, mobile phone or tablet) when visited. They allow the site to remember information about the visit, such as preferred language or browsing preferences, and can help with navigation, improve user experience, gather statistics or deliver personalised content.

This policy explains which cookies the website `https://papik.cat` uses, for what purpose, and how the user can manage them.

---

## 2 · Types of cookies used

### By ownership

```
First-party cookies: those sent to the user's device from a system or domain managed by PAPIK Group.

Third-party cookies: those sent to the user's device from a system or domain that is not managed by PAPIK Group, but by another organisation that processes the data obtained through the cookies.
```

### By purpose

```
Strictly necessary or technical cookies: enable the user to navigate the website and use its features. These do not require consent.

Preference or personalisation cookies: remember information so the user accesses the website with certain settings (language, region, etc.).

Analytical or statistical cookies: count the number of users and analyse their behaviour on the website to support service improvement.

Advertising or behavioural advertising cookies: manage advertising and, where applicable, deliver advertising content tailored to the browsing profile.
```

### By duration

```
Session cookies: deleted when the browser is closed.

Persistent cookies: remain on the device for a defined period, ranging from minutes to several years.
```

---

## 3 · Cookies used on this website

`[This table must be completed by the development team before publication, with the cookies actually deployed. Suggested format:]`

```
COOKIE              | OWNER          | PURPOSE                        | DURATION     | TYPE
──────────────────────────────────────────────────────────────────────────────────────
[COOKIE_NAME]       | PAPIK Group    | [PURPOSE DESCRIPTION]          | [DURATION]   | Technical
[COOKIE_NAME]       | Google         | Web traffic analytics          | 24 months    | Analytical · third-party
[COOKIE_NAME]       | Meta           | Advertising pixel (if active)  | [DURATION]   | Advertising · third-party
[COOKIE_NAME]       | [PROVIDER]     | [PURPOSE]                      | [DURATION]   | [TYPE]
```

`[The development team must audit cookies actually installed using a cookie scan tool before the first deployment.]`

---

## 4 · User consent

In accordance with article 22.2 of Law 34/2002 (Spanish Information Society Services Law, LSSI-CE) and the EU General Data Protection Regulation (GDPR, Regulation EU 2016/679), PAPIK Group requests the user's express consent to install cookies that are not strictly necessary.

On the first visit to the website, the user receives an information notice and can:

```
A · Accept all cookies.
B · Reject cookies that are not strictly necessary.
C · Configure each category individually to accept or reject.
```

The user can change their cookie preferences at any time through the configuration panel accessible at the foot of the website.

---

## 5 · How to disable or remove cookies

The user can configure their browser to accept, reject or remove cookies. The following links provide official information for each browser:

```
· Google Chrome: https://support.google.com/chrome/answer/95647
· Mozilla Firefox: https://support.mozilla.org/kb/enable-and-disable-cookies-website-preferences
· Safari: https://support.apple.com/guide/safari/manage-cookies-sfri11471/mac
· Microsoft Edge: https://support.microsoft.com/microsoft-edge/delete-cookies-in-microsoft-edge-63947406-40ac-c3b8-57b9-2a946a29ae09
```

These links may change; in that case the user can consult the help menu of their browser for up-to-date instructions.

Disabling strictly necessary cookies may affect the functioning of the website.

---

## 6 · Retention and processing of data

Data obtained through cookies is kept for the periods indicated in the table in section 3. Once the period has expired, the data is deleted or anonymised.

The processing of data obtained through cookies is governed by our [Privacy policy](/en/privacy-policy).

---

## 7 · International transfers

Some third-party cookies may involve international transfers of data outside the European Economic Area (in particular cookies from Google, Meta and other platforms based in the United States). In these cases, the relevant providers apply the safeguards required by the GDPR: Standard Contractual Clauses (SCCs), an adequacy decision from the European Commission, or self-certification under the EU-US Data Privacy Framework (DPF) where applicable.

After the Court of Justice's Schrems II ruling (case C-311/18), PAPIK Group performs a transfer impact assessment for each non-EEA processor and applies additional technical and organisational measures where appropriate.

Users have the right to ask which third countries their cookie data is transferred to and which safeguard applies in each case. Requests can be sent to `[DPO EMAIL OR GENERAL EMAIL]`.

`[Confirm with the development team which external providers are active and review the transfer policy of each one.]`

---

## 8 · Modifications

PAPIK Group reserves the right to modify this cookie policy to adapt it to legislative, technological or operational changes. The version in force is always the one published on the website with the last update date indicated at the top of the document.

---

## 9 · Contact

For any query about this cookie policy, the user can write to `[DPO EMAIL OR GENERAL EMAIL]`.

---

## OPERATIONAL NOTES (not published)

### Fields to complete before publication

`[COOKIE_NAME]` and metadata in the section 3 table: the development team must complete this with a real cookie scan before deployment. Categories typically expected at PAPIK: technical (session, language), analytical (Google Analytics 4 or Plausible), advertising (Meta Pixel if active), preferences (cookie consent state).

### Cookie banner

Implement the banner in line with AEPD 2024 guidance: three equivalent options (accept all, reject all, configure). Do NOT accept consent through scrolling alone. Granular acceptance per category. Consent log with timestamp.

### JSON-LD schema

`06-breadcrumb.json` (Home, Cookie policy).

### Mandatory review

A lawyer specialised in GDPR and LSSI-CE plus a frontend developer with consent-management expertise must validate:
- Banner aligned with AEPD 2024 guidance
- Accurate cookie scan
- Consistency between declared categories and cookies actually deployed
- Operation of the preference management panel
- Consent log with timestamp

### Cookie scan

Recommended tools: Cookiebot scan, OneTrust audit or equivalent. Minimum frequency: quarterly.

### Template reference

Structure aligned with the AEPD's "Guide on the use of cookies" (2024 version) and with European Data Protection Board guidance. Adapted to PAPIK Group's typical technology stack (static site with analytics and possible advertising pixels) and to an international audience.
