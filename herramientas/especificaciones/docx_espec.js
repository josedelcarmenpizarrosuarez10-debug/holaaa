// Word de especificaciones tecnicas a partir del JSON de espec.py
const fs = require("fs");
const D = require("docx");
const { Document, Packer, Paragraph, TextRun, HeadingLevel, AlignmentType, Table, TableRow, TableCell, WidthType, BorderStyle,
        ShadingType, Header, Footer, PageNumber, TableOfContents, LevelFormat, PageBreak, TabStopType, ImageRun } = D;
const [, , entrada, salida] = process.argv;
const J = JSON.parse(fs.readFileSync(entrada, "utf8"));
const FUENTE = "Arial";
const AZUL = "1F3864";
const ANCHO = 9071;            // A4 (11906) menos margenes de 3.0 cm (1701) y 2.0 cm (1134)
const COD = J.codigo || ("CUI N.° " + J.cui);   // codigo del proyecto (CUI; o C.I. si aun no tiene CUI)
const txt = (s, o = {}) => new TextRun({ text: s, font: FUENTE, size: o.size || 20, bold: o.bold, italics: o.italics, color: o.color, allCaps: o.caps });
const par = (s, o = {}) => new Paragraph({ children: [txt(s, o)], alignment: o.align || AlignmentType.JUSTIFIED, spacing: { after: o.after ?? 100, before: o.before || 0, line: 276 }, indent: o.indent });
const borde = { style: BorderStyle.SINGLE, size: 4, color: "808080" };
const bordes = { top: borde, bottom: borde, left: borde, right: borde };

function tabla(cab, filas) {
  const n = cab.length;
  const pesos = n === 3 ? [26, 50, 24] : Array(n).fill(100 / n);
  const cols = pesos.map(p => Math.round(ANCHO * p / 100)); cols[n - 1] = ANCHO - cols.slice(0, n - 1).reduce((a, b) => a + b, 0);
  const celda = (s, i, head) => new TableCell({ borders: bordes, width: { size: cols[i], type: WidthType.DXA },
    shading: head ? { fill: "D9E2F3", type: ShadingType.CLEAR, color: "auto" } : undefined, margins: { top: 60, bottom: 60, left: 90, right: 90 },
    children: [new Paragraph({ children: [txt(String(s), { size: 17, bold: head })], alignment: head ? AlignmentType.CENTER : AlignmentType.LEFT })] });
  return new Table({ width: { size: ANCHO, type: WidthType.DXA }, columnWidths: cols,
    rows: [new TableRow({ tableHeader: true, children: cab.map((c, i) => celda(c, i, true)) }), ...filas.map(f => new TableRow({ children: f.map((c, i) => celda(c, i, false)) }))] });
}

function bloques(lista) {
  const out = [];
  for (const b of lista) {
    if (b[0] === "p") out.push(par(b[1]));
    else if (b[0] === "l") for (const it of b[1]) out.push(new Paragraph({ children: [txt(it)], numbering: { reference: "vinetas", level: 0 }, alignment: AlignmentType.JUSTIFIED, spacing: { after: 60, line: 264 } }));
    else if (b[0] === "t") { out.push(tabla(b[1], b[2])); out.push(par("", { after: 60 })); }
  }
  return out;
}

const H = [HeadingLevel.HEADING_1, HeadingLevel.HEADING_2, HeadingLevel.HEADING_3, HeadingLevel.HEADING_4, HeadingLevel.HEADING_5];
const titulo = (s, nivel, saltoAntes) => new Paragraph({ heading: H[nivel], pageBreakBefore: !!saltoAntes, children: [new TextRun({ text: s })], keepNext: true });

// ---------------------------------------------------------------- portada
const portada = [
  par("", { after: 1400 }),
  par(J.entidad, { align: AlignmentType.CENTER, bold: true, size: 24, after: 600 }),
  par("EXPEDIENTE TÉCNICO", { align: AlignmentType.CENTER, bold: true, size: 26, after: 200, color: AZUL }),
  par("ESPECIFICACIONES TÉCNICAS", { align: AlignmentType.CENTER, bold: true, size: 40, after: 200, color: AZUL }),
  par("ESPECIALIDAD: " + J.especialidad, { align: AlignmentType.CENTER, bold: true, size: 24, after: 900 }),
  par("PROYECTO:", { align: AlignmentType.CENTER, bold: true, size: 20, after: 120 }),
  par(J.proyecto, { align: AlignmentType.CENTER, size: 22, after: 300 }),
  par(COD, { align: AlignmentType.CENTER, bold: true, size: 24, after: 900 }),
  par("UBICACIÓN: " + J.ubicacion, { align: AlignmentType.CENTER, size: 20, after: 120 }),
  par(J.fecha, { align: AlignmentType.CENTER, bold: true, size: 20 }),
];

// caratula con foto (J.caratula: textos y foto de la caratula comun del proyecto; sin ella, la portada anterior)
let portadaFinal = portada;
if (J.caratula) {
  const C = J.caratula, CEN = AlignmentType.CENTER, wpx = 586;            // foto de 15.5 cm de ancho
  const cpar = (s, o = {}) => par(s, Object.assign({ align: CEN }, o));
  const sin = { style: BorderStyle.NONE, size: 0, color: "FFFFFF" };
  const banda = new Table({ width: { size: ANCHO, type: WidthType.DXA }, columnWidths: [ANCHO], alignment: CEN,
    rows: [new TableRow({ children: [new TableCell({ width: { size: ANCHO, type: WidthType.DXA }, borders: { top: sin, bottom: sin, left: sin, right: sin },
      shading: { fill: AZUL, type: ShadingType.CLEAR, color: "auto" }, margins: { top: 120, bottom: 120, left: 120, right: 120 },
      children: [new Paragraph({ alignment: CEN, spacing: { after: 40 }, children: [txt(C.titulo, { bold: true, size: 40, color: "FFFFFF" })] }),
                 new Paragraph({ alignment: CEN, children: [txt(C.subtitulo, { bold: true, size: 22, color: "FFFFFF" })] })] })] })] });
  portadaFinal = [
    cpar(C.entidad, { bold: true, size: 30, color: AZUL, after: 0 }),
    new Paragraph({ alignment: CEN, border: { bottom: { style: BorderStyle.SINGLE, size: 12, color: AZUL, space: 4 } }, spacing: { after: 160 },
                    children: [txt(C.gerencia, { bold: true, size: 22, color: "595959" })] }),
    cpar(C.expediente, { bold: true, size: 24, color: AZUL, after: 80 }),
    cpar(C.proyecto, { bold: true, size: 23, after: 40 }),
    cpar(C.ci, { bold: true, size: 22, color: AZUL, after: 160 }),
    new Paragraph({ alignment: CEN, children: [new ImageRun({ type: "jpg", data: fs.readFileSync(C.foto),
                    transformation: { width: wpx, height: Math.round(wpx * C.proporcion) } })] }),
    cpar(C.leyenda, { italics: true, size: 16, color: "595959", after: 160 }),
    banda,
    cpar(C.especialidad, { bold: true, size: 21, before: 200, after: 40 }),
    cpar(C.ubicacion, { size: 20, after: 160 }),
    cpar(C.fecha, { bold: true, size: 24, color: AZUL }),
  ];
}

// ---------------------------------------------------------------- cuerpo
const cuerpo = [];
cuerpo.push(new Paragraph({ children: [txt("ÍNDICE", { bold: true, size: 26, color: AZUL })], alignment: AlignmentType.CENTER, spacing: { after: 200 } }));
cuerpo.push(new TableOfContents("Índice", { hyperlink: true, headingStyleRange: "1-4" }));
cuerpo.push(titulo("CAPÍTULO I. GENERALIDADES", 0, true));
J.generalidades.forEach((g, i) => { cuerpo.push(titulo(`1.${i + 1}  ${g[0]}`, 1)); cuerpo.push(...bloques(g[1])); });
cuerpo.push(titulo("CAPÍTULO II. ESPECIFICACIONES TÉCNICAS POR PARTIDA", 0, true));
cuerpo.push(par("Las partidas se presentan con la numeración, la descripción y la unidad del metrado de la especialidad. Los títulos agrupan partidas y no tienen medición ni pago propio."));
for (const it of J.partidas) {
  const nivel = Math.min(1 + it.nivel, 4);
  cuerpo.push(titulo(`${it.codigo}  ${it.desc}` + (it.und ? `  (${it.und})` : ""), nivel, it.nivel === 0 && J.partidas.indexOf(it) > 0));
  if (!it.secciones) continue;
  for (const [nombre, cont] of it.secciones) {
    cuerpo.push(new Paragraph({ children: [txt(nombre, { bold: true, size: 19, color: AZUL })], spacing: { before: 120, after: 60 }, keepNext: true }));
    cuerpo.push(...bloques(cont));
  }
}

const cab = new Header({ children: [new Paragraph({ border: { bottom: { style: BorderStyle.SINGLE, size: 6, color: AZUL, space: 2 } }, tabStops: [{ type: TabStopType.RIGHT, position: ANCHO }],
  children: [txt("ESPECIFICACIONES TÉCNICAS - DRENAJE PLUVIAL", { size: 15, bold: true, color: AZUL }), txt("\t" + J.corto + " - " + COD, { size: 15, color: AZUL })] })] });
const pie = new Footer({ children: [new Paragraph({ alignment: AlignmentType.RIGHT, children: [txt("Página ", { size: 16 }), new TextRun({ children: [PageNumber.CURRENT], font: FUENTE, size: 16 }), txt(" de ", { size: 16 }), new TextRun({ children: [PageNumber.TOTAL_PAGES], font: FUENTE, size: 16 })] })] });
const pagina = { size: { width: 11906, height: 16838 }, margin: { top: 1418, bottom: 1134, left: 1701, right: 1134, header: 567, footer: 567 } };

const doc = new Document({
  creator: "Proyectista", title: "Especificaciones técnicas - Drenaje pluvial - " + J.corto, features: { updateFields: true },
  styles: {
    default: { document: { run: { font: FUENTE, size: 20 } } },
    paragraphStyles: [
      { id: "Heading1", name: "Heading 1", basedOn: "Normal", next: "Normal", quickFormat: true, run: { font: FUENTE, size: 26, bold: true, color: AZUL }, paragraph: { spacing: { before: 240, after: 200 }, outlineLevel: 0, alignment: AlignmentType.CENTER } },
      { id: "Heading2", name: "Heading 2", basedOn: "Normal", next: "Normal", quickFormat: true, run: { font: FUENTE, size: 22, bold: true, color: AZUL }, paragraph: { spacing: { before: 240, after: 120 }, outlineLevel: 1 } },
      { id: "Heading3", name: "Heading 3", basedOn: "Normal", next: "Normal", quickFormat: true, run: { font: FUENTE, size: 21, bold: true }, paragraph: { spacing: { before: 200, after: 100 }, outlineLevel: 2 } },
      { id: "Heading4", name: "Heading 4", basedOn: "Normal", next: "Normal", quickFormat: true, run: { font: FUENTE, size: 20, bold: true }, paragraph: { spacing: { before: 200, after: 80 }, outlineLevel: 3 } },
      { id: "Heading5", name: "Heading 5", basedOn: "Normal", next: "Normal", quickFormat: true, run: { font: FUENTE, size: 20, bold: true, italics: true }, paragraph: { spacing: { before: 160, after: 80 }, outlineLevel: 4 } },
    ],
  },
  numbering: { config: [{ reference: "vinetas", levels: [{ level: 0, format: LevelFormat.BULLET, text: "•", alignment: AlignmentType.LEFT, style: { paragraph: { indent: { left: 567, hanging: 284 } } } }] }] },
  sections: [
    { properties: { page: pagina }, children: portadaFinal },
    { properties: { page: pagina }, headers: { default: cab }, footers: { default: pie }, children: cuerpo },
  ],
});
Packer.toBuffer(doc).then(b => { fs.writeFileSync(salida, b); console.log("ok", salida, b.length); });
