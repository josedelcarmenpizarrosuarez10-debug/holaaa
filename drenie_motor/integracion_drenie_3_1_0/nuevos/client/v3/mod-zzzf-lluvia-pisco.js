/* DrenIE 3.1.0 · Lluvia PISCO-SENAMHI en la pestaña LLUVIA.
   Trae la precipitación máxima en 24 h de cada mes (1981-2025) del punto del proyecto, desde PISCOp v3.0 del SENAMHI (base que va
   con el motor, sin internet), multiplicada por el factor estación / PISCO (en San Martín, interpolado entre 8 estaciones del SENAMHI).
   La serie entra en la misma tabla que «Importar Excel»: DrenIE calcula 1.13, distribuciones, Bell e IDF como siempre. */
var wsPiscoBase = StatsStep;
StatsStep = function (props) { return h(React.Fragment, null, h(WsPisco, props), h(wsPiscoBase, props)); };

function WsPisco(props) {
  var st = props.state, s = st.statistics || DrenStats.defaults(), g = wsGeo(st), u0 = wsuUbigeo(g);
  var abierto = useState(false), modo = useState('distrito'), dep = useState(u0.dep || ''), prov = useState(u0.prov || ''), dist = useState(u0.dist || '');
  var lat = useState(''), lon = useState(''), factor = useState(''), res = useState(null), msg = useState(''), ocupado = useState(false), confirmar = useState(false);
  if (!abierto[0]) return h('section', { className: 'card ws-pisco' }, h('div', { className: 'section-heading' },
    h('h2', null, 'Lluvia PISCO-SENAMHI (referencial)'),
    h(Btn, { onClick: function () { abierto[1](true); } }, 'Traer la serie de cualquier lugar del Perú')),
    h('p', { className: 'muted small' }, 'Precipitación máxima en 24 h de cada mes, 1981-2025, sin internet. Úsela para anteproyectos o donde no haya estación; para el expediente cargue la serie certificada de la estación SENAMHI más cercana.'));
  var sel = function (et, valor, opciones, cambiar, falta) {
    return h('label', { className: 'ws-field', style: { flex: '1 1 220px', minWidth: 0 } }, h('span', null, et), h('select', { 'aria-label': et + ' de la lluvia', value: valor, disabled: !!falta, style: { width: '100%' },
      onChange: function (e) { cambiar(e.target.value); } }, [h('option', { key: '', value: '' }, falta || '— Elija —')].concat(opciones.map(function (x) { return h('option', { key: x.u, value: x.u }, x.n); }))));
  };
  function pedir() {
    var e = { factor: factor[0] === '' ? null : Number(factor[0]) };
    if (modo[0] === 'distrito') { if (!dist[0]) { msg[1]('Elija el distrito.'); return; } e.ubigeo = dist[0]; }
    else { var la = Number(lat[0]), lo = Number(lon[0]); if (!isFinite(la) || !isFinite(lo) || lat[0] === '' || lon[0] === '') { msg[1]('Escriba la latitud y la longitud en grados decimales (por ejemplo −6.5116 y −76.3199).'); return; } e.lat = la; e.lon = lo; }
    ocupado[1](true); msg[1](''); confirmar[1](false);
    rcMotor('pisco', [], e).then(function (d) { res[1](d); if (factor[0] === '') factor[1](String(d.factor)); },
      function (er) { res[1](null); msg[1](String(er && er.message || er)); }).finally(function () { ocupado[1](false); });
  }
  function cargar() {
    var d = res[0]; if (!d) return;
    if (s.rows && s.rows.length && !confirmar[0]) { confirmar[1](true); return; }
    var filas = d.anios.map(function (an, k) { return { id: 'pisco-' + an, year: an, months: d.filas[k].map(function (v) { return v == null ? '' : v; }), included: true }; });
    var demo = !canModule('import');
    if (demo) filas = filas.slice(-30);
    var u = d.ubicacion || {};
    var estacion = { name: 'PISCOp v3.0 (SENAMHI) × ' + Number(d.factor).toFixed(2) + ' · celda ' + d.celda.lat.toFixed(2) + ', ' + d.celda.lon.toFixed(2),
      latitude: String(d.celda.lat), longitude: String(d.celda.lon), elevation: '', department: u.departamento || '', province: u.provincia || '', district: u.distrito || '' };
    props.setState(function (prev) {
      var next = Object.assign({}, prev.statistics || DrenStats.defaults(), { rows: filas, station: estacion, connected: true, aux: {},
        period: filas[0].year + '-' + filas[filas.length - 1].year, sourceName: 'PISCOp v3.0 (SENAMHI) × ' + Number(d.factor).toFixed(2) });
      return Object.assign({}, prev, { statistics: next });
    });
    confirmar[1](false);
    msg[1]('Serie cargada en la tabla (' + filas.length + ' años' + (demo ? ', demo: últimos 30' : '') + '). Las precipitaciones de diseño ya se calculan con la distribución seleccionada.');
  }
  var d = res[0];
  return h('section', { className: 'card ws-pisco' },
    h('div', { className: 'section-heading' }, h('h2', null, 'Lluvia PISCO-SENAMHI (referencial)'), h(Btn, { onClick: function () { abierto[1](false); } }, 'Cerrar')),
    h('div', { className: 'ws-actions' }, h('label', null, 'Lugar ', h('select', { 'aria-label': 'Lugar de la lluvia', value: modo[0], onChange: function (e) { modo[1](e.target.value); res[1](null); } },
      h('option', { value: 'distrito' }, 'Por distrito'), h('option', { value: 'coordenadas' }, 'Por coordenadas (grados decimales)')))),
    modo[0] === 'distrito' ? h('div', { className: 'ws-actions', style: { alignItems: 'flex-end' } },
      sel('Departamento', dep[0], wsuLista('region'), function (v) { dep[1](v); prov[1](''); dist[1](''); res[1](null); }),
      sel('Provincia', prov[0], dep[0] ? wsuLista('provincia', dep[0]) : [], function (v) { prov[1](v); dist[1](''); res[1](null); }, dep[0] ? '' : 'Primero el departamento'),
      sel('Distrito', dist[0], prov[0] ? wsuLista('distrito', prov[0]) : [], function (v) { dist[1](v); res[1](null); }, prov[0] ? '' : 'Primero la provincia'))
    : h('div', { className: 'ws-actions', style: { alignItems: 'flex-end' } },
      wsField('Latitud (°)', lat[0], function (v) { lat[1](v); res[1](null); }, { placeholder: '−6.5116', inputMode: 'decimal' }),
      wsField('Longitud (°)', lon[0], function (v) { lon[1](v); res[1](null); }, { placeholder: '−76.3199', inputMode: 'decimal' })),
    h('div', { className: 'ws-actions', style: { alignItems: 'flex-end' } },
      wsField('Factor estación / PISCO', factor[0], function (v) { factor[1](v); res[1](null); }, { placeholder: 'automático (estaciones SENAMHI cercanas)', inputMode: 'decimal' }),
      h(Btn, { variant: 'primary', disabled: ocupado[0], onClick: pedir }, ocupado[0] ? 'Buscando…' : 'Traer serie')),
    d ? h('div', { className: 'ws-pisco-res' },
      h('p', null, h('strong', null, (d.ubicacion.distrito ? d.ubicacion.distrito + ', ' + d.ubicacion.provincia + ', ' + d.ubicacion.departamento : 'Punto ' + d.punto.lat + ', ' + d.punto.lon)),
        ' · celda PISCO ' + d.celda.lat.toFixed(2) + ', ' + d.celda.lon.toFixed(2) + ' · ' + d.periodo + ' · factor ' + Number(d.factor).toFixed(2)),
      h('p', null, 'Máxima anual en 24 h (corregida): promedio ' + d.resumen.max_anual_media_mm + ' mm, mayor ' + d.resumen.max_anual_mm + ' mm en ' + d.resumen.anios + ' años.'),
      d.calibracion ? h('p', { className: 'muted small' }, d.calibracion + '.') : null,
      d.avisos.map(function (t, i) { return h('p', { key: i, className: 'ws-note' }, t); }),
      h('div', { className: 'ws-actions' }, h(Btn, { variant: 'primary', onClick: cargar },
        confirmar[0] ? 'Sí, reemplazar la tabla actual (' + s.rows.length + ' años)' : 'Cargar en la tabla de lluvias'))) : null,
    msg[0] ? h('p', { role: 'status', className: 'ws-note' }, msg[0]) : null,
    h('p', { className: 'muted small' }, 'Fuente: PISCOp v3.0, SENAMHI (precipitación diaria grillada, 0.1°). La lluvia grillada promedia ~10 × 10 km y subestima las máximas puntuales; por eso se corrige con el factor estación / PISCO.'));
}
