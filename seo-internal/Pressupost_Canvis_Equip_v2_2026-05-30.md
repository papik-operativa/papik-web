# Canvis a la lògica de càlcul del pressupost · ITERACIÓ 2

> Recalibració completa contra 3 propostes econòmiques oficials PAPIK reals.
> Origen: CamScanner 29-5-26 17.43.pdf, 17.45.pdf, 17.46.pdf (5 pàgines cadascuna).
> Aquest document substitueix la primera versió (29-05-2026).

---

## 1 · Resum executiu

L'iteració 1 va aplicar literalment els ajustos manuscrits a IMG_3526-3534. **Va resultar incorrecte**: els valors manuscrits no coincideixen amb el càlcul oficial PAPIK. L'iteració 2 ha recalibrat tot el càlcul prenent com a font de veritat les 3 propostes econòmiques oficials.

### Comparativa final

| Cas | Configurador antic | Codi v2 | Oficial PAPIK |
|---|---:|---:|---:|
| 1 · Santa Coloma 140 m² · 2P | 368.950 € | 359.873 € | 454.637 € * |
| 2 · Barcelona 160 m² · 2P | 408.458 € | 396.620 € | 400.971 € ** |
| 3 · Barcelona 200 m² · 3P | 495.565 € | 420.514 € | 433.146 € *** |

\* CAS 1 inclou 20.000 € de piscina (no preguntada al configurador) i 52.000 € de fonamentació.
\*\* CAS 2 té dues anomalies a la PDF oficial: pòrxos no facturats i transport per 44 km en lloc de 23.
\*\*\* CAS 3: el client ja porta projecte i fonamentació, per això són 0 €.

### Acord pragmàtic

La fonamentació no es calcula al configurador. L'oficial PAPIK la marca sempre com a "pendent de valorar" (varia entre 0 € i 52.000 € segons terreny). Es mostra com a línia informativa amb estimació de 300 €/m² però NO se suma al total.

---

## 2 · Lògica nova del càlcul

### 2.1 · Pack envolvent tèrmic (€/m² per partida)

| Partida | 1 planta | 2 plantes | 3 plantes |
|---|---:|---:|---:|
| Estructura vertical | 480 €/m² | 555 €/m² | 555 €/m² |
| Coberta plana | 290 €/m² | 332 €/m² | 303 €/m² |
| Coberta teula | 275 €/m² | 315 €/m² | 288 €/m² |
| Coberta xapa | 247 €/m² | 282 €/m² | 258 €/m² |
| Finestres base S-72 | 222 €/m² | 222 €/m² | 222 €/m² |
| Suplement S-82 (+) | 5 €/m² | 5 €/m² | 5 €/m² |
| Suplement VMM-74 (+) | 25 €/m² | 25 €/m² | 25 €/m² |
| Suplement Supercomfort (+) | 50 €/m² | 50 €/m² | 50 €/m² |
| Porta entrada (fix) | 3.445,45 € | 3.445,45 € | 3.445,45 € |
| Grua (fix) | 858 € | 858 € | 858 € |

### 2.2 · Pack instal·lacions

| Concepte | Càlcul |
|---|---|
| Telecomunicacions | 2.423,55 € fix |
| Sanejament interior | 2.851,63 € fix |
| Escomeses (llum + aigua + telecos) | 8.578,00 € fix |
| Pre-instal·lació ventilació | 2.345,00 € fix |
| Electricitat interior | 6,15 % × Pack envolvent |
| Aigua interior | 4,98 % × Pack envolvent |
| Zehnder 350Q (qualitat aire excel·lent) | 8.910 € fix |
| Aerotèrmia ACS sola (NO fan coils) | 2.870 € fix |
| Aerotèrmia ACS+cal+ref (auto si fan coils) | 10.976 € fix |
| Fan coils Panasonic 700 | 996 € × (nº habitacions + 2) |
| Llar de foc | 3.200 € fix |
| Plaques solars (~4 kWp) | 6.500 € fix |
| Persianes motoritzades | 650 € × nº finestres |
| Membrana radó | 12 €/m² |
| Domòtica Loxone | 8.500 € + 25 €/m² |

**Canvi clau:** si el client demana fan coils → aerotèrmia es força automàticament a la versió completa (ACS+cal+ref, 10.976 €).

### 2.3 · Pack parking i exteriors

| Concepte | Càlcul |
|---|---|
| Porta peatonal RF (si garatge) | 544 € |
| Previsió porta motoritzada (si garatge) | 3.345,76 € (era 2.450) |
| Estructura garatge | 998 €/m² × m²_garatge |
| Pòrxos i terrasses | 577 €/m² × m²_porxos |

### 2.4 · Pack acabats interiors

| Concepte | Càlcul |
|---|---|
| Pintura | 2,95 % × Pack envolvent (era 19,5 €/m²) |
| Pladur | 12,05 % × Pack envolvent (era 99 €/m²) |
| Cuina funcional | 10.500 € |
| Cuina alta qualitat (defecte) | 13.234 € |
| Cuina exclusiu (Krona) | 17.174,43 € (era 16.500) |
| Paviment laminat / parquet | 51,21 €/m² × m²_paviment |
| Paviment ceràmic | 49 €/m² × m²_paviment |
| Paviment formigó | 42 €/m² × m²_paviment |
| Portes interiors | 495 € × nº portes |
| Estructura Krona (si exclusiu) | 245 € × nº portes |
| Bany estàndard | 4.322,50 € × nº banys (era 2.800) |
| Bany alt | 5.500 € × nº banys (era 4.500) |
| Bany premium | 8.500 € × nº banys (era 7.500) |
| Escala fusta | 3.638,40 € × (plantes - 1) (era 3.423) |
| Escala metàl·lica | 5.000 € × (plantes - 1) |

### 2.5 · Transport i contractació externa

| Concepte | Càlcul |
|---|---|
| Transport | 97 €/km (era 95) |
| Projecte arquitectònic | 0 € si client porta, si no 187 €/m² |
| Seguretat i salut | 2 % × total construcció |
| Fonamentació | **PENDENT DE VALORAR · no se suma · informatiu 300 €/m²** |

---

## 3 · Pendents

### 3.1 · Inconsistències a l'oficial PAPIK (cal aclarir)

1. **Pòrxos 40 m²** facturats al CAS 1 (23.080 €) i NO al CAS 2. El codi els compta sempre.
2. **CAS 2 transport** calculat amb 44 km en lloc dels 23 km de Barcelona. El codi usa 23 km.
3. **Piscina** apareix al CAS 1 (20.000 €) però no és cap pregunta del configurador.

### 3.2 · Coses pendents heretades de l'iteració 1

4. Confirmar si volem deixar la fonamentació "pendent" (decidit per ara: SÍ).
5. Confirmar si 187 €/m² mig pel projecte arquitectònic està bé.
6. Anotacions IMG_3529 ("DEUER", "chapeta") segueixen sense desxifrar.

### 3.3 · Recomanació · afegir preguntes opcionals

- Vol incloure piscina al pressupost? (Sí 7×3 amb sistema aigua salada = 20.000 €)
- Té el projecte arquitectònic ja fet? (Si Sí → no es facturen 187 €/m²)
- Té la fonamentació ja feta? (Si Sí → 0 €; si No → "pendent de valorar")

---

## 4 · Verificació amb el CAS 2 (Barcelona 160 m² · 2P · 2B · 2H)

| Partida | Aquest codi | Oficial PAPIK |
|---|---:|---:|
| Envolvent | 182.543 € | 187.491 € |
| Instal·lacions | 51.475 € | ~52.026 € |
| Parking (40 m² pòrxos) | 23.080 € | 3.346 € (anomalia) |
| Acabats | 64.831 € | ~57.438 € |
| Transport | 2.231 € (23 km) | 4.268 € (44 km, anomalia) |
| Projecte arquitectònic | 29.920 € | 29.900 € |
| Seguretat i salut | 6.483 € | 5.777 € |
| Fonamentació | 0 € (pendent) | 40.000 € (pendent) |
| **TOTAL pressupost** | **396.620 €** | **400.971 €** |

Si s'eliminen les anomalies (pòrxos i 44 km) i s'ignora la fonamentació, la diferència és **<1 %**.

---

## 5 · Fitxers tocats

| Fitxer | Què s'hi ha canviat |
|---|---|
| `api/calcular.py` | Reescrita la lògica completa amb fórmules calibrades. |
| `Pressupost_Canvis_Equip_v2_2026-05-30.docx` | Versió Word d'aquest document (a l'arrel del repo). |
| `seo-internal/Pressupost_Canvis_Equip_v2_2026-05-30.md` | Aquest document. |
