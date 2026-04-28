// Build Word document from PAPIK article: Hipoteca verda Sabadell
const fs = require('fs');
const {
  Document, Packer, Paragraph, TextRun, AlignmentType, LevelFormat,
  HeadingLevel, Footer, Header, PageNumber, BorderStyle, TabStopType,
  TabStopPosition,
} = require('docx');

// Helper to create body paragraph
const p = (text, options = {}) => new Paragraph({
  children: [new TextRun({ text, ...options })],
  spacing: { after: 120 },
  ...options.paragraphOptions,
});

// Helper for bullet item
const bullet = (text) => new Paragraph({
  numbering: { reference: 'bullets', level: 0 },
  children: [new TextRun(text)],
});

// Helper for inline link
const link = (text) => new TextRun({ text, italics: true, color: '1F4788' });

const doc = new Document({
  creator: 'PAPIK Group',
  title: 'Hipoteca verda per a Passivhaus · acord PAPIK + Banc Sabadell',
  description: 'Article editorial · PAPIK Group',
  styles: {
    default: {
      document: { run: { font: 'Calibri', size: 22 } }, // 11pt
    },
    paragraphStyles: [
      {
        id: 'Heading1',
        name: 'Heading 1',
        basedOn: 'Normal',
        next: 'Normal',
        quickFormat: true,
        run: { size: 36, bold: true, font: 'Calibri', color: '1A1A1A' },
        paragraph: { spacing: { before: 360, after: 240 }, outlineLevel: 0 },
      },
      {
        id: 'Heading2',
        name: 'Heading 2',
        basedOn: 'Normal',
        next: 'Normal',
        quickFormat: true,
        run: { size: 28, bold: true, font: 'Calibri', color: '1A1A1A' },
        paragraph: { spacing: { before: 280, after: 160 }, outlineLevel: 1 },
      },
      {
        id: 'Heading3',
        name: 'Heading 3',
        basedOn: 'Normal',
        next: 'Normal',
        quickFormat: true,
        run: { size: 24, bold: true, font: 'Calibri', color: '333333' },
        paragraph: { spacing: { before: 200, after: 120 }, outlineLevel: 2 },
      },
      {
        id: 'Title',
        name: 'Title',
        basedOn: 'Normal',
        next: 'Normal',
        run: { size: 44, bold: true, font: 'Calibri', color: '0A1B12' },
        paragraph: { spacing: { before: 0, after: 120 }, alignment: AlignmentType.LEFT },
      },
      {
        id: 'Subtitle',
        name: 'Subtitle',
        basedOn: 'Normal',
        next: 'Normal',
        run: { size: 22, italics: true, font: 'Calibri', color: '666666' },
        paragraph: { spacing: { before: 0, after: 360 } },
      },
      {
        id: 'Disclaimer',
        name: 'Disclaimer',
        basedOn: 'Normal',
        run: { size: 18, italics: true, font: 'Calibri', color: '777777' },
        paragraph: { spacing: { before: 240, after: 120 } },
      },
    ],
  },
  numbering: {
    config: [
      {
        reference: 'bullets',
        levels: [
          {
            level: 0,
            format: LevelFormat.BULLET,
            text: '•',
            alignment: AlignmentType.LEFT,
            style: { paragraph: { indent: { left: 720, hanging: 360 } } },
          },
        ],
      },
    ],
  },
  sections: [
    {
      properties: {
        page: {
          size: { width: 11906, height: 16838 }, // A4
          margin: { top: 1440, right: 1440, bottom: 1440, left: 1440 }, // 1 inch
        },
      },
      headers: {
        default: new Header({
          children: [
            new Paragraph({
              children: [
                new TextRun({ text: 'PAPIK Group · ', size: 18, color: '888888' }),
                new TextRun({ text: 'Article editorial', size: 18, italics: true, color: '888888' }),
              ],
              alignment: AlignmentType.RIGHT,
              border: {
                bottom: { style: BorderStyle.SINGLE, size: 4, color: 'CCCCCC', space: 4 },
              },
            }),
          ],
        }),
      },
      footers: {
        default: new Footer({
          children: [
            new Paragraph({
              children: [
                new TextRun({
                  text: 'Aquest contingut és informatiu. La menció de l\u2019acord PAPIK-Banc Sabadell no constitueix oferta vinculant de finançament. Les condicions hipotecàries concretes es defineixen entre l\u2019entitat financera i el client en funció del seu perfil de risc, en línia amb la normativa hipotecària espanyola vigent.',
                  size: 16,
                  italics: true,
                  color: '888888',
                }),
              ],
              spacing: { before: 100 },
            }),
            new Paragraph({
              children: [
                new TextRun({ text: 'PAPIK Group · papik.cat', size: 16, color: 'AAAAAA' }),
                new TextRun({ text: '\t', size: 16 }),
                new TextRun({ text: 'Pàgina ', size: 16, color: 'AAAAAA' }),
                new TextRun({ children: [PageNumber.CURRENT], size: 16, color: 'AAAAAA' }),
              ],
              tabStops: [{ type: TabStopType.RIGHT, position: 9026 }],
              spacing: { before: 80 },
            }),
          ],
        }),
      },
      children: [
        // ---- TITLE BLOCK ----
        new Paragraph({
          style: 'Title',
          children: [new TextRun('Hipoteca verda per a Passivhaus')],
        }),
        new Paragraph({
          style: 'Title',
          children: [new TextRun({ text: 'Acord PAPIK + Banc Sabadell', size: 32, color: '56685E' })],
        }),
        new Paragraph({
          style: 'Subtitle',
          children: [new TextRun('Equip de PAPIK Group  ·  [Data publicació]  ·  Reading time ~7 min')],
        }),

        // ---- INTRO ----
        new Paragraph({
          children: [
            new TextRun(
              'Construir o comprar una casa Passivhaus suposa una inversió superior a la d\u2019una construcció convencional — i tradicionalment ha topat amb una limitació financera: els bancs no diferenciaven entre vivendes amb estàndards energètics avançats i la resta del parc immobiliari. Això comença a canviar.'
            ),
          ],
          spacing: { after: 200 },
        }),
        new Paragraph({
          children: [
            new TextRun('PAPIK Group i '),
            new TextRun({ text: 'Banc Sabadell', bold: true }),
            new TextRun(' han formalitzat un acord per oferir '),
            new TextRun({ text: 'hipoteques verdes', bold: true }),
            new TextRun(' específiques per a clients de PAPIK que adquireixin habitatges d\u2019alta eficiència energètica. Aquest article explica què són les hipoteques verdes, com s\u2019han d\u2019integrar amb projectes Passivhaus, i el marc general de l\u2019acord PAPIK-Sabadell.'),
          ],
          spacing: { after: 240 },
        }),

        // ---- H2 · 1 ----
        new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun('1. Què és una hipoteca verda')] }),
        new Paragraph({
          children: [
            new TextRun('Una '),
            new TextRun({ text: 'hipoteca verda', bold: true }),
            new TextRun(' (també anomenada \u201Chipoteca energètica\u201D o \u201Chipoteca sostenible\u201D) és un producte de finançament destinat a:'),
          ],
          spacing: { after: 120 },
        }),
        bullet('L\u2019adquisició d\u2019habitatges amb classe energètica A o B'),
        bullet('La rehabilitació energètica que millora la classe energètica almenys dos nivells'),
        bullet('L\u2019adquisició de promocions amb certificació Passivhaus o equivalent'),
        new Paragraph({
          children: [
            new TextRun('A diferència d\u2019una hipoteca convencional, la hipoteca verda '),
            new TextRun({ text: 'incorpora bonificacions específiques', bold: true }),
            new TextRun(' vinculades a l\u2019eficiència energètica del bé finançat. Aquestes bonificacions varien segons l\u2019entitat i les condicions específiques de cada client, però generalment poden incloure:'),
          ],
          spacing: { before: 160, after: 120 },
        }),
        bullet('Reducció del tipus d\u2019interès aplicable'),
        bullet('Bonificació per acreditació de la certificació energètica'),
        bullet('Termes diferenciats sobre comissions i productes vinculats'),
        new Paragraph({
          children: [
            new TextRun({ text: '⚠ ', bold: true, color: 'B85C5C' }),
            new TextRun({ text: 'Les condicions concretes de cada hipoteca verda es defineixen entre l\u2019entitat financera i el client, segons el seu perfil específic. Aquest article no descriu les condicions exactes de l\u2019acord PAPIK-Sabadell — són ', italics: true }),
            new TextRun({ text: 'privades i exclusives', italics: true, bold: true }),
            new TextRun({ text: ' per a clients que les sol·licitin a través de PAPIK.', italics: true }),
          ],
          spacing: { before: 200, after: 240 },
          shading: { fill: 'F5F5F5', type: 'clear' },
        }),

        // ---- H2 · 2 ----
        new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun('2. L\u2019acord PAPIK + Banc Sabadell')] }),
        new Paragraph({
          children: [
            new TextRun('Banc Sabadell és una de les entitats financeres espanyoles amb una '),
            new TextRun({ text: 'estratègia ESG (Environmental · Social · Governance)', bold: true }),
            new TextRun(' consolidada i mandat actiu de finançament sostenible. PAPIK Group, com a constructora especialitzada en estàndards Passivhaus, ha estructurat amb Banc Sabadell un acord pel qual els clients de PAPIK poden accedir a un canal preferent de finançament verda.'),
          ],
          spacing: { after: 200 },
        }),
        new Paragraph({
          children: [new TextRun({ text: 'El que aporta l\u2019acord:', bold: true })],
          spacing: { after: 120 },
        }),
        bullet('Procés simplificat — presentació tècnica del projecte per part de PAPIK al Banc, evitant que el client gestioni la documentació tècnica davant de l\u2019entitat'),
        bullet('Reconeixement formal de l\u2019estàndard — les vivendes Passivhaus o equivalents construïdes per PAPIK queden validades automàticament dins el marc de criteris d\u2019eficiència energètica del Banc'),
        bullet('Canal d\u2019atenció dedicat — l\u2019equip comercial de PAPIK coordina directament amb un punt de contacte específic dins de Banc Sabadell'),
        new Paragraph({
          children: [
            new TextRun('Les '),
            new TextRun({ text: 'condicions concretes de cada operació hipotecària', bold: true }),
            new TextRun(' (tipus, termini, comissions, garanties) es '),
            new TextRun({ text: 'negocien individualment', bold: true }),
            new TextRun(' entre el client i Banc Sabadell, com a qualsevol producte hipotecari. PAPIK actua com a facilitador del canal, no com a part del contracte de préstec.'),
          ],
          spacing: { before: 200, after: 240 },
        }),

        // ---- H2 · 3 ----
        new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun('3. Per què Passivhaus mereix tractament financer diferenciat')] }),
        new Paragraph({
          children: [new TextRun('Una vivenda Passivhaus presenta un perfil econòmic radicalment diferent al d\u2019una construcció convencional, i això justifica que les entitats financeres ofereixin condicions específiques:')],
          spacing: { after: 160 },
        }),
        new Paragraph({ heading: HeadingLevel.HEADING_3, children: [new TextRun('Cost operatiu inferior · risc d\u2019impagament reduït')] }),
        new Paragraph({
          children: [new TextRun('Una casa Passivhaus consumeix fins a un 90% menys d\u2019energia que una equivalent convencional. La factura energètica reduïda allibera capacitat de pagament del client al llarg de la vida del préstec — fet rellevant per al risc de l\u2019entitat.')],
          spacing: { after: 200 },
        }),
        new Paragraph({ heading: HeadingLevel.HEADING_3, children: [new TextRun('Revalorització superior')] }),
        new Paragraph({
          children: [new TextRun('Estudis del sector immobiliari (com els publicats per Sociedad de Tasación o Idealista Data) indiquen que les vivendes amb classe energètica A es revaloritzen entre un 15% i un 25% més que equivalents classe E o F en mercats secundaris. Una garantia immobiliària amb millor revalorització esperada redueix l\u2019exposició del Banc.')],
          spacing: { after: 200 },
        }),
        new Paragraph({ heading: HeadingLevel.HEADING_3, children: [new TextRun('Marc regulatori favorable')] }),
        new Paragraph({
          children: [
            new TextRun('La Comissió Europea i el Banc Central Europeu promouen activament el finançament d\u2019habitatge eficient com a part del '),
            new TextRun({ text: 'Pacte Verd Europeu', bold: true }),
            new TextRun('. Les entitats financeres tenen mandat creixent d\u2019incloure criteris ESG en les seves carteres hipotecàries — i el finançament d\u2019habitatges Passivhaus encaixa exactament amb aquest marc.'),
          ],
          spacing: { after: 200 },
        }),
        new Paragraph({ heading: HeadingLevel.HEADING_3, children: [new TextRun('Ajudes públiques compatibles')] }),
        new Paragraph({
          children: [
            new TextRun('En projectes de rehabilitació energètica, la hipoteca verda és compatible amb les '),
            new TextRun({ text: 'ajudes Next Generation EU', bold: true }),
            new TextRun(' (Programes 3, 4 i 5), generant una estructura financera optimitzada que combina capital propi del client + subvenció pública + finançament verd.'),
          ],
          spacing: { after: 240 },
        }),

        // ---- H2 · 4 ----
        new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun('4. A qui s\u2019adreça aquest acord')] }),
        new Paragraph({ children: [new TextRun('L\u2019acord PAPIK + Banc Sabadell s\u2019adreça a tres perfils de client de PAPIK:')], spacing: { after: 160 } }),

        new Paragraph({ heading: HeadingLevel.HEADING_3, children: [new TextRun('1. Compradors de promocions PAPIK')] }),
        new Paragraph({
          children: [new TextRun('Particulars que adquireixen una vivenda terminada o sobre plà a una de les promocions actives de PAPIK. La presentació tècnica al Banc està facilitada per la documentació estandaritzada de cada promoció.')],
          spacing: { after: 200 },
        }),

        new Paragraph({ heading: HeadingLevel.HEADING_3, children: [new TextRun('2. Clients de Construcció')] }),
        new Paragraph({
          children: [new TextRun('Famílies que construeixen la seva casa amb PAPIK i necessiten finançament hipotecari per a l\u2019adquisició del solar i/o l\u2019execució de l\u2019obra. La certificació final Passivhaus permet activar el canal d\u2019hipoteca verda al final del procés.')],
          spacing: { after: 200 },
        }),

        new Paragraph({ heading: HeadingLevel.HEADING_3, children: [new TextRun('3. Clients de Rehabilitació')] }),
        new Paragraph({
          children: [new TextRun('Propietaris que rehabiliten energèticament la seva vivenda amb PAPIK i requereixen finançament addicional al subsidi NGEU. La hipoteca verda pot finançar la part no subvencionada del cost.')],
          spacing: { after: 200 },
        }),

        new Paragraph({
          children: [
            new TextRun({ text: '⚠ ', bold: true, color: 'B85C5C' }),
            new TextRun({ text: 'La concessió de la hipoteca ', italics: true }),
            new TextRun({ text: 'depèn dels criteris de risc i solvència del Banc', italics: true, bold: true }),
            new TextRun({ text: ', que avalua cada client segons els seus paràmetres habituals. PAPIK no garanteix l\u2019aprovació — facilita l\u2019accés al canal preferent.', italics: true }),
          ],
          spacing: { before: 160, after: 240 },
          shading: { fill: 'F5F5F5', type: 'clear' },
        }),

        // ---- H2 · 5 ----
        new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun('5. Procés per accedir a la hipoteca verda PAPIK + Banc Sabadell')] }),
        new Paragraph({
          children: [new TextRun('Per a un client de PAPIK que vulgui explorar aquesta opció, el procés és:')],
          spacing: { after: 160 },
        }),
        new Paragraph({ numbering: { reference: 'bullets', level: 0 }, children: [
          new TextRun({ text: 'Definició del projecte amb PAPIK', bold: true }),
          new TextRun(' — construcció, promoció o rehabilitació, amb pressupost i certificació energètica esperada')
        ]}),
        new Paragraph({ numbering: { reference: 'bullets', level: 0 }, children: [
          new TextRun({ text: 'Sol·licitud de canal preferent', bold: true }),
          new TextRun(' — PAPIK presenta el projecte tècnicament a Banc Sabadell amb la documentació estandaritzada')
        ]}),
        new Paragraph({ numbering: { reference: 'bullets', level: 0 }, children: [
          new TextRun({ text: 'Avaluació del client', bold: true }),
          new TextRun(' — Banc Sabadell avalua perfil de client i condicions específiques aplicables')
        ]}),
        new Paragraph({ numbering: { reference: 'bullets', level: 0 }, children: [
          new TextRun({ text: 'Proposta hipotecària', bold: true }),
          new TextRun(' — l\u2019entitat formula proposta concreta al client, que decideix si l\u2019accepta')
        ]}),
        new Paragraph({ numbering: { reference: 'bullets', level: 0 }, children: [
          new TextRun({ text: 'Formalització', bold: true }),
          new TextRun(' — contracte hipotecari directe entre client i Banc Sabadell. PAPIK no és part del préstec')
        ]}),
        new Paragraph({
          children: [new TextRun('L\u2019acompanyament tècnic de PAPIK durant el procés és coordinat amb el departament d\u2019autopromoció i el comercial.')],
          spacing: { before: 160, after: 280 },
        }),

        // ---- H2 · 6 · FAQ ----
        new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun('Preguntes freqüents')] }),

        new Paragraph({ heading: HeadingLevel.HEADING_3, children: [new TextRun('Quines són les condicions concretes de la hipoteca verda?')] }),
        new Paragraph({
          children: [new TextRun('Les condicions concretes (tipus d\u2019interès, termini, comissions, productes vinculats) són privades i exclusives per a cada client que sol·liciti l\u2019opció a través de PAPIK. Es comuniquen individualment durant el procés d\u2019avaluació.')],
          spacing: { after: 200 },
        }),

        new Paragraph({ heading: HeadingLevel.HEADING_3, children: [new TextRun('Tinc garantida l\u2019aprovació de la hipoteca?')] }),
        new Paragraph({
          children: [new TextRun('No. L\u2019aprovació depèn dels criteris de risc i solvència de Banc Sabadell, que avalua cada client segons els seus paràmetres habituals. PAPIK facilita l\u2019accés al canal però no influeix en la decisió de concessió.')],
          spacing: { after: 200 },
        }),

        new Paragraph({ heading: HeadingLevel.HEADING_3, children: [new TextRun('Puc usar aquesta opció amb una rehabilitació energètica?')] }),
        new Paragraph({
          children: [new TextRun('Sí. El finançament verd és compatible amb projectes de rehabilitació energètica — habitualment com a complement a les ajudes Next Generation EU. PAPIK estructura la combinació òptima durant la fase de projecte.')],
          spacing: { after: 200 },
        }),

        new Paragraph({ heading: HeadingLevel.HEADING_3, children: [new TextRun('L\u2019acord és exclusiu? Puc negociar amb altres entitats?')] }),
        new Paragraph({
          children: [new TextRun('L\u2019acord PAPIK-Sabadell és un canal preferent, però no exclusiu. Vostè pot negociar la seva hipoteca amb qualsevol altra entitat financera. La nostra recomanació: comparar sempre vàries opcions abans de firmar.')],
          spacing: { after: 200 },
        }),

        new Paragraph({ heading: HeadingLevel.HEADING_3, children: [new TextRun('Quin tipus de certificació energètica acredita el meu projecte?')] }),
        new Paragraph({
          children: [new TextRun('Una vivenda PAPIK pot acreditar diversos nivells: certificat energètic A, certificació Passivhaus (Standard, Plus o Premium), EnerPHit per a rehabilitació. Cada nivell té les seves implicacions financeres específiques — l\u2019orientem en cada cas concret.')],
          spacing: { after: 280 },
        }),

        // ---- CIERRE ----
        new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun('Comencem la conversa')] }),
        new Paragraph({
          children: [new TextRun('Si està valorant un projecte amb PAPIK i vol explorar l\u2019opció d\u2019hipoteca verda amb Banc Sabadell, podem incorporar-ho a la fase de planificació financera del projecte.')],
          spacing: { after: 200 },
        }),
        new Paragraph({
          children: [
            new TextRun({ text: '→ ', bold: true, color: '0A1B12' }),
            new TextRun({ text: 'Sol·licitar informació sobre finançament verd', bold: true }),
            new TextRun('  ·  papik.cat/contacte'),
          ],
          spacing: { after: 120 },
        }),
        new Paragraph({
          children: [
            new TextRun({ text: '→ ', bold: true, color: '0A1B12' }),
            new TextRun('Configurar el pressupost del meu projecte  ·  papik.cat/pressupost'),
          ],
          spacing: { after: 280 },
        }),

        // ---- LLEGIU TAMBÉ ----
        new Paragraph({
          children: [new TextRun({ text: 'Llegiu també', bold: true, size: 22, color: '666666' })],
          spacing: { before: 240, after: 120 },
        }),
        bullet('Hipoteca energètica · què és i quan val la pena'),
        bullet('Construcció · de zero a clau en mà'),
        bullet('Promoció · cases ja construïdes o amb entrega tancada'),
        bullet('Rehabilitació energètica + Next Generation EU'),
      ],
    },
  ],
});

Packer.toBuffer(doc).then((buffer) => {
  const out = '/Users/trisfisas/Desktop/CÓDIGO/papik-web/seo-internal/exports/article-nota-premsa-papik-sabadell-ca.docx';
  fs.writeFileSync(out, buffer);
  console.log('OK · Fitxer generat:', out);
  console.log('Mida:', (buffer.length / 1024).toFixed(1), 'KB');
});
