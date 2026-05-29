# Canvis a la lògica de càlcul del pressupost

> Origen: notes manuscrites de l'equip sobre 9 fulls impresos del configurador (29 maig 2026).
> Imatges originals: `IMG_3526.HEIC` … `IMG_3534.HEIC` (carpeta Downloads).
> Aquest document recull què s'ha aplicat, què queda pendent i què no s'ha entès.

---

## 1 · Canvis aplicats a `api/calcular.py`

### 1.1 Pack Envolvent tèrmic

| Partida | Abans | Després |
|---|---|---|
| Estructura vertical | `base × 0,503` | `base × 0,503 × 1,185` (+18,5 %) |
| Coberta i forjats | `base × 0,294 + increment_coberta` | `(base × 0,294 + increment_coberta) × 1,09` (+9 %) |
| Finestres | `base × 0,178 + suplement` | `(base × 0,178 + suplement) × 1,183` (+18,3 %) |
| Porta d'entrada | `2.245 €` fix | `3.445,45 €` fix |

Font: IMG_3526 (manuscrit `+18,5 %`, `+9 %`, `+18,3 %`) + IMG_3534 (taula comercial: porta 3.445,45 €).

### 1.2 Pack Instal·lacions

| Partida | Abans | Després |
|---|---|---|
| Telecomunicacions | `1.989 €` fix | `m² × 18,9 €/m²` |
| Sanejament interior | `1.621 €` fix | `m² × 18,7 €/m²` |
| Pre-instal·lació ventilació | `1.985 €` fix | `m² × 14,2 €/m²` |
| Nº fan coils | `max(2, round(m²/40))` | `num_habitacions + 2` |

Font: IMG_3528 (telecos m² × 18,9, sanejament m² × 18,7) + IMG_3526 (ventilació m² × 14,2) + IMG_3530 (fan coils = `nº habitacions + 2`).

### 1.3 Configurador (`papik_configurador.json`)

S'afegeix la pregunta:

> **Quantes habitacions té la casa?** (mínim 1 – màxim 10) — necessària per calcular el nombre de fan coils.

### 1.4 Contractació externa

| Partida | Abans | Després |
|---|---|---|
| Projecte arquitectònic | `10,5 % × total_construcció` | `198,60 €/m²` (0 si el client ja porta projecte) |
| Seguretat i salut | `1,75 % × total_construcció` | `2 % × total_construcció` |

Font: IMG_3527 (`198,60 €/m²` projecte; `2 % pressupost total` seguretat).

> Nota: "pressupost total" en la nota s'ha interpretat com `total_construcció` (mateixa base que abans), no com el total amb IVA. Si l'equip volia el total amb IVA, cal corregir.

---

## 2 · Canvis pendents (a decidir amb l'equip)

### 2.1 Pintura i Pladur (IMG_3527 + IMG_3531)

L'equip ha anotat:

- Pintura → **2,96 % p.a.t.**
- Pladur → **12,06 % p.a.t.**

No tenim clar què és **p.a.t.** ni sobre quina base s'aplica el percentatge. Hipòtesis:

- Pack Acabats Total (circular: la pintura forma part del pack acabats).
- Pack Envolvent Tèrmic (els números d'IMG_3527 quadren aproximadament: 158.784 € × 2,96 % ≈ 4.700 €).
- Pressupost Aproximat Total (total_construcció).
- Senzillament pujar el €/m² actual aquest percentatge (19,5 × 1,0296 = 20,08 €/m²) — canvi molt petit, poc probable.

**Decisió temporal:** es manté el càlcul actual (19,5 €/m² pintura, 99 €/m² pladur) fins a confirmar.

### 2.2 Fonamentació (IMG_3533)

A la foto s'ha ratllat amb X vermella el valor 79.200 € (= 396 €/m² × 200 m²), però no s'indica el valor nou. **No s'aplica cap canvi.**

### 2.3 IMG_3529 (Santa Coloma de Gramenet)

Anotacions:
- "+ DEUER ↓ Sobre lògica càlcul"
- "X chapeta" al costat de finestres EcoVen S-82

No s'ha pogut interpretar. **No s'aplica cap canvi.**

---

## 3 · Coses que no sabem

Llistat obert per al pròxim repàs amb l'equip:

1. Significat de **p.a.t.** (apartat 2.1).
2. Valor correcte de la **fonamentació** (apartat 2.2).
3. Significat de "**DEUER**" i "**chapeta**" a IMG_3529 (apartat 2.3).
4. Discrepància entre **3.345,48 €** (manuscrit IMG_3526) i **3.445,45 €** (taula comercial IMG_3534) per a la **porta d'entrada**. S'ha agafat 3.445,45 € (document comercial). A confirmar.
5. **Seguretat i salut**: "2 % pressupost total" — total de què? S'ha mantingut sobre `total_construcció`.
6. **Pre-instal·lació ventilació**: a IMG_3526 s'escriu "m² × 14,2" amb dubtes (xifra poc nítida). Si era 19,2 o un altre valor, cal corregir.
7. **Increments envolvent (+18,5 / +9 / +18,3 %)**: estan sobre la partida abans del suplement o sobre el resultat amb suplement? S'ha aplicat sobre el resultat final de cada partida (inclou suplement de coberta i de finestres).

---

## 4 · Referència ràpida d'imatges

| Foto | Contingut |
|---|---|
| IMG_3526 | Desglossament 158.784 € envolvent. Manuscrits +18,5 %, +9 %, +18,3 %; telecos/sanejament/ventilació en €/m²; porta 3.345,48 €. |
| IMG_3527 | Acabats. Pintura 2,96 % p.a.t., pladur 12,06 % p.a.t. Projecte 198,60 €/m². Seguretat 2 %. |
| IMG_3528 | Càlculs nets: telecos = m² × 18,9; sanejament interior = m² × 18,7. |
| IMG_3529 | Resum Santa Coloma 140 m². Anotació "DEUER" i "chapeta" (no enteses). |
| IMG_3530 | Desglossament 139.236 € + notes sobre aerotèrmia (ACS sola vs ACS+cal+ref) i fórmula fan coils = nº habitacions + 2. |
| IMG_3531 | Acabats variant amb anotacions vermelles sobre pintura i pladur. |
| IMG_3532 | Desglossament 210.871 € amb correcció manual a 223.000 €. |
| IMG_3533 | Acabats. Tachat el 79.200 € de fonamentació. |
| IMG_3534 | Taula comercial oficial amb preus per unitat. Total envolvent 223.044,54 €. Confirma porta 3.445,45 €, fan coils 996 €/unitat × 6 unitats. |
