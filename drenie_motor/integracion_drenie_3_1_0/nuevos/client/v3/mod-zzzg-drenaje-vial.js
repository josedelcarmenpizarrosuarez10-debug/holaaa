/* DrenIE 3.1.0 · Drenaje vial (Manual de Hidrología, Hidráulica y Drenaje del MTC, R.D. N.° 20-2011-MTC/14).
   Página 16 y cinta DRENAJE VIAL: cunetas de la vía, alcantarillas de alivio y de paso de quebradas y badenes, con la lluvia de la
   pestaña LLUVIA. El cálculo lo hace el motor (orden vial, también en la demo); los entregables (memoria Word, memoria de cálculo
   Excel con fórmulas, metrado y planos DXF) usan la orden vial_entregables, con licencia. Los datos se guardan en el proyecto. */
var DV_ICONS = {
  vial_calc: '<rect x="3" y="4" width="22" height="22" rx="3" fill="#E0F2FE" stroke="#0B2545" stroke-width="1.6"/><path d="M6 20l6-12h4l6 12" stroke="#0B2545" stroke-width="1.6"/><path d="M14 9v3M14 15v2" stroke="#E08A12" stroke-width="1.6"/><circle cx="23.5" cy="23.5" r="6.5" fill="#1EA7F2"/><path d="M21.5 20.5v6l5-3z" fill="#fff"/>',
  vial_cuneta: '<path d="M2 9h8l5 9 5-9h10" fill="none" stroke="#0B2545" stroke-width="1.8"/><path d="M11 12h8" stroke="#1EA7F2" stroke-width="2"/><path d="M2 26h28" stroke="#64748B" stroke-width="1.4" stroke-dasharray="4 2.5"/>',
  vial_alc: '<path d="M2 12h28" stroke="#0B2545" stroke-width="1.6"/><circle cx="16" cy="20" r="6" fill="#E0F2FE" stroke="#0B2545" stroke-width="1.6"/><path d="M11 22h10" stroke="#1EA7F2" stroke-width="1.8"/><rect x="6" y="12" width="3" height="14" fill="#CBD5E1" stroke="#0B2545"/><rect x="23" y="12" width="3" height="14" fill="#CBD5E1" stroke="#0B2545"/>',
  vial_excel: '<rect x="4" y="4" width="20" height="24" rx="2" fill="#DCFCE7" stroke="#0B2545" stroke-width="1.5"/><path d="M9 11l7 9M16 11l-7 9" stroke="#16A34A" stroke-width="2.2"/><path d="M20 22l5 5M25 22v5h-5" stroke="#0B6FC0" stroke-width="1.8"/>'
};
Object.keys(DV_ICONS).forEach(function (k) { V3_RIB_ICONS[k] = DV_ICONS[k]; });
V3_RIB_TABS.splice(V3_RIB_TABS.findIndex(function (t) { return t[0] === 'red'; }) + 1, 0, ['vial', 'DRENAJE VIAL']);
V3_STEP_TAB[16] = 'vial';
V3_NAV.splice(V3_NAV.findIndex(function (n) { return n[0] === 15; }) + 1, 0, [16, 'Drenaje vial', 'V', 'profile']);
(function () {
  var css = '.dv-tabla input,.dv-tabla select{width:100%;min-width:52px;box-sizing:border-box;font:inherit;padding:2px 4px}.dv-tabla select{min-width:104px}' +
    '.dv-tabla td{padding:2px 3px}.dv-tabla th{font-size:11px;white-space:normal}.dv-ok{color:#15803D;font-weight:600}.dv-mal{color:#B91C1C;font-weight:600}' +
    '.dv-rev{color:#B45309;font-weight:600}.dv-res td,.dv-res th{padding:3px 6px}.dv-chips{display:flex;gap:8px;flex-wrap:wrap;margin:6px 0}';
  var s = document.createElement('style'); s.textContent = css; document.head.appendChild(s);
})();

var DV = { aviso: null, verNormas: false, resultado: null, archivos: null, carpeta: '' };
// Columnas de cada tabla: [clave, título, tipo (n = número, t = texto, o = opciones), opciones]
var DV_CUN = [['id', 'Código', 't'], ['lado', 'Lado', 'o', [['izquierdo', 'Izquierdo'], ['derecho', 'Derecho']]], ['prog_ini', 'Prog. inicio (m)', 'n'],
  ['prog_fin', 'Prog. fin (m)', 'n'], ['pendiente_pct', 'Pendiente (%)', 'n'], ['revestimiento', 'Revestimiento', 'o', [['concreto', 'Concreto'], ['tierra', 'Tierra'], ['roca', 'Roca']]],
  ['tipo', 'Sección', 'o', [['', 'Mínima MTC'], ['triangular', 'Triangular'], ['trapezoidal', 'Trapezoidal'], ['rectangular', 'Rectangular']]],
  ['d', 'Prof. d (m)', 'n'], ['a', 'Ancho a o fondo b (m)', 'n'], ['w1', 'Calzada y berma (m)', 'n'], ['c1', 'C', 'n'], ['w2', 'Talud de corte (m)', 'n'],
  ['c2', 'C', 'n'], ['w3', 'Ladera (m)', 'n'], ['c3', 'C', 'n']];
var DV_COB = [['bosques', 'Bosques'], ['pastos', 'Pastos'], ['cultivos', 'Cultivos'], ['hierba', 'Hierba, grama'], ['sin_vegetacion', 'Sin vegetación']];
var DV_SUE = [['semipermeable', 'Semipermeable'], ['permeable', 'Permeable'], ['impermeable', 'Impermeable']];
var DV_ALC = [['id', 'Código', 't'], ['prog', 'Progresiva (m)', 'n'], ['tipo', 'Tipo', 'o', [['cruce', 'Paso de quebrada'], ['alivio', 'Alivio']]],
  ['area_km2', 'Área (km²)', 'n'], ['L_m', 'L cauce (m)', 'n'], ['H_m', 'Desnivel H (m)', 'n'], ['cobertura', 'Cobertura', 'o', DV_COB], ['suelo', 'Suelo', 'o', DV_SUE],
  ['C', 'C (opcional)', 'n'], ['cunetas', 'Recibe cunetas', 't'], ['tipo_conducto', 'Conducto', 'o', [['TMC', 'TMC'], ['MCA', 'Marco de concreto']]],
  ['diametro_pulg', 'Ø fijo (pulg)', 'n'], ['pendiente_pct', 'Pendiente (%)', 'n'], ['longitud_m', 'Longitud (m)', 'n']];
var DV_BAD = [['id', 'Código', 't'], ['prog', 'Progresiva (m)', 'n'], ['area_km2', 'Área (km²)', 'n'], ['L_m', 'L cauce (m)', 'n'], ['H_m', 'Desnivel H (m)', 'n'],
  ['cobertura', 'Cobertura', 'o', DV_COB], ['suelo', 'Suelo', 'o', DV_SUE], ['cunetas', 'Recibe cunetas', 't'], ['b', 'Fondo b (m)', 'n'], ['z', 'Talud z', 'n'],
  ['profundidad', 'Profundidad (m)', 'n'], ['pendiente_pct', 'Pendiente transversal (%)', 'n']];
var DV_VIA = [['velocidad_kmh', 'Velocidad de diseño (km/h)'], ['imda', 'IMDA (veh/día)'], ['precipitacion_anual_mm', 'Precipitación media anual (mm)'],
  ['talud_corte_z', 'Talud de corte z (H por 1 V)'], ['ancho_plataforma', 'Ancho de plataforma (m)'], ['longitud_alivio_m', 'Longitud de alivios (m)'],
  ['pendiente_alivio_pct', 'Pendiente de alivios (%)']];
var DV_EJEMPLO = {
  via: { velocidad_kmh: 40, imda: 350, precipitacion_anual_mm: 2300, talud_corte_z: 0.5, ancho_plataforma: 7, longitud_alivio_m: 8, pendiente_alivio_pct: 2, selva_alta: false },
  cunetas: [{ id: 'CU-01', lado: 'izquierdo', prog_ini: 0, prog_fin: 480, pendiente_pct: 1.2, revestimiento: 'concreto', tipo: 'triangular', d: 0.4, a: 1.2, w1: 3, c1: 0.86, w2: 6, c2: 0.55, w3: 20, c3: 0.35 },
    { id: 'CU-02', lado: 'izquierdo', prog_ini: 520, prog_fin: 1200, pendiente_pct: 3.5, revestimiento: 'concreto', tipo: 'triangular', d: 0.4, a: 1.2, w1: 3, c1: 0.86, w2: 8, c2: 0.55 }],
  alcantarillas: [{ id: 'AC-01', prog: 500, tipo: 'cruce', area_km2: 0.42, L_m: 1150, H_m: 95, cobertura: 'bosques', suelo: 'semipermeable', cunetas: 'CU-01', tipo_conducto: 'TMC', pendiente_pct: 3, longitud_m: 9 },
    { id: 'AC-02', prog: 1200, tipo: 'cruce', area_km2: 2.8, L_m: 3100, H_m: 210, cobertura: 'bosques', suelo: 'semipermeable', cunetas: 'CU-02', tipo_conducto: 'TMC', pendiente_pct: 2, longitud_m: 10 }],
  badenes: [{ id: 'BA-01', prog: 860, area_km2: 0.9, L_m: 1600, H_m: 120, cobertura: 'pastos', suelo: 'semipermeable', cunetas: '', b: 6, z: 10, profundidad: 0.8, pendiente_pct: 2.5 }]
};

function dvAvisar() { window.dispatchEvent(new Event('drenie-vial')); window.dispatchEvent(new Event('drenie-ui')); }
function dvDatos(st) { return st.drenajeVial || { via: Object.assign({}, DV_EJEMPLO.via), cunetas: [], alcantarillas: [], badenes: [] }; }
function dvGuardar(setState, fn) { setState(function (prev) { var d = JSON.parse(JSON.stringify(dvDatos(prev))); fn(d); return Object.assign({}, prev, { drenajeVial: d }); }); DV.resultado = null; }
function dvNum(v) { if (v === '' || v == null) return null; var n = Number(String(v).replace(',', '.')); return isFinite(n) ? n : v; }
function dvOcupado(texto, fn) { DV.aviso = { texto: texto, desde: Date.now() }; dvAvisar(); return Promise.resolve().then(fn).finally(function () { DV.aviso = null; dvAvisar(); }); }

// Lluvia de la pestaña LLUVIA → serie de máximas mensuales, factor 1.13 si está activo y la distribución elegida por K-S.
function dvLluvia(st) {
  var s = st.statistics || {}, rows = (s.rows || []).filter(function (r) { return r.included !== false; });
  var serie = {};
  rows.forEach(function (r) { var m = (r.months || []).map(function (v) { var n = DrenStats.num(v); return n === null ? null : n; }); if (m.some(function (v) { return v !== null; })) serie[String(r.year)] = m; });
  var n = Object.keys(serie).length;
  if (n < 10) return { error: 'Cargue la serie de precipitación máxima en 24 h en LLUVIA → Análisis estadístico (por lo menos 10 años; ' + n + ' ahora).' };
  var res = null; try { res = DrenStats.calculate(s); } catch (e) {}
  var dist = { normal: 'normal', lognormal: 'lognormal', pearson: 'lp3', gumbel: 'gumbel' }[res && res.selected] || null;
  var f = s.fixedInterval ? (s.fixedFactor === undefined ? 1.13 : DrenStats.num(s.fixedFactor) || 1) : 1;
  var est = s.station && (s.station.name || s.station.nombre) || s.sourceName || '';
  return { serie: serie, factor: f, distribucion: dist || undefined, estacion: { name: est }, anios: n,
    texto: n + ' años' + (est ? ' · ' + est : '') + (f !== 1 ? ' · factor ' + fmt(f, 2) : '') + (dist ? ' · ' + DrenStats.names[res.selected] : '') };
}
// Datos de la pantalla → JSON del motor
function dvEntrada(st) {
  var d = dvDatos(st), via = {}, ll = dvLluvia(st), pr = st.project || {};
  DV_VIA.forEach(function (c) { var v = dvNum(d.via[c[0]]); if (v !== null) via[c[0].replace('_pct', '')] = c[0].slice(-4) === '_pct' ? v / 100 : v; });
  via.selva_alta = !!d.via.selva_alta;
  function obra(x) {
    var o = {};
    Object.keys(x).forEach(function (k) { var v = x[k]; if (v === '' || v == null) return; o[k] = ['id', 'lado', 'tipo', 'revestimiento', 'cobertura', 'suelo', 'cunetas', 'tipo_conducto'].indexOf(k) >= 0 ? v : dvNum(v); });
    if (o.pendiente_pct != null) { o[o.b != null && o.z != null ? 'pendiente_transversal' : 'pendiente'] = o.pendiente_pct / 100; delete o.pendiente_pct; }
    if (o.cunetas != null) o.cunetas = String(o.cunetas).split(/[,;\s]+/).filter(Boolean);
    if (o.cobertura) { o.coberturas = [{ fraccion: 1, cobertura: o.cobertura, suelo: o.suelo || 'semipermeable' }]; delete o.cobertura; delete o.suelo; }
    return o;
  }
  var cun = d.cunetas.map(function (x) {
    var o = obra(x), sec = null;
    if (o.tipo) { sec = { tipo: o.tipo, d: o.d }; if (o.tipo === 'triangular') sec.a = o.a; else sec.b = o.a; }
    var ap = [];
    [['w1', 'c1', 'Calzada y berma'], ['w2', 'c2', 'Talud de corte'], ['w3', 'c3', 'Ladera']].forEach(function (k) { if (o[k[0]] != null && o[k[1]] != null) ap.push({ descripcion: k[2], ancho: o[k[0]], C: o[k[1]] }); });
    ['tipo', 'd', 'a', 'w1', 'c1', 'w2', 'c2', 'w3', 'c3'].forEach(function (k) { delete o[k]; });
    if (sec && sec.d != null) o.seccion = sec; if (ap.length) o.aportes = ap;
    return o;
  });
  return { proyecto: { nombre: pr.name || 'Proyecto vial', ubicacion: pr.location || '', entidad: pr.entity || '', codigo: pr.code || pr.cui || '' },
    lluvia: ll.error ? {} : { serie: ll.serie, factor: ll.factor, distribucion: ll.distribucion, estacion: ll.estacion },
    via: via, cunetas: cun, alcantarillas: d.alcantarillas.map(obra), badenes: d.badenes.map(obra) };
}
// Plantilla Excel leída por el motor → filas de la pantalla
function dvDesdeMotor(x) {
  var via = Object.assign({}, DV_EJEMPLO.via, x.via || {});
  if (via.pendiente_alivio != null) via.pendiente_alivio_pct = +(via.pendiente_alivio * 100).toFixed(3);
  function fila(o) {
    var r = Object.assign({}, o);
    if (r.pendiente != null) { r.pendiente_pct = +(r.pendiente * 100).toFixed(4); delete r.pendiente; }
    if (r.pendiente_transversal != null) { r.pendiente_pct = +(r.pendiente_transversal * 100).toFixed(4); delete r.pendiente_transversal; }
    if (r.coberturas && r.coberturas[0]) { r.cobertura = r.coberturas[0].cobertura; r.suelo = r.coberturas[0].suelo; delete r.coberturas; }
    if (Array.isArray(r.cunetas)) r.cunetas = r.cunetas.join(', ');
    if (r.seccion) { r.tipo = r.seccion.tipo; r.d = r.seccion.d; r.a = r.seccion.a != null ? r.seccion.a : r.seccion.b; delete r.seccion; }
    (r.aportes || []).slice(0, 3).forEach(function (a, i) { r['w' + (i + 1)] = a.ancho; r['c' + (i + 1)] = a.C; }); delete r.aportes;
    return r;
  }
  return { via: via, cunetas: (x.cunetas || []).map(fila), alcantarillas: (x.alcantarillas || []).map(fila), badenes: (x.badenes || []).map(fila) };
}

function dvCalcular(props) {
  var st = props.state, ll = dvLluvia(st);
  if (ll.error) { v3Notice(ll.error, { title: 'Lluvia de diseño' }); return; }
  var e = dvEntrada(st);
  if (!e.cunetas.length && !e.alcantarillas.length && !e.badenes.length) { v3Notice('Agregue cunetas, alcantarillas o badenes (o cargue el ejemplo).', { title: 'Drenaje vial' }); return; }
  dvOcupado('Calculando el drenaje vial', function () { return rcMotor('vial', [], e); }).then(function (r) { DV.resultado = r; DV.archivos = null; DV.verNormas = false; dvAvisar(); })
    .catch(function (er) { rcError('Drenaje vial', er); });
}
function dvEntregables(props) {
  var ll = dvLluvia(props.state);
  if (ll.error) { v3Notice(ll.error, { title: 'Lluvia de diseño' }); return; }
  rcElegir('carpeta').then(function (c) {
    if (!c) return;
    return dvOcupado('Generando la memoria, el metrado y los planos del drenaje vial', function () { return rcMotor('vial_entregables', [c], dvEntrada(props.state)); })
      .then(function (r) { DV.resultado = r; DV.archivos = r.archivos || []; DV.carpeta = c; dvAvisar(); });
  }).catch(function (er) { rcError('Entregables del drenaje vial', er); });
}
function dvImportar(props) {
  rcElegir('plantilla').then(function (r) {
    if (!r) return;
    return rcMotor('vial', [], { leer_plantilla: r }).then(function (x) {
      var d = dvDesdeMotor(x.datos);
      props.setState(function (prev) { return Object.assign({}, prev, { drenajeVial: d }); }); DV.resultado = null; dvAvisar();
      v3Notice('Se cargaron ' + d.cunetas.length + ' cunetas, ' + d.alcantarillas.length + ' alcantarillas y ' + d.badenes.length + ' badenes de la plantilla.', { title: 'Drenaje vial' });
    });
  }).catch(function (er) { rcError('Plantilla del drenaje vial', er); });
}
function dvPlantilla(props) {
  rcElegir('carpeta').then(function (c) {
    if (!c) return;
    return rcMotor('vial', [], { crear_plantilla: true, carpeta: c, datos: dvEntrada(props.state) }).then(function (r) {
      v3Notice('Plantilla guardada: ' + r.archivos[0] + '. Llénela en Excel y cárguela con «Importar Excel».', { title: 'Drenaje vial' });
    });
  }).catch(function (er) { rcError('Plantilla del drenaje vial', er); });
}
function dvEjemplo(props) {
  var hay = dvDatos(props.state);
  function poner() { props.setState(function (prev) { return Object.assign({}, prev, { drenajeVial: JSON.parse(JSON.stringify(DV_EJEMPLO)) }); }); DV.resultado = null; dvAvisar(); }
  if (hay.cunetas.length || hay.alcantarillas.length || hay.badenes.length) v3Ask('Se reemplazan los datos del drenaje vial por el ejemplo.', poner, { ok: 'Sí, cargar el ejemplo', title: 'Ejemplo de drenaje vial' });
  else poner();
}

function v3VialRibbon(props) {
  function go() { if (props.home || props.state.step !== 16) v3Go(props, 16); }
  var on = !props.home && props.state.step === 16;
  return [
    rbGrp('Datos', [rbBig('vial_cuneta', 'Datos de\nla vía', function () { DV.verNormas = false; DV.resultado = null; go(); dvAvisar(); }, { on: on && !DV.resultado && !DV.verNormas, k: 'dat' }),
      rbBig('vial_excel', 'Importar\nExcel', function () { go(); dvImportar(props); }, { k: 'imp' }),
      rbCol(rbSm('excel', 'Plantilla Excel', function () { go(); dvPlantilla(props); }, { k: 'pla' }), rbSm('vial_alc', 'Cargar ejemplo', function () { go(); dvEjemplo(props); }, { k: 'eje' }))]),
    rbGrp('Cálculo', [rbBig('vial_calc', 'Calcular', function () { go(); dvCalcular(props); }, { on: on && !!DV.resultado && !DV.verNormas, k: 'cal' }),
      rbBig('red_entreg', 'Entregables', function () { go(); dvEntregables(props); }, { k: 'ent', title: 'Memoria Word, memoria de cálculo Excel, metrado y planos DXF' })]),
    rbGrp('Normas', [rbBig('red_normas', 'Normas y\nfuentes', function () { DV.verNormas = true; go(); dvAvisar(); }, { on: on && DV.verNormas, k: 'nor' })])
  ];
}

function dvCelda(c, v, cambiar) {
  if (c[2] === 'o') return h('select', { value: v == null ? '' : v, 'aria-label': c[1], onChange: function (e) { cambiar(e.target.value); } },
    c[3].map(function (o) { return h('option', { key: o[0], value: o[0] }, o[1]); }));
  return h('input', { value: v == null ? '' : v, 'aria-label': c[1], inputMode: c[2] === 'n' ? 'decimal' : undefined, onChange: function (e) { cambiar(e.target.value); } });
}
function DvTabla(props) {
  var filas = props.filas, cols = props.cols;
  function set(i, k, v) { props.cambiar(function (lista) { lista[i][k] = v; }); }
  return h('section', { className: 'card' }, h('div', { className: 'section-heading' }, h('h2', null, props.titulo),
      h(Btn, { onClick: function () { props.cambiar(function (lista) { var n = props.nuevo(lista.length + 1); var u = lista[lista.length - 1]; if (u && n.prog_ini != null && u.prog_fin != null) { n.prog_ini = u.prog_fin; } lista.push(n); }); } }, 'Agregar fila')),
    props.nota ? h('p', { className: 'muted small' }, props.nota) : null,
    filas.length ? h('div', { className: 'table-wrap' }, h('table', { className: 'rc-tabla dv-tabla' },
      h('thead', null, h('tr', null, cols.map(function (c, j) { return h('th', { key: j }, c[1]); }).concat([h('th', { key: 'x' }, '')]))),
      h('tbody', null, filas.map(function (f, i) {
        return h('tr', { key: i }, cols.map(function (c, j) { return h('td', { key: j }, dvCelda(c, f[c[0]], function (v) { set(i, c[0], v); })); })
          .concat([h('td', { key: 'x' }, h('button', { type: 'button', className: 'btn', title: 'Quitar fila', onClick: function () { props.cambiar(function (lista) { lista.splice(i, 1); }); } }, '×'))]));
      })))) : h('p', { className: 'muted' }, 'Sin filas.'));
}
function dvEstado(e) { return h('span', { className: e === 'CUMPLE' ? 'dv-ok' : e === 'NO CUMPLE' ? 'dv-mal' : 'dv-rev' }, e); }
function dvProg(p) { var k = Math.floor(p / 1000); return k + '+' + ('000' + (p - 1000 * k).toFixed(2)).slice(-6); }
function DvResultado() {
  var R = DV.resultado, t = R.totales;
  function tabla(cab, filas) {
    return h('div', { className: 'table-wrap' }, h('table', { className: 'rc-tabla dv-res' }, h('thead', null, h('tr', null, cab.map(function (c, j) { return h('th', { key: j }, c); }))),
      h('tbody', null, filas.map(function (f, i) { return h('tr', { key: i }, f.map(function (v, j) { return h('td', { key: j }, v); })); }))));
  }
  return h(React.Fragment, null,
    h('section', { className: 'card' }, h('h2', null, 'Resultado'),
      h('div', { className: 'dv-chips' }, h('span', { className: 'rc-chip ok' }, fmt(t.cunetas_m, 0) + ' m de cunetas'), h('span', { className: 'rc-chip ok' }, t.alivios + ' alcantarillas de alivio'),
        h('span', { className: 'rc-chip ok' }, t.cruces + ' de paso de quebrada'), h('span', { className: 'rc-chip ok' }, t.badenes + ' badenes'),
        h('span', { className: 'rc-chip' + (t.no_cumplen || t.revisar ? ' pend' : ' ok') }, t.no_cumplen + ' no cumplen · ' + t.revisar + ' por revisar')),
      h('p', { className: 'muted small' }, 'Lluvia: ' + R.lluvia.fuente + '. Región ' + R.region.toLowerCase() + '. Cunetas con T = ' + R.periodo_plataforma.T + ' años (riesgo ' +
        Math.round(R.periodo_plataforma.R * 100) + ' %, vida útil ' + R.periodo_plataforma.n + ' años).')),
    R.cunetas.length ? h('section', { className: 'card' }, h('h2', null, 'Cunetas'), tabla(['Cuneta', 'Tramo', 'S (%)', 'I (mm/h)', 'Q capacidad (m³/s)', 'V llena (m/s)', 'L máx. (m)', 'Descargas en', 'Estado'],
      R.cunetas.map(function (c) { return [c.id, dvProg(c.prog_ini) + ' – ' + dvProg(c.prog_fin), fmt(c.pendiente * 100, 2), fmt(c.I_mmh, 1), fmt(c.Q_capacidad, 3), fmt(c.V_lleno, 2), fmt(c.L_max, 0),
        c.tramos.map(function (s) { return dvProg(s.descarga_en); }).join(', '), dvEstado(c.estado)]; }))) : null,
    R.alcantarillas.length ? h('section', { className: 'card' }, h('h2', null, 'Alcantarillas'), tabla(['Obra', 'Prog.', 'Tipo', 'T (años)', 'Q (m³/s)', 'Sección', 'y/D', 'V (m/s)', 'd50 salida (m)', 'Estado'],
      R.alcantarillas.map(function (a) { return [a.id, dvProg(a.prog), a.tipo === 'alivio' ? 'Alivio' : 'Paso de quebrada', a.periodo.T, fmt(a.Q, 3), a.conducto, fmt(a.tirante_rel, 2), fmt(a.V, 2), fmt(a.d50_salida, 2), dvEstado(a.estado)]; }))) : null,
    R.badenes.length ? h('section', { className: 'card' }, h('h2', null, 'Badenes'), tabla(['Obra', 'Prog.', 'Q (m³/s)', 'Tirante (m)', 'Borde libre (m)', 'V (m/s)', 'Estado'],
      R.badenes.map(function (b) { return [b.id, dvProg(b.prog), fmt(b.Q, 3), fmt(b.tirante || 0, 3), fmt(b.borde_libre || 0, 2), fmt(b.V || 0, 2), dvEstado(b.estado)]; }))) : null,
    R.avisos.length ? h('section', { className: 'card' }, h('h2', null, 'Observaciones'), h('ul', null, R.avisos.map(function (a, i) { return h('li', { key: i }, a); }))) : null,
    DV.archivos ? h('section', { className: 'card' }, h('h2', null, 'Entregables'), h('ul', null, DV.archivos.filter(function (a) { return !/\.png$/i.test(a); }).map(function (a, i) { return h('li', { key: i }, a); })),
      h('div', { className: 'ws-actions' }, h(Btn, { variant: 'primary', onClick: function () { rcMotor('vial', [], { abrir_carpeta: DV.carpeta }).catch(function (e) { rcError('Abrir carpeta', e); }); } }, 'Abrir la carpeta'))) : null);
}
function DvAviso() {
  var t = useState(0);
  useEffect(function () { if (!DV.aviso) return; var k = setInterval(function () { t[1](function (n) { return n + 1; }); }, 1000); return function () { clearInterval(k); }; }, [DV.aviso && DV.aviso.desde]);
  if (!DV.aviso) return null;
  return h('div', { className: 'v3-dlg-overlay rc-velo', role: 'status', 'aria-live': 'polite' }, h('div', { className: 'v3-dlg rc-velo-caja' },
    h('div', { className: 'v3-dlg-main' }, h('div', { className: 'v3-dlg-body' }, h('h3', null, DV.aviso.texto + '…'), h('p', null, 'Tiempo: ' + Math.round((Date.now() - DV.aviso.desde) / 1000) + ' s.')),
      h('div', { className: 'rc-barra' }, h('i')))));
}
function DvPage(props) {
  var tick = useState(0);
  useEffect(function () { function f() { tick[1](function (n) { return n + 1; }); } window.addEventListener('drenie-vial', f); return function () { window.removeEventListener('drenie-vial', f); }; }, []);
  var st = props.state, d = dvDatos(st), ll = dvLluvia(st);
  function cambiar(grupo) { return function (fn) { dvGuardar(props.setState, function (x) { fn(x[grupo]); }); dvAvisar(); }; }
  function setVia(k, v) { dvGuardar(props.setState, function (x) { x.via[k] = v; }); dvAvisar(); }
  return h('div', { className: 'ws-page', 'data-workspace': 'vial' },
    wsHead('Drenaje vial', 'Cunetas de la vía, alcantarillas de alivio y de paso de quebradas y badenes según el Manual de Hidrología, Hidráulica y Drenaje del MTC (R.D. N.° 20-2011-MTC/14).'),
    DV.verNormas ? h(React.Fragment, null, h('div', { className: 'ws-actions' }, h(Btn, { onClick: function () { DV.verNormas = false; dvAvisar(); } }, 'Volver')), h(RcNormas)) :
    DV.resultado ? h(React.Fragment, null, h('div', { className: 'ws-actions' }, h(Btn, { onClick: function () { DV.resultado = null; dvAvisar(); } }, 'Volver a los datos'),
        h(Btn, { variant: 'primary', onClick: function () { dvEntregables(props); } }, 'Generar entregables')), h(DvResultado)) :
    h(React.Fragment, null,
      h('section', { className: 'card' }, h('h2', null, 'Datos de la vía y lluvia'),
        h('div', { className: 'ws-form-grid' }, DV_VIA.map(function (c) { return h(React.Fragment, { key: c[0] }, wsField(c[1], d.via[c[0]], function (v) { setVia(c[0], v); }, { inputMode: 'decimal' })); }),
          h('label', { className: 'ws-field' }, h('span', null, 'Selva alta con cauces en V'), h('select', { value: d.via.selva_alta ? 'si' : 'no', onChange: function (e) { setVia('selva_alta', e.target.value === 'si'); } },
            h('option', { value: 'no' }, 'No'), h('option', { value: 'si' }, 'Sí (TMC Ø 48" mínimo)')))),
        h('div', { className: 'rc-lluvia' + (ll.error ? ' falta' : '') }, h('div', null, h('span', null, 'Lluvia (pestaña LLUVIA)'), h('b', null, ll.error ? 'Pendiente' : 'Serie cargada'),
          h('small', null, ll.error || ll.texto + '. El período de retorno de cada obra sale del riesgo admisible y la vida útil (MTC, Tabla N.° 02).')),
          h(Btn, { onClick: function () { v3Go(props, 0); } }, 'Ir a la serie'))),
      h(DvTabla, { titulo: 'Cunetas', cols: DV_CUN, filas: d.cunetas, cambiar: cambiar('cunetas'),
        nota: 'Una fila por tramo de pendiente uniforme. Sección vacía: la mínima de la Tabla N.° 34 según la precipitación anual. Aportes por metro de cuneta: ancho que drena a la cuneta y su C. Las alcantarillas de alivio se ubican solas.',
        nuevo: function (k) { return { id: 'CU-' + ('0' + k).slice(-2), lado: 'izquierdo', revestimiento: 'concreto', tipo: '', w1: 3.6, c1: 0.86 }; } }),
      h(DvTabla, { titulo: 'Alcantarillas de paso de quebradas', cols: DV_ALC, filas: d.alcantarillas, cambiar: cambiar('alcantarillas'),
        nota: 'Cuenca: área, longitud del cauce y desnivel. «Recibe cunetas»: códigos separados por coma; recibe la descarga de cada una a menos de 50 m.',
        nuevo: function (k) { return { id: 'AC-' + ('0' + k).slice(-2), tipo: 'cruce', cobertura: 'bosques', suelo: 'semipermeable', tipo_conducto: 'TMC', pendiente_pct: 2, longitud_m: 8 }; } }),
      h(DvTabla, { titulo: 'Badenes', cols: DV_BAD, filas: d.badenes, cambiar: cambiar('badenes'),
        nuevo: function (k) { return { id: 'BA-' + ('0' + k).slice(-2), cobertura: 'pastos', suelo: 'semipermeable', b: 4, z: 10, profundidad: 0.6, pendiente_pct: 2.5 }; } }),
      h('div', { className: 'ws-actions ws-next' }, h(Btn, { onClick: function () { dvImportar(props); } }, 'Importar Excel'), h(Btn, { variant: 'primary', onClick: function () { dvCalcular(props); } }, 'Calcular'))),
    h(DvAviso));
}
