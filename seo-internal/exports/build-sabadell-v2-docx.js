// Build Word document v2 from PAPIK Sabadell article (esmena editorial v1.1)
// Sense guions llargs, amb prosa argumentada, registre elevat
const fs = require('fs');
const {
  Document, Packer, Paragraph, TextRun, AlignmentType,
  HeadingLevel, Footer, Header, PageNumber, BorderStyle, TabStopType,
} = require('docx');

const doc = new Document({
  creator: 'PAPIK Group',
  title: "Hipoteca verda per a Passivhaus: l'acord entre PAPIK i Banc Sabadell",
  description: 'Article editorial · PAPIK Group · v2 esmena editorial',
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
        paragraph: { spacing: { before: 320, after: 180 }, outlineLevel: 1 },
      },
      {
        id: 'Heading3',
        name: 'Heading 3',
        basedOn: 'Normal',
        next: 'Normal',
        quickFormat: true,
        run: { size: 24, bold: true, font: 'Calibri', color: '333333' },
        paragraph: { spacing: { before: 220, after: 140 }, outlineLevel: 2 },
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
    ],
  },
  sections: [
    {
      properties: {
        page: {
          size: { width: 11906, height: 16838 }, // A4
          margin: { top: 1440, right: 1440, bottom: 1440, left: 1440 },
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
                  text: "Aquest contingut és informatiu. La menció de l'acord PAPIK i Banc Sabadell no constitueix oferta vinculant de finançament. Les condicions hipotecàries concretes es defineixen entre l'entitat financera i el client en funció del seu perfil de risc, en línia amb la normativa hipotecària espanyola vigent.",
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
        // TITLE
        new Paragraph({
          style: 'Title',
          children: [new TextRun('Hipoteca verda per a Passivhaus')],
        }),
        new Paragraph({
          style: 'Title',
          children: [new TextRun({ text: "L'acord entre PAPIK i Banc Sabadell", size: 32, color: '56685E' })],
        }),
        new Paragraph({
          style: 'Subtitle',
          children: [new TextRun('Equip de PAPIK Group  ·  [Data publicació]  ·  Reading time aproximat 7 min')],
        }),

        // INTRO
        new Paragraph({
          children: [
            new TextRun(
              "Construir o comprar una casa Passivhaus implica una inversió superior a la d'una construcció convencional, i tradicionalment ha topat amb una limitació financera concreta. Els bancs no diferenciaven entre vivendes amb estàndards energètics avançats i la resta del parc immobiliari, i això deixava sense translació financera el sobrecost real associat a complir amb estàndards d'alta eficiència. Aquesta situació comença a canviar."
            ),
          ],
          spacing: { after: 200 },
        }),
        new Paragraph({
          children: [new TextRun(
            "PAPIK Group i Banc Sabadell han formalitzat un acord per oferir hipoteques verdes als clients de PAPIK que adquireixin habitatges d'alta eficiència energètica. Aquest article descriu què és aquest tipus de finançament, com s'integra amb projectes Passivhaus, i el marc general de la col·laboració entre les dues parts."
          )],
          spacing: { after: 280 },
        }),

        // H2 1
        new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun('1. Què és una hipoteca verda')] }),
        new Paragraph({
          children: [new TextRun(
            "Una hipoteca verda, també anomenada hipoteca energètica o hipoteca sostenible, és un producte de finançament destinat a tres tipus d'operacions: l'adquisició d'habitatges amb classe energètica A o B, la rehabilitació energètica que millori la qualificació en almenys dos nivells, i l'adquisició de promocions amb certificació Passivhaus o equivalent. La característica distintiva, respecte d'una hipoteca convencional, és que incorpora bonificacions específiques vinculades a l'eficiència energètica del bé finançat."
          )],
          spacing: { after: 200 },
        }),
        new Paragraph({
          children: [new TextRun(
            "Aquestes bonificacions varien segons l'entitat i les condicions del client. Habitualment es traslladen al tipus d'interès aplicable, a les condicions sobre comissions i productes vinculats, o a la valoració mateixa de la garantia immobiliària. La intensitat de cada element depèn de l'entitat financera i del perfil concret de l'operació, motiu pel qual no es publiquen aquí les condicions exactes."
          )],
          spacing: { after: 200 },
        }),
        new Paragraph({
          children: [new TextRun(
            "Les condicions específiques de l'acord PAPIK i Banc Sabadell són privades i exclusives per a clients que les sol·licitin a través de PAPIK. Es comuniquen individualment durant el procés d'avaluació de cada operació."
          )],
          spacing: { after: 280 },
        }),

        // H2 2
        new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun("2. L'acord PAPIK i Banc Sabadell")] }),
        new Paragraph({
          children: [new TextRun(
            "Banc Sabadell és una de les entitats financeres espanyoles amb una estratègia ESG (Environmental, Social, Governance) consolidada i mandat actiu de finançament sostenible. PAPIK Group, com a constructora especialitzada en estàndards Passivhaus, ha estructurat amb Banc Sabadell un acord pel qual els clients de PAPIK poden accedir a un canal preferent de finançament verda."
          )],
          spacing: { after: 200 },
        }),
        new Paragraph({
          children: [new TextRun(
            "L'acord aporta tres elements operatius. Primer, un procés simplificat: PAPIK presenta tècnicament el projecte al Banc, evitant que el client hagi de gestionar la documentació tècnica davant de l'entitat. Segon, un reconeixement formal de l'estàndard: les vivendes Passivhaus o equivalents construïdes per PAPIK queden validades automàticament dins el marc de criteris d'eficiència energètica del Banc. Tercer, un canal d'atenció dedicat: l'equip comercial de PAPIK coordina directament amb un punt de contacte específic dins de Banc Sabadell."
          )],
          spacing: { after: 200 },
        }),
        new Paragraph({
          children: [new TextRun(
            "Les condicions concretes de cada operació hipotecària, incloent tipus, termini, comissions i garanties, es negocien individualment entre el client i Banc Sabadell, com a qualsevol producte hipotecari. PAPIK actua com a facilitador del canal, no com a part del contracte de préstec."
          )],
          spacing: { after: 280 },
        }),

        // H2 3
        new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun('3. Per què Passivhaus mereix tractament financer diferenciat')] }),
        new Paragraph({
          children: [new TextRun(
            "Una vivenda Passivhaus presenta un perfil econòmic radicalment diferent al d'una construcció convencional, i això justifica que les entitats financeres ofereixin condicions específiques. Els arguments són d'ordre tècnic i de risc, no comercial."
          )],
          spacing: { after: 200 },
        }),

        new Paragraph({ heading: HeadingLevel.HEADING_3, children: [new TextRun("Cost operatiu inferior i risc d'impagament reduït")] }),
        new Paragraph({
          children: [new TextRun(
            "Una casa Passivhaus consumeix fins a un 90% menys d'energia que una equivalent convencional. La factura energètica reduïda allibera capacitat de pagament del client al llarg de tota la vida del préstec, fet rellevant per al càlcul de risc de l'entitat financera. Quan dos clients amb el mateix perfil de renda accedeixen a hipoteques per a vivendes amb prestacions energètiques diferents, el risc associat al préstec també és diferent."
          )],
          spacing: { after: 200 },
        }),

        new Paragraph({ heading: HeadingLevel.HEADING_3, children: [new TextRun('Revalorització superior')] }),
        new Paragraph({
          children: [new TextRun(
            "Els estudis del sector immobiliari, com els publicats per Sociedad de Tasación o Idealista Data, indiquen que les vivendes amb classe energètica A es revaloritzen entre un 15% i un 25% més que equivalents classe E o F en mercats secundaris. Una garantia immobiliària amb millor revalorització esperada redueix l'exposició del Banc al llarg del termini de la hipoteca, especialment rellevant en escenaris de mercat estables o ascendents."
          )],
          spacing: { after: 200 },
        }),

        new Paragraph({ heading: HeadingLevel.HEADING_3, children: [new TextRun('Marc regulatori favorable')] }),
        new Paragraph({
          children: [new TextRun(
            "La Comissió Europea i el Banc Central Europeu promouen activament el finançament d'habitatge eficient com a part del Pacte Verd Europeu. Les entitats financeres tenen mandat creixent d'incloure criteris ESG en les seves carteres hipotecàries, i el finançament d'habitatges Passivhaus encaixa exactament amb aquest marc. Per a una entitat com Banc Sabadell, integrar aquest tipus de producte no és una decisió de màrqueting verd: és una resposta operativa a un mandat regulatori que avança any rere any."
          )],
          spacing: { after: 200 },
        }),

        new Paragraph({ heading: HeadingLevel.HEADING_3, children: [new TextRun('Compatibilitat amb ajudes públiques')] }),
        new Paragraph({
          children: [new TextRun(
            "En projectes de rehabilitació energètica, la hipoteca verda és compatible amb les ajudes Next Generation EU dels programes 3, 4 i 5. La combinació entre capital propi del client, subvenció pública i finançament verd genera una estructura financera optimitzada que pot reduir significativament el cost net per al beneficiari final."
          )],
          spacing: { after: 280 },
        }),

        // H2 4
        new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun("4. A qui s'adreça aquest acord")] }),
        new Paragraph({
          children: [new TextRun(
            "L'acord és aplicable a tres perfils de client de PAPIK, cada un amb un cas d'ús diferenciat."
          )],
          spacing: { after: 200 },
        }),

        new Paragraph({ heading: HeadingLevel.HEADING_3, children: [new TextRun('Compradors de promocions PAPIK')] }),
        new Paragraph({
          children: [new TextRun(
            "Particulars que adquireixen una vivenda terminada o sobre plà a una de les promocions actives de PAPIK. La presentació tècnica al Banc està facilitada per la documentació estandaritzada de cada promoció, fet que accelera la fase d'avaluació respecte d'una hipoteca tradicional."
          )],
          spacing: { after: 200 },
        }),

        new Paragraph({ heading: HeadingLevel.HEADING_3, children: [new TextRun('Clients de Construcció')] }),
        new Paragraph({
          children: [new TextRun(
            "Famílies que construeixen la seva casa amb PAPIK i necessiten finançament hipotecari per a l'adquisició del solar, l'execució de l'obra, o ambdues coses. La certificació final Passivhaus del projecte permet activar el canal d'hipoteca verda al final del procés constructiu, una vegada la vivenda compleix amb els criteris de l'estàndard."
          )],
          spacing: { after: 200 },
        }),

        new Paragraph({ heading: HeadingLevel.HEADING_3, children: [new TextRun('Clients de Rehabilitació')] }),
        new Paragraph({
          children: [new TextRun(
            "Propietaris que rehabiliten energèticament la seva vivenda amb PAPIK i requereixen finançament addicional al subsidi NGEU. La hipoteca verda pot finançar la part no subvencionada del cost, completant l'estructura financera del projecte de rehabilitació."
          )],
          spacing: { after: 200 },
        }),

        new Paragraph({
          children: [new TextRun(
            "En tots tres casos, la concessió de la hipoteca depèn dels criteris de risc i solvència del Banc, que avalua cada client segons els seus paràmetres habituals. PAPIK no garanteix l'aprovació; facilita l'accés al canal preferent."
          )],
          spacing: { after: 280 },
        }),

        // H2 5
        new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun('5. Procés per accedir al canal preferent')] }),
        new Paragraph({
          children: [new TextRun(
            "El procés segueix una seqüència estructurada que minimitza la fricció administrativa per al client. La primera fase és la definició del projecte amb PAPIK, ja sigui de construcció, promoció o rehabilitació, amb pressupost i certificació energètica esperada definits. A continuació, PAPIK presenta tècnicament el projecte a Banc Sabadell amb la documentació estandaritzada del canal preferent, evitant que el client gestioni aquesta documentació pel seu compte."
          )],
          spacing: { after: 200 },
        }),
        new Paragraph({
          children: [new TextRun(
            "El Banc avalua el perfil del client i les condicions específiques aplicables, segons els seus criteris de risc i solvència. Si l'avaluació és favorable, l'entitat formula una proposta hipotecària concreta al client, que decideix individualment si l'accepta o si negocia amb altres entitats."
          )],
          spacing: { after: 200 },
        }),
        new Paragraph({
          children: [new TextRun(
            "La formalització, en cas que el client decideixi avançar, és un contracte hipotecari directe entre el client i Banc Sabadell. PAPIK no és part d'aquest contracte. L'acompanyament tècnic durant tot el procés es coordina entre el departament d'autopromoció de PAPIK i el comercial."
          )],
          spacing: { after: 280 },
        }),

        // H2 6 FAQ
        new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun('6. Preguntes freqüents')] }),

        new Paragraph({ heading: HeadingLevel.HEADING_3, children: [new TextRun('Quines són les condicions concretes de la hipoteca verda?')] }),
        new Paragraph({
          children: [new TextRun(
            "Les condicions concretes (tipus d'interès, termini, comissions, productes vinculats) són privades i exclusives per a cada client que sol·liciti l'opció a través de PAPIK. Es comuniquen individualment durant el procés d'avaluació, motiu pel qual no es publiquen aquí."
          )],
          spacing: { after: 200 },
        }),

        new Paragraph({ heading: HeadingLevel.HEADING_3, children: [new TextRun("Tinc garantida l'aprovació de la hipoteca?")] }),
        new Paragraph({
          children: [new TextRun(
            "No. L'aprovació depèn dels criteris de risc i solvència de Banc Sabadell, que avalua cada client segons els seus paràmetres habituals. PAPIK facilita l'accés al canal preferent però no influeix en la decisió de concessió."
          )],
          spacing: { after: 200 },
        }),

        new Paragraph({ heading: HeadingLevel.HEADING_3, children: [new TextRun('Puc usar aquesta opció amb una rehabilitació energètica?')] }),
        new Paragraph({
          children: [new TextRun(
            "Sí. El finançament verd és compatible amb projectes de rehabilitació energètica, habitualment com a complement a les ajudes Next Generation EU. PAPIK estructura la combinació òptima de finançament durant la fase de projecte."
          )],
          spacing: { after: 200 },
        }),

        new Paragraph({ heading: HeadingLevel.HEADING_3, children: [new TextRun("L'acord és exclusiu? Puc negociar amb altres entitats?")] }),
        new Paragraph({
          children: [new TextRun(
            "L'acord PAPIK i Sabadell és un canal preferent, però no exclusiu. El client pot negociar la seva hipoteca amb qualsevol altra entitat financera. La nostra recomanació és comparar sempre vàries opcions abans de signar."
          )],
          spacing: { after: 200 },
        }),

        new Paragraph({ heading: HeadingLevel.HEADING_3, children: [new TextRun('Quin tipus de certificació energètica acredita el meu projecte?')] }),
        new Paragraph({
          children: [new TextRun(
            "Una vivenda PAPIK pot acreditar diversos nivells: certificat energètic A, certificació Passivhaus en les seves modalitats Standard, Plus o Premium, o EnerPHit per a rehabilitació. Cada nivell té implicacions financeres específiques que orientem en cada cas concret durant la fase d'avaluació del projecte."
          )],
          spacing: { after: 280 },
        }),

        // CIERRE
        new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun('Comencem la conversa')] }),
        new Paragraph({
          children: [new TextRun(
            "Si està valorant un projecte amb PAPIK i vol explorar l'opció d'hipoteca verda amb Banc Sabadell, podem incorporar-ho a la fase de planificació financera. La conversa inicial es fa sense compromís i orienta sobre quina estructura encaixa millor amb el seu cas."
          )],
          spacing: { after: 200 },
        }),
        new Paragraph({
          children: [
            new TextRun({ text: 'Sol·licitar informació sobre finançament verd: ', bold: true }),
            new TextRun('contacte general de PAPIK.'),
          ],
          spacing: { after: 120 },
        }),
        new Paragraph({
          children: [
            new TextRun({ text: 'Configurar el pressupost del meu projecte: ', bold: true }),
            new TextRun('papik.cat/pressupost.'),
          ],
          spacing: { after: 280 },
        }),

        // LLEGIU TAMBÉ
        new Paragraph({
          children: [new TextRun({ text: 'Llegiu també', bold: true, size: 24, color: '666666' })],
          spacing: { before: 240, after: 160 },
        }),
        new Paragraph({
          children: [new TextRun({ text: 'Hipoteca energètica: què és i quan val la pena.', italics: true })],
          spacing: { after: 100 },
        }),
        new Paragraph({
          children: [new TextRun({ text: 'Construcció: de zero a clau en mà.', italics: true })],
          spacing: { after: 100 },
        }),
        new Paragraph({
          children: [new TextRun({ text: 'Promoció: cases ja construïdes o amb entrega tancada.', italics: true })],
          spacing: { after: 100 },
        }),
        new Paragraph({
          children: [new TextRun({ text: 'Rehabilitació energètica i Next Generation EU.', italics: true })],
          spacing: { after: 100 },
        }),
      ],
    },
  ],
});

Packer.toBuffer(doc).then((buffer) => {
  const out = '/Users/trisfisas/Desktop/CÓDIGO/papik-web/seo-internal/exports/article-nota-premsa-papik-sabadell-ca-v2.docx';
  fs.writeFileSync(out, buffer);
  console.log('OK · Fitxer v2 generat:', out);
  console.log('Mida:', (buffer.length / 1024).toFixed(1), 'KB');
});
