/* DrenIE 3.1.0 · Red de cunetas desde el plano.
   La página 15 lee el plano DXF del local (cerco, techos, curvas de nivel), propone la red de cunetas con sus descargas
   por gravedad y entrega planos, metrado, memorias y especificaciones. El cálculo lo hace el motor de la red, que DrenIE
   lleva instalado y llama por la orden nativa motor_red (con la misma licencia). El visor va en un marco de la página
   (visor-red.html) y se maneja desde la cinta RED DE CUNETAS. */
var RC_ICONS = {
  red_nuevo: '<rect x="3" y="5" width="23" height="19" rx="2" fill="#fff" stroke="#0B2545" stroke-width="1.6"/><path d="M7 19l5-6 4 3 6-7" stroke="#D61F9A" stroke-width="2"/><circle cx="24" cy="24" r="6" fill="#16A34A"/><path d="M24 21v6M21 24h6" stroke="#fff" stroke-width="1.8"/>',
  red_calc: '<rect x="3" y="4" width="22" height="22" rx="3" fill="#E0F2FE" stroke="#0B2545" stroke-width="1.6"/><path d="M7 9h14M7 9v12M7 15h9M16 15v6" stroke="#D61F9A" stroke-width="2"/><circle cx="23.5" cy="23.5" r="6.5" fill="#1EA7F2"/><path d="M21.5 20.5v6l5-3z" fill="#fff"/>',
  red_sol: '<path d="M16 3a9 9 0 0 0-5 16.5V23h10v-3.5A9 9 0 0 0 16 3z" fill="#FDE68A" stroke="#B45309" stroke-width="1.5"/><path d="M12 26h8M13 29h6" stroke="#0B2545" stroke-width="1.8"/><path d="M16 8v7M12.5 11.5h7" stroke="#B45309" stroke-width="1.6"/>',
  red_entreg: '<rect x="9" y="3" width="18" height="22" rx="2" fill="#fff" stroke="#0B2545" stroke-width="1.5"/><rect x="5" y="7" width="18" height="22" rx="2" fill="#E0F2FE" stroke="#0B2545" stroke-width="1.5"/><path d="M9 13h10M9 17h10M9 21h6" stroke="#0B6FC0" stroke-width="1.6"/><circle cx="23" cy="25" r="5" fill="#16A34A"/><path d="M20.8 25l1.6 1.6 3-3.2" stroke="#fff" stroke-width="1.6"/>',
  red_cuneta: '<path d="M3 8v13h26V8" fill="#E0F2FE" stroke="#0B2545" stroke-width="1.6"/><path d="M8 8v8h16V8" fill="#fff" stroke="#0B2545" stroke-width="1.6"/><path d="M8 13h16" stroke="#1EA7F2" stroke-width="2"/><path d="M3 26h26" stroke="#D61F9A" stroke-width="2" stroke-dasharray="4 2.5"/>',
  red_montante: '<rect x="3" y="4" width="25" height="6" fill="#E0F2FE" stroke="#0B2545" stroke-width="1.5"/><path d="M13 10v12a4 4 0 0 0 4 4h11" stroke="#0B6FC0" stroke-width="3.4"/><path d="M13 10v12a4 4 0 0 0 4 4h11" stroke="#7DD3FC" stroke-width="1.2"/><rect x="9.5" y="21" width="7" height="7" fill="#CBD5E1" stroke="#0B2545" stroke-width="1.2"/>',
  red_sumidero: '<rect x="5" y="4" width="22" height="20" rx="2" fill="#E0F2FE" stroke="#0B2545" stroke-width="1.6"/><path d="M11 8v12M16 8v12M21 8v12" stroke="#0B2545" stroke-width="2"/><path d="M6 28c2-1.6 4-1.6 6 0s4 1.6 6 0 4-1.6 6 0" stroke="#1EA7F2" stroke-width="1.7"/>',
  red_descarga: '<rect x="3" y="4" width="6" height="24" fill="#CBD5E1" stroke="#0B2545" stroke-width="1.4"/><path d="M9 15h13" stroke="#1EA7F2" stroke-width="3"/><path d="M19 10l6 5-6 5" stroke="#0B6FC0" stroke-width="2"/><path d="M13 26c2-1.5 4-1.5 6 0s4 1.5 6 0" stroke="#1EA7F2" stroke-width="1.6"/>',
  red_flecha: '<path d="M3 13L16 5l13 8" fill="#E0F2FE" stroke="#0B2545" stroke-width="1.6"/><path d="M16 12v14M11 21l5 5 5-5" stroke="#E08A12" stroke-width="2.3"/>',
  red_asignar: '<rect x="4" y="4" width="24" height="24" rx="2" fill="#DCFCE7" stroke="#0B2545" stroke-width="1.6"/><path d="M4 16L16 4M4 28L28 4M16 28L28 16" stroke="#16A34A" stroke-width="1.6"/>',
  red_capas: '<path d="M16 4l12 6-12 6-12-6z" fill="#E0F2FE" stroke="#0B2545" stroke-width="1.5"/><path d="M4 16l12 6 12-6" stroke="#1EA7F2" stroke-width="1.7"/><path d="M4 22l12 6 12-6" stroke="#0B6FC0" stroke-width="1.7"/>'
};
// [comando del visor, texto, grupo de la cinta, trazos 16 x 16] (mismos comandos que la línea de comando del visor)
var RC_CMDS = [
  ['linea', 'Línea', 'dib', 'M2 14L14 2'], ['pl', 'Polilínea', 'dib', 'M2 13L6 5l4 5 4-7'], ['rect', 'Rectángulo', 'dib', 'M2 4h12v8H2z'],
  ['circulo', 'Círculo', 'dib', 'M8 2a6 6 0 1 0 .01 0M8 8h.01'], ['texto', 'Texto', 'dib', 'M3 3h10M8 3v10M6 13h4'], ['cotaal', 'Cota', 'dib', 'M3 13L13 3M1 11l4 4M11 1l4 4M6 6l1.5 1.5'],
  ['mover', 'Desplazar', 'mod', 'M8 1v14M1 8h14M6 3l2-2 2 2M6 13l2 2 2-2M3 6L1 8l2 2M13 6l2 2-2 2'], ['copiar', 'Copiar', 'mod', 'M2 6h8v8H2zM6 2h8v8h-4'], ['rotar', 'Girar', 'mod', 'M13 8a5 5 0 1 1-1.5-3.5M12 1v4H8'],
  ['escala', 'Escala', 'mod', 'M2 14V9M2 14h5M2 14L14 2M14 2H9M14 2v5'], ['simetria', 'Simetría', 'mod', 'M8 1v14M6 4L2 8l4 4zM10 4l4 4-4 4z'], ['desfase', 'Desfase', 'mod', 'M2 10L7 4h7M2 14l5-6h7'],
  ['recortar', 'Recortar', 'mod', 'M4 2.5a1.8 1.8 0 1 0 .01 0M4 13.5a1.8 1.8 0 1 0 .01 0M5.5 5L14 12M5.5 11L14 4'], ['alargar', 'Alargar', 'mod', 'M14 2v12M2 8h9M8 5l3 3-3 3'], ['empalme', 'Empalme', 'mod', 'M3 14V7a4 4 0 0 1 4-4h7'],
  ['chaflan', 'Chaflán', 'mod', 'M3 14V8l5-5h6'], ['estirar', 'Estirar', 'mod', 'M2 14l5-5h7M7 9l4-6M10 2h2v2'], ['borrar', 'Borrar', 'mod', 'M3 4h10M6 4V2h4v2M4 4l1 10h6l1-10'],
  ['dist', 'Distancia', 'med', 'M1 11L11 1l4 4L5 15zM4 8l1.5 1.5M6 6l1.5 1.5M8 4l1.5 1.5'], ['area', 'Área', 'med', 'M3 13L2 5l6-3 6 4-2 7z'], ['id', 'Coordenada', 'med', 'M8 1v14M1 8h14M5.5 5.5h5v5h-5z'],
  ['zoom', 'Zoom ventana', 'vis', 'M7 2a5 5 0 1 0 .01 0M11 11l4 4M5 7h4M7 5v4'], ['extension', 'Zoom extensión', 'vis', 'M2 6V2h4M10 2h4v4M14 10v4h-4M6 14H2v-4'], ['pan', 'Encuadre', 'vis', 'M8 1v14M1 8h14M6 3l2-2 2 2M6 13l2 2 2-2M3 6L1 8l2 2M13 6l2 2-2 2'],
  ['deshacer', 'Deshacer', 'vis', 'M5 3L2 6l3 3M2 6h7a4 4 0 0 1 0 8H6'], ['rehacer', 'Rehacer', 'vis', 'M11 3l3 3-3 3M14 6H7a4 4 0 0 0 0 8h3']
];
Object.keys(RC_ICONS).forEach(function (k) { V3_RIB_ICONS[k] = RC_ICONS[k]; });
RC_CMDS.forEach(function (c) { V3_RIB_ICONS['rc_' + c[0]] = '<path d="' + c[3] + '" transform="scale(2)" stroke="#0B2545" stroke-width="1.15"/>'; });
// Orden de trabajo: la red de cunetas va después de la lluvia de diseño (la usa) y antes de techos, cunetas y montantes.
V3_RIB_TABS.splice(V3_RIB_TABS.findIndex(function (t) { return t[0] === 'lluvia'; }) + 1, 0, ['red', 'RED DE CUNETAS']);
V3_STEP_TAB[15] = 'red';
V3_NAV.splice(V3_NAV.findIndex(function (n) { return n[0] === 1; }) + 1, 0, [15, 'Red de cunetas', 'R', 'profile']);

var RC = { proyecto: null, nombre: '', pendientes: 0, observaciones: 0, asistente: null, aviso: null, marco: null, visorListo: false, estado: null, setState: null };
// Lluvia de diseño de la pestaña LLUVIA: la misma intensidad (curva IDF y tiempo de concentración de diseño) para todo el proyecto.
function rcLluvia(st) {
  if (!st) return { error: 'Abra la pestaña LLUVIA y complete la curva IDF del proyecto.' };
  var d = v3DesignDuration(st), I = v3DesignIntensity(st);
  if (!d.valid) return { error: 'Revise el tiempo de concentración de diseño en la pestaña LLUVIA: ' + (d.errors || []).join(' ') };
  if (!(I > 0)) return { error: 'La curva IDF de la pestaña LLUVIA no está completa: ' + (v3IdfErrors(st).join(' ') || 'agregue al menos una fila.') };
  var rows = validIdfRows(st.idf || []).map(function (r) { return [r.duration, r.intensity]; }).sort(function (a, b) { return a[0] - b[0]; });
  var s = st.statistics || {}, est = s.station && (s.station.name || s.station.nombre) || s.sourceName || '';
  var origen = s.connected ? 'análisis estadístico de DrenIE' + (est ? ' (' + est + ')' : '') + (s.returnPeriod ? ', T = ' + s.returnPeriod + ' años' : '') : 'curva IDF ingresada en DrenIE';
  var ejemplo = v3IdfSample(st);
  return { I_mmh: Math.round(I * 100) / 100, tc_min: d.duration, metodo_tc: d.method, idf: rows, ejemplo: ejemplo || undefined,
    fuente: 'Pestaña LLUVIA de DrenIE: ' + origen + '; I para tc = ' + fmt(d.duration, 0) + ' min (' + d.method + ')' + (ejemplo ? '. CURVA DE EJEMPLO: reemplazar con la de la estación del proyecto' : '') };
}
function rcVincular(ruta, nombre) {
  if (RC.setState) RC.setState(function (prev) { return prev.redCunetas && prev.redCunetas.proyecto === ruta ? prev : Object.assign({}, prev, { redCunetas: { proyecto: ruta, nombre: nombre || '' } }); });
}
var RC_PLANTEAMIENTO = [['completar', 'Completar mis líneas de cuneta (recomendado)'], ['automatico', 'Proponer toda la red (no usar las líneas del plano)'], ['no', 'Solo mis líneas de cuneta']];
function rcAvisar() { window.dispatchEvent(new Event('drenie-red')); window.dispatchEvent(new Event('drenie-ui')); }
function rcRecientes() { try { return JSON.parse(localStorage.getItem('drenie-red-recientes') || '[]').filter(function (r) { return r && r.ruta; }); } catch (e) { return []; } }
function rcRecordar(ruta, nombre) { try { localStorage.setItem('drenie-red-recientes', JSON.stringify([{ ruta: ruta, nombre: nombre, fecha: new Date().toLocaleDateString('es-PE') }].concat(rcRecientes().filter(function (r) { return r.ruta !== ruta; })).slice(0, 8))); } catch (e) {} }
function rcEsLicencia(m) { return /licencia|módulo|demo|activ/i.test(m || ''); }
function rcError(titulo, e) {
  var m = String(e && e.message || e || '');
  if (rcEsLicencia(m)) licenseDialog(m); else v3Notice(m, { title: titulo });
}
// Orden nativa: el motor responde un JSON; los errores de datos llegan en «error» en español.
function rcMotor(accion, args, entrada) {
  if (!window.__TAURI__) return Promise.reject(Error('La red de cunetas funciona en la aplicación de Windows.'));
  return nativeCall('motor_red', { accion: accion, args: args || [], entrada: entrada == null ? null : JSON.stringify(entrada) }).then(function (txt) {
    var d; try { d = JSON.parse(txt); } catch (e) { throw Error('El motor de la red de cunetas no respondió correctamente.'); }
    if (d && d.error) throw Error(d.error);
    return d;
  });
}
function rcElegir(tipo) { return nativeCall('motor_elegir', { tipo: tipo }); }
function rcOcupado(texto, fn) {
  RC.aviso = { texto: texto, desde: Date.now() }; rcAvisar();
  return Promise.resolve().then(fn).finally(function () { RC.aviso = null; rcAvisar(); });
}
function rcAbrirProyecto(ruta, nombre) { RC.proyecto = ruta; RC.nombre = nombre || ''; RC.asistente = null; RC.pendientes = 0; RC.observaciones = 0; RC.visorListo = false; rcRecordar(ruta, nombre || ruta); RC.vinculoVisto = ruta; rcVincular(ruta, nombre); rcAvisar(); }
function rcAbrirDialogo() { rcElegir('proyecto').then(function (r) { if (r) rcAbrirProyecto(r, ''); }).catch(function (e) { rcError('Abrir proyecto de red', e); }); }
function rcNuevo() {
  RC.asistente = { dxf: '', capas: [], sel: {}, landxml: '', nombre: '', codigo: '', entidad: '', ubicacion: '', carpeta: '', npt: '', area_verde: '', I_mmh: '', planteamiento: 'completar', por_defecto: 'verde' };
  rcAvisar();
}
function rcOrden(orden, args) { if (RC.marco && RC.marco.contentWindow) RC.marco.contentWindow.postMessage({ drenie: 'red', tipo: 'orden', orden: orden, args: args || {} }, location.origin === 'null' ? '*' : location.origin); }
function rcNecesita(fn) { return function () { if (!RC.proyecto) { v3Notice('Primero cree o abra un proyecto de red de cunetas.', { title: 'Red de cunetas' }); return; } fn(); }; }

// Llamadas del visor (marco) atendidas por la página: cada una pasa por la orden nativa con la licencia.
var RC_API = {
  escena: function () { return rcMotor('vista', [RC.proyecto]).then(function (d) { if (d.nombre && d.nombre !== RC.nombre) { RC.nombre = d.nombre; rcRecordar(RC.proyecto, d.nombre); rcAvisar(); } return d; }); },
  leer: function (a) { return rcOcupado(a.texto || 'Leyendo el plano', function () { return rcMotor('leer', [RC.proyecto]); }); },
  ediciones: function (a) { return rcMotor('ediciones', [RC.proyecto], a.ediciones || {}); },
  calcular: function (a) {
    var ll = rcLluvia(RC.estado);
    if (ll.error) return Promise.reject(Error(ll.error));
    return rcOcupado(a.texto || 'Calculando el diseño, los planos y los documentos', function () {
      var t0 = Date.now();
      return rcMotor('datos', [RC.proyecto], { lluvia: ll })
        .then(function () { return a.ediciones ? rcMotor('ediciones', [RC.proyecto], a.ediciones) : null; }).then(function () { return rcMotor('disenar', [RC.proyecto]); })
        .then(function (r) { r.segundos = r.segundos || (Date.now() - t0) / 1000; return r; });
    });
  },
  entregables: function () { return rcMotor('entregables', [RC.proyecto]); },
  abrir_archivo: function (a) { return rcMotor('abrir', a.nombre ? [RC.proyecto, a.nombre] : [RC.proyecto]); }
};
window.addEventListener('message', function (e) {
  if (!RC.marco || e.source !== RC.marco.contentWindow || !e.data || e.data.drenie !== 'red') return;
  if (location.origin !== 'null' && e.origin !== location.origin) return;
  var d = e.data, destino = location.origin === 'null' ? '*' : location.origin;
  if (d.tipo === 'estado') { RC.pendientes = d.pendientes || 0; RC.observaciones = d.observaciones || 0; RC.visorListo = true; rcAvisar(); return; }
  if (d.tipo !== 'api') return;
  var f = RC_API[d.nombre];
  Promise.resolve().then(function () { if (!f) throw Error('Llamada desconocida.'); if (!RC.proyecto) throw Error('No hay un proyecto de red abierto.'); return f(d.args || {}); })
    .then(function (datos) { e.source.postMessage({ drenie: 'red', tipo: 'api-r', id: d.id, datos: datos }, destino); },
          function (er) { var m = String(er && er.message || er); if (rcEsLicencia(m)) licenseDialog(m); e.source.postMessage({ drenie: 'red', tipo: 'api-r', id: d.id, error: m }, destino); });
});

// Cinta RED DE CUNETAS
function v3RedRibbon(props) {
  function go() { if (props.home || props.state.step !== 15) v3Go(props, 15); }
  function cmd(n) { return rcNecesita(function () { go(); rcOrden('comando', { nombre: n }); }); }
  function big(n, t, k) { return rbBig(k, t, cmd(n), { k: n, title: t.replace('\n', ' ') }); }
  function col(g, desde, hasta) { return rbCol.apply(null, RC_CMDS.filter(function (c) { return c[2] === g; }).slice(desde, hasta).map(function (c) { return rbSm('rc_' + c[0], c[1], cmd(c[0]), { k: c[0] }); })); }
  var on = !props.home && props.state.step === 15;
  RC.estado = props.state; RC.setState = props.setState;
  return [
    rbGrp('Proyecto de red', [rbBig('red_nuevo', 'Nuevo desde\nplano DXF', function () { go(); rcNuevo(); }, { on: on && !!RC.asistente }), rbBig('abrir', 'Abrir\nproyecto', function () { go(); rcAbrirDialogo(); }, { k: 'rab' })]),
    rbGrp('Cálculo', [rbBig('red_calc', 'Calcular\ntodo', rcNecesita(function () { go(); rcOrden('calcular'); })),
      rbBig('red_sol', 'Soluciones' + (RC.pendientes ? '\n(' + RC.pendientes + ' por decidir)' : '\npropuestas'), rcNecesita(function () { go(); rcOrden('soluciones'); }), { k: 'sol' }),
      rbBig('red_entreg', 'Entregables', rcNecesita(function () { go(); rcOrden('entregables'); }))]),
    rbGrp('Drenaje', [big('cuneta', 'Eje de\ncuneta', 'red_cuneta'), big('montante', 'Montante', 'red_montante'), big('sumidero', 'Sumidero', 'red_sumidero'),
      big('descarga', 'Descarga', 'red_descarga'), big('flecha', 'Caída de\ntecho', 'red_flecha'), big('asignar', 'Asignar\nsuperficie', 'red_asignar')]),
    rbGrp('Dibujo', [col('dib', 0, 3), col('dib', 3, 6)]),
    rbGrp('Modificar', [col('mod', 0, 3), col('mod', 3, 6), col('mod', 6, 9), col('mod', 9, 12)]),
    rbGrp('Medir y vista', [col('med', 0, 3), col('vis', 0, 3), rbCol.apply(null, RC_CMDS.filter(function (c) { return c[2] === 'vis'; }).slice(3).map(function (c) { return rbSm('rc_' + c[0], c[1], cmd(c[0]), { k: c[0] }); })
      .concat([rbSm('red_capas', 'Paneles', rcNecesita(function () { go(); rcOrden('paneles'); }), { k: 'pan' })]))])
  ];
}

function rcCampo(etiqueta, valor, cambiar, o) { return wsField(etiqueta, valor, cambiar, o); }
function rcSelect(etiqueta, valor, opciones, cambiar) {
  return h('label', { className: 'ws-field' }, h('span', null, etiqueta), h('select', { value: valor || '', onChange: function (e) { cambiar(e.target.value); } },
    opciones.map(function (o) { return h('option', { key: o[0], value: o[0] }, o[1]); })));
}
function RcAviso() {
  var t = useState(0);
  useEffect(function () { if (!RC.aviso) return; var k = setInterval(function () { t[1](function (n) { return n + 1; }); }, 1000); return function () { clearInterval(k); }; }, [RC.aviso && RC.aviso.desde]);
  if (!RC.aviso) return null;
  return h('div', { className: 'v3-dlg-overlay rc-velo', role: 'status', 'aria-live': 'polite' }, h('div', { className: 'v3-dlg rc-velo-caja' },
    h('div', { className: 'v3-dlg-main' }, h('div', { className: 'v3-dlg-body' }, h('h3', null, RC.aviso.texto + '…'),
      h('p', null, 'Tiempo: ' + Math.round((Date.now() - RC.aviso.desde) / 1000) + ' s. El plano, la red, los planos y los documentos se generan en la carpeta del proyecto.')),
      h('div', { className: 'rc-barra' }, h('i')))));
}
function RcAsistente(props) {
  var a = RC.asistente, st = props.state;
  RC.estado = st; RC.setState = props.setState;
  function set(k, v) { a[k] = v; rcAvisar(); }
  function setCapa(k, v) { a.sel[k] = v; rcAvisar(); }
  function plano() {
    rcElegir('dxf').then(function (r) {
      if (!r) return;
      return rcOcupado('Leyendo las capas del plano', function () { return rcMotor('capas', [r]); }).then(function (d) {
        a.dxf = d.dxf; a.capas = d.capas || []; a.sel = Object.assign({}, d.sugeridas || {});
        if (!a.nombre) a.nombre = (st.project && st.project.name) || '';
        if (!a.ubicacion) a.ubicacion = (st.project && st.project.location) || '';
        if (!a.entidad) a.entidad = (st.project && st.project.entity) || '';
        rcAvisar();
      });
    }).catch(function (e) { rcError('Plano DXF', e); });
  }
  function carpeta() { rcElegir('carpeta').then(function (r) { if (r) set('carpeta', r); }).catch(function (e) { rcError('Carpeta del proyecto', e); }); }
  function landxml() { rcElegir('landxml').then(function (r) { if (r) set('landxml', r); }).catch(function (e) { rcError('Terreno LandXML', e); }); }
  function crear() {
    if (ll.error) { v3Notice(ll.error, { title: 'Lluvia de diseño' }); return; }
    var d = { nombre: a.nombre, codigo: a.codigo, entidad: a.entidad, ubicacion: a.ubicacion, dxf: a.dxf, carpeta: a.carpeta || null, landxml: a.landxml || null,
      capas: a.sel, npt: a.npt, area_verde: a.area_verde, lluvia: ll, planteamiento: a.planteamiento, por_defecto: a.por_defecto };
    rcOcupado('Creando el proyecto', function () { return rcMotor('crear', [], d); }).then(function (r) { rcAbrirProyecto(r.proyecto, a.nombre); })
      .catch(function (e) { rcError('Proyecto de red', e); });
  }
  var opc = [['', '(ninguna)']].concat(a.capas.map(function (c) { return [c.capa, c.capa + ' · ' + c.entidades + ' obj.' + (c.cerradas ? ' · ' + c.cerradas + ' cerradas' : '') + (c.con_cota ? ' · ' + c.con_cota + ' con cota' : '')]; }));
  var ll = rcLluvia(st);
  return h(React.Fragment, null,
    h('section', { className: 'card' }, h('h2', null, '1 · Plano del local'),
      h('p', { className: 'muted small' }, 'Plano general en DXF a escala real (1 unidad = 1 m), con el cerco perimétrico, las proyecciones de techo y las curvas de nivel con su cota.'),
      h('div', { className: 'ws-actions' }, h(Btn, { variant: 'primary', onClick: plano }, a.dxf ? 'Cambiar plano DXF' : 'Elegir plano DXF'), a.dxf ? h('span', { className: 'rc-ruta', title: a.dxf }, a.dxf) : null),
      a.capas.length ? h('div', { className: 'ws-form-grid' },
        rcSelect('Cerco perimétrico (límite de intervención)', a.sel.cerco, opc, function (v) { setCapa('cerco', v); }),
        rcSelect('Proyecciones de techo', a.sel.techos, opc, function (v) { setCapa('techos', v); }),
        rcSelect('Curvas de nivel', a.sel.curvas, opc, function (v) { setCapa('curvas', v); }),
        rcSelect('Veredas y pisos', a.sel.veredas, opc, function (v) { setCapa('veredas', v); }),
        rcSelect('Muros', a.sel.muros, opc, function (v) { setCapa('muros', v); }),
        rcSelect('Líneas de cuneta del proyectista', a.sel.ejes, opc, function (v) { setCapa('ejes', v); })) : null,
      a.capas.length ? h('div', { className: 'ws-actions' }, h(Btn, { onClick: landxml }, a.landxml ? 'Cambiar terreno LandXML' : 'Terreno LandXML (opcional)'), a.landxml ? h('span', { className: 'rc-ruta', title: a.landxml }, a.landxml) : h('span', { className: 'muted small' }, 'Si no hay curvas de nivel en el plano, use la superficie del levantamiento topográfico.')) : null),
    a.capas.length ? h('section', { className: 'card' }, h('h2', null, '2 · Datos del proyecto'),
      h('div', { className: 'ws-form-grid' },
        rcCampo('Nombre del proyecto', a.nombre, function (v) { set('nombre', v); }), rcCampo('Código (CUI)', a.codigo, function (v) { set('codigo', v); }),
        rcCampo('Entidad', a.entidad, function (v) { set('entidad', v); }), rcCampo('Ubicación', a.ubicacion, function (v) { set('ubicacion', v); })),
      h('div', { className: 'ws-actions' }, h(Btn, { onClick: carpeta }, 'Carpeta del proyecto'), h('span', { className: 'rc-ruta' }, a.carpeta || 'Documentos\\DrenIE\\' + (a.nombre || 'Proyecto')))) : null,
    a.capas.length ? h('section', { className: 'card' }, h('h2', null, '3 · Niveles, lluvia y planteamiento'),
      h('div', { className: 'ws-form-grid' },
        rcCampo('NPT y borde de cuneta (m)', a.npt, function (v) { set('npt', v); }, { inputMode: 'decimal', placeholder: 'ej. 184.65' }),
        rcCampo('Nivel de área verde (m)', a.area_verde, function (v) { set('area_verde', v); }, { inputMode: 'decimal', placeholder: 'NPT − 0.05' }),
        rcSelect('Planteamiento de la red', a.planteamiento, RC_PLANTEAMIENTO, function (v) { set('planteamiento', v); }),
        rcSelect('Áreas que el plano no define', a.por_defecto, [['verde', 'Área verde'], ['pavimento', 'Piso de concreto']], function (v) { set('por_defecto', v); })),
      h('div', { className: 'rc-lluvia' + (ll.error ? ' falta' : ll.ejemplo ? ' ejemplo' : '') },
        h('div', null, h('span', null, 'Lluvia de diseño'), h('b', null, ll.error ? 'Pendiente' : fmt(ll.I_mmh, 2) + ' mm/h'),
          h('small', null, ll.error || ll.fuente)),
        h(Btn, { onClick: function () { v3Go(props, 1); } }, 'Ir a LLUVIA')),
      h('p', { className: 'ws-note' }, 'La cota de fondo de cada cuneta, sus descargas por gravedad y la llegada de cada montante sobre el nivel del agua se calculan y se verifican. Lo que el programa no pueda resolver solo aparece en la ventana de soluciones para que usted decida.'),
      h('div', { className: 'ws-actions ws-next' }, h(Btn, { onClick: function () { RC.asistente = null; rcAvisar(); } }, 'Cancelar'), h(Btn, { variant: 'primary', onClick: crear }, 'Crear y abrir el proyecto'))) : null);
}
function RcInicio() {
  var rec = rcRecientes();
  return h(React.Fragment, null,
    h('section', { className: 'card' }, h('h2', null, 'Empezar'), h('div', { className: 'ws-file-grid' },
      h('button', { className: 'ws-file-action', onClick: rcNuevo }, h(V3RIcon, { name: 'red_nuevo' }), 'Nuevo proyecto desde el plano DXF'),
      h('button', { className: 'ws-file-action', onClick: rcAbrirDialogo }, h(V3RIcon, { name: 'abrir' }), 'Abrir proyecto de red (proyecto.json)'))),
    h('section', { className: 'card' }, h('h2', null, 'Proyectos de red recientes'), rec.length ? h('div', { className: 'rc-recientes' }, rec.map(function (r) {
      return h('button', { key: r.ruta, className: 'rc-reciente', onClick: function () { rcAbrirProyecto(r.ruta, r.nombre); }, title: r.ruta }, h('b', null, r.nombre || 'Proyecto'), h('small', null, r.ruta), h('em', null, r.fecha || ''));
    })) : h('p', { className: 'muted' }, 'Todavía no hay proyectos de red.')),
    h('section', { className: 'card' }, h('h2', null, 'Qué entrega'), h('p', { className: 'ws-note' },
      'Planta de la red con cotas de fondo, perfiles longitudinales, secciones, descargas, detalles, metrado (concreto, encofrado, acero, curado, rejillas, tapas, juntas, canaletas, falsas columnas, dados y tubería enterrada de cada montante), memoria descriptiva, memoria de cálculo, especificaciones técnicas, carátulas e índice de planos, en Word, Excel, DXF y PNG.')));
}
function RcPage(props) {
  var tick = useState(0), ref = React.useRef(null);
  useEffect(function () { function f() { tick[1](function (n) { return n + 1; }); } window.addEventListener('drenie-red', f); return function () { window.removeEventListener('drenie-red', f); }; }, []);
  useEffect(function () { RC.marco = ref.current; return function () { if (RC.marco === ref.current) RC.marco = null; }; });
  RC.estado = props.state; RC.setState = props.setState;
  // El proyecto de DrenIE recuerda su red de cunetas: al abrirlo, la página vuelve a esa red.
  var vinc = props.state.redCunetas;
  if (!RC.asistente && vinc && vinc.proyecto && RC.vinculoVisto !== vinc.proyecto) { RC.vinculoVisto = vinc.proyecto; RC.proyecto = vinc.proyecto; RC.nombre = vinc.nombre || ''; RC.pendientes = 0; RC.observaciones = 0; }
  var abierto = RC.proyecto && !RC.asistente;
  return h('div', { className: 'ws-page rc-page' + (abierto ? ' rc-con-visor' : ''), 'data-workspace': 'red' },
    abierto ? h('div', { className: 'rc-cab' }, h('div', null, h('h1', null, RC.nombre || 'Red de cunetas'), h('span', { className: 'rc-ruta', title: RC.proyecto }, RC.proyecto)),
        RC.observaciones ? h('span', { className: 'rc-chip' + (RC.pendientes ? ' pend' : ' ok') }, RC.pendientes ? RC.pendientes + ' observación(es) por decidir' : 'Observaciones resueltas') : null,
        h(Btn, { onClick: function () { RC.proyecto = null; RC.nombre = ''; rcAvisar(); } }, 'Cerrar proyecto'))
      : wsHead('Red de cunetas desde el plano', 'Lee el plano del local, propone la red de cunetas con sus descargas por gravedad y entrega planos, metrado, memorias y especificaciones.'),
    RC.asistente ? h(RcAsistente, props) : abierto ? h('section', { className: 'card rc-visor' }, h('iframe', { ref: ref, key: RC.proyecto, src: 'visor-red.html?drenie=1', title: 'Visor de la red de cunetas' })) : h(RcInicio, props),
    h(RcAviso));
}
