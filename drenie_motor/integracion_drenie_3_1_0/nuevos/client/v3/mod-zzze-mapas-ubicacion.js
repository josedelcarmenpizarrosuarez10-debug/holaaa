/* DrenIE 3.1.0 · Mapas de ubicación automáticos (página Datos del proyecto).
   Cada recuadro de mapa tiene su lista: País (siempre Perú) → Departamento → Provincia → Distrito. Al elegir, el programa dibuja
   el mapa con los límites del INEI que trae incorporados (WS_LIMITES_PERU, el mismo archivo del motor de la red; sin internet).
   La Localidad / centro poblado se carga a mano y, como toda imagen cargada, se ajusta al mismo tamaño de los demás mapas.
   Un mapa propio (cargado por el usuario) nunca se reemplaza solo: el botón «Usar el mapa automático» lo cambia. */
var WSU_W = 960, WSU_H = 1040;                       // misma proporción de la figura de la memoria (600 x 650)
var WSU_PASTEL = [ '#A8C5E8', '#F6D186', '#B5DEA4', '#F2B5C9', '#C9B8E8', '#9ED9D4', '#F8C59B' ];
var WSU_RES = '#E4572E', WSU_REC = '#D90429', WSU_TXT = '#1B2A3A', WSU_AZUL = '#0B2545';
var WSU_FUENTE = 'Límites: INEI (límites censales)';
var WSU_PAISES = [ [ 'ECUADOR', -78.6, -1.8 ], [ 'COLOMBIA', -72.5, -1.0 ], [ 'BRASIL', -68.6, -8.6 ], [ 'BOLIVIA', -66.9, -15.6 ], [ 'CHILE', -69.6, -19.3 ] ];

function wsuDatos() { return typeof WS_LIMITES_PERU === 'object' && WS_LIMITES_PERU ? WS_LIMITES_PERU : null; }
function wsuGeom(x) { if (!x._g) x._g = typeof x.g === 'string' ? JSON.parse(x.g) : (x.g || []); return x._g; }
function wsuNorm(t) { return String(t || '').normalize('NFD').replace(/[̀-ͯ]/g, '').toUpperCase().replace(/[^A-Z0-9]+/g, ' ').trim(); }
function wsuLista(nivel, padre) {
  var L = wsuDatos(); if (!L) return [];
  var k = { region: 'departamentos', provincia: 'provincias', distrito: 'distritos' }[nivel];
  return (L[k] || []).filter(function (x) { return x.g && (!padre || x.u.indexOf(padre) === 0); })
    .sort(function (a, b) { return a.n.localeCompare(b.n, 'es'); });
}
function wsuPorU(u) {
  var L = wsuDatos(); if (!L || !u) return null;
  var k = u.length === 2 ? 'departamentos' : u.length === 4 ? 'provincias' : 'distritos';
  return (L[k] || []).find(function (x) { return x.u === u; }) || null;
}
// Ubigeos elegidos (o reconocidos por el nombre escrito en «Ubicación del proyecto»).
function wsuUbigeo(g) {
  var u = Object.assign({}, g.ubigeo || {});
  function porNombre(nivel, nombre, padre) {
    var n = wsuNorm(nombre); if (!n) return '';
    var x = wsuLista(nivel, padre).find(function (y) { return wsuNorm(y.n) === n; });
    return x ? x.u : '';
  }
  // lo escrito a mano en «Ubicación del proyecto» manda sobre lo elegido antes en la lista
  [ [ 'dep', 'region' ], [ 'prov', 'province' ], [ 'dist', 'district' ] ].forEach(function (k) {
    var x = wsuPorU(u[k[0]]); if (x && g[k[1]] != null && wsuNorm(g[k[1]]) !== wsuNorm(x.n)) u[k[0]] = '';
  });
  if (!u.dep) u.dep = porNombre('region', g.region);
  if (!u.prov && u.dep) u.prov = porNombre('provincia', g.province, u.dep);
  if (!u.dist && u.prov) u.dist = porNombre('distrito', g.district, u.prov);
  if (u.prov && u.prov.indexOf(u.dep) !== 0) u.prov = '';
  if (u.dist && u.dist.indexOf(u.prov || '@') !== 0) u.dist = '';
  return u;
}

// ------------------------------------------------------------------ geometría
function wsuCaja(polys) {
  var c = [ Infinity, Infinity, -Infinity, -Infinity ];
  polys.forEach(function (p) { p[0].forEach(function (q) { c[0] = Math.min(c[0], q[0]); c[1] = Math.min(c[1], q[1]); c[2] = Math.max(c[2], q[0]); c[3] = Math.max(c[3], q[1]); }); });
  return c;
}
function wsuAreaAnillo(r) { var a = 0; for (var i = 0, j = r.length - 1; i < r.length; j = i++) a += (r[j][0] + r[i][0]) * (r[j][1] - r[i][1]); return Math.abs(a / 2); }
function wsuArea(polys) { return polys.reduce(function (s, p) { return s + wsuAreaAnillo(p[0]); }, 0); }
// Punto para el nombre: en el polígono mayor, el centro del tramo interior más ancho a la altura de su centro.
function wsuPuntoNombre(polys) {
  var p = polys.slice().sort(function (a, b) { return wsuAreaAnillo(b[0]) - wsuAreaAnillo(a[0]); })[0], best = null;
  var cj = wsuCaja([ p ]);
  [ 0.5, 0.4, 0.6, 0.3, 0.7 ].forEach(function (f) {
    var y = cj[1] + (cj[3] - cj[1]) * f, xs = [];
    p.forEach(function (r) { for (var i = 0, j = r.length - 1; i < r.length; j = i++) { var a = r[j], b = r[i]; if ((a[1] > y) !== (b[1] > y)) xs.push(a[0] + (y - a[1]) * (b[0] - a[0]) / (b[1] - a[1])); } });
    xs.sort(function (a, b) { return a - b; });
    for (var k = 0; k + 1 < xs.length; k += 2) { var w = xs[k + 1] - xs[k]; if (!best || w > best.w * 1.15) best = { w: w, x: (xs[k] + xs[k + 1]) / 2, y: y }; }
  });
  return best ? [ best.x, best.y ] : [ (cj[0] + cj[2]) / 2, (cj[1] + cj[3]) / 2 ];
}
function wsuSeTocan(a, b, t) { return a[0] <= b[2] + t && b[0] <= a[2] + t && a[1] <= b[3] + t && b[1] <= a[3] + t; }
function wsuColores(items) {
  var col = {}, cajas = items.map(function (x) { return wsuCaja(wsuGeom(x)); });
  items.forEach(function (x, i) {
    var usados = {};
    for (var j = 0; j < i; j++) if (wsuSeTocan(cajas[i], cajas[j], 1e-4)) usados[col[items[j].u]] = 1;
    col[x.u] = WSU_PASTEL.find(function (c) { return !usados[c]; }) || WSU_PASTEL[i % WSU_PASTEL.length];
  });
  return col;
}

// ------------------------------------------------------------------ dibujo
function wsuVista(caja, ancho, alto) {
  var lat0 = (caja[1] + caja[3]) / 2, kx = Math.max(0.2, Math.cos(lat0 * Math.PI / 180));
  var x0 = caja[0] * kx, x1 = caja[2] * kx, y0 = caja[1], y1 = caja[3], w = x1 - x0, hh = y1 - y0;
  if (w / hh > ancho / alto) { var d = (w * alto / ancho - hh) / 2; y0 -= d; y1 += d; } else { var e = (hh * ancho / alto - w) / 2; x0 -= e; x1 += e; }
  var m = 0.08 * (x1 - x0), n = 0.08 * (y1 - y0); x0 -= m; x1 += m; y0 -= n; y1 += n;
  var s = ancho / (x1 - x0);
  return { kx: kx, s: s, x0: x0, y1: y1, lon0: x0 / kx, lon1: x1 / kx, lat0: y0, lat1: y1,
    P: function (q) { return [ (q[0] * kx - x0) * s, (y1 - q[1]) * s ]; } };
}
function wsuTrazo(ctx, V, polys) {
  ctx.beginPath();
  polys.forEach(function (p) { p.forEach(function (r) { r.forEach(function (q, i) { var a = V.P(q); i ? ctx.lineTo(a[0], a[1]) : ctx.moveTo(a[0], a[1]); }); ctx.closePath(); }); });
}
function wsuPintar(ctx, V, polys, relleno, borde, ancho) {
  wsuTrazo(ctx, V, polys);
  if (relleno) { ctx.fillStyle = relleno; ctx.fill('evenodd'); }
  if (borde) { ctx.strokeStyle = borde; ctx.lineWidth = ancho || 1; ctx.lineJoin = 'round'; ctx.stroke(); }
}
function wsuTexto(ctx, t, x, y, tam, color, negrita, fondo) {
  ctx.font = (negrita ? '600 ' : '500 ') + tam + "px Poppins, 'Segoe UI', Arial, sans-serif";
  ctx.textAlign = 'center'; ctx.textBaseline = 'middle';
  if (fondo) { var w = ctx.measureText(t).width; ctx.fillStyle = 'rgba(255,255,255,.78)'; ctx.fillRect(x - w / 2 - 4, y - tam * 0.7, w + 8, tam * 1.4); }
  ctx.lineWidth = 3; ctx.strokeStyle = 'rgba(255,255,255,.85)'; ctx.strokeText(t, x, y);
  ctx.fillStyle = color; ctx.fillText(t, x, y);
}
function wsuNombres(ctx, V, items, grande, ancho, alto, ocupados) {
  // primero el nombre resaltado y los grandes; un nombre que se cruzaría con otro ya puesto o se saldría del marco no se escribe
  var area = (V.lon1 - V.lon0) * (V.lat1 - V.lat0), lista = items.map(function (x) {
    var polys = wsuGeom(x); return { x: x, polys: polys, fr: wsuArea(polys) / area, es: !!(grande && x.u === grande.u) };
  }).filter(function (o) { return o.fr >= 0.0025 || o.es; }).sort(function (a, b) { return (b.es - a.es) || (b.fr - a.fr); });
  lista.forEach(function (o) {
    var p = V.P(wsuPuntoNombre(o.polys)), tam = (o.fr < 0.01 ? 14 : o.fr < 0.04 ? 16 : 19) + (o.es ? 3 : 0), t = o.x.n.toUpperCase();
    ctx.font = (o.es ? '600 ' : '500 ') + tam + "px Poppins, 'Segoe UI', Arial, sans-serif";
    var w = ctx.measureText(t).width + 8, r = [ p[0] - w / 2, p[1] - tam * 0.75, p[0] + w / 2, p[1] + tam * 0.75 ];
    if (r[0] < 8 || r[2] > ancho - 8 || r[1] < 8 || r[3] > alto - 8) return;
    if (ocupados.some(function (q) { return r[0] < q[2] && q[0] < r[2] && r[1] < q[3] && q[1] < r[3]; })) return;
    ocupados.push(r);
    wsuTexto(ctx, t, p[0], p[1], tam, WSU_TXT, o.es, o.es);
  });
}
function wsuNorte(ctx, x, y) {
  ctx.fillStyle = WSU_AZUL; ctx.beginPath(); ctx.moveTo(x, y); ctx.lineTo(x - 13, y + 46); ctx.lineTo(x, y + 36); ctx.closePath(); ctx.fill();
  ctx.fillStyle = '#fff'; ctx.strokeStyle = WSU_AZUL; ctx.lineWidth = 1.5; ctx.beginPath(); ctx.moveTo(x, y); ctx.lineTo(x + 13, y + 46); ctx.lineTo(x, y + 36); ctx.closePath(); ctx.fill(); ctx.stroke();
  wsuTexto(ctx, 'N', x, y - 14, 22, WSU_AZUL, true);
}
function wsuEscala(ctx, V, x, y, ancho) {
  var kmPx = 111.32 / V.s, obj = ancho * 0.24 * kmPx, n = Math.pow(10, Math.floor(Math.log10(obj)));
  var paso = [ 5, 2, 1 ].map(function (m) { return m * n; }).find(function (v) { return v <= obj; }) || n, largo = paso / kmPx;
  ctx.fillStyle = 'rgba(255,255,255,.8)'; ctx.fillRect(x - 12, y - 30, largo + 50, 50);
  for (var k = 0; k < 4; k++) { ctx.fillStyle = k % 2 ? '#fff' : WSU_AZUL; ctx.fillRect(x + k * largo / 4, y, largo / 4, 9); }
  ctx.strokeStyle = WSU_AZUL; ctx.lineWidth = 1.2; ctx.strokeRect(x, y, largo, 9);
  wsuTexto(ctx, '0', x, y - 12, 14, WSU_AZUL); wsuTexto(ctx, (paso >= 1 ? paso : paso * 1000) + (paso >= 1 ? ' km' : ' m'), x + largo, y - 12, 14, WSU_AZUL);
}
function wsuRecuadro(ctx, V, polys) {
  var c = wsuCaja(polys), a = V.P([ c[0], c[3] ]), b = V.P([ c[2], c[1] ]), m = Math.max(b[0] - a[0], b[1] - a[1]) * 0.12 + 6;
  ctx.strokeStyle = WSU_REC; ctx.lineWidth = 4; ctx.strokeRect(a[0] - m, a[1] - m, b[0] - a[0] + 2 * m, b[1] - a[1] + 2 * m);
}

// nivel: 'pais' | 'region' | 'provincia' | 'distrito'; u: ubigeos elegidos {dep, prov, dist}
function wsuDibujar(nivel, u) {
  var L = wsuDatos(); if (!L) throw Error('Esta versión de DrenIE no trae los límites del INEI.');
  var W = WSU_W, H = WSU_H, c = document.createElement('canvas'); c.width = W; c.height = H;
  var ctx = c.getContext('2d'), deps = wsuLista('region'), foco, items, fondo = [], sig = null, mar = false;
  if (nivel === 'pais') { foco = deps.reduce(function (a, x) { return a.concat(wsuGeom(x)); }, []); items = deps; sig = wsuPorU(u.dep); mar = true; }
  else if (nivel === 'region') { var d = wsuPorU(u.dep); if (!d) throw Error('Elija el departamento.'); foco = wsuGeom(d); items = wsuLista('provincia', d.u); sig = wsuPorU(u.prov); fondo = deps.filter(function (x) { return x.u !== d.u; }); }
  else if (nivel === 'provincia') { var p = wsuPorU(u.prov); if (!p) throw Error('Elija la provincia.'); foco = wsuGeom(p); items = wsuLista('distrito', p.u); sig = wsuPorU(u.dist); fondo = wsuLista('provincia').filter(function (x) { return x.u !== p.u; }); }
  else { var t = wsuPorU(u.dist); if (!t) throw Error('Elija el distrito.'); foco = wsuGeom(t); items = [ t ]; sig = t; fondo = wsuLista('distrito').filter(function (x) { return x.u !== t.u; }); }
  var V = wsuVista(wsuCaja(foco), W, H), vista = [ V.lon0, V.lat0, V.lon1, V.lat1 ];
  ctx.fillStyle = mar ? '#DCEEFB' : '#F7F9FB'; ctx.fillRect(0, 0, W, H);
  if (mar) (L.paises || []).forEach(function (x) { wsuPintar(ctx, V, wsuGeom(x), '#ECEFF3', '#9AA8B8', 1); });
  var cerca = fondo.filter(function (x) { return wsuSeTocan(wsuCaja(wsuGeom(x)), vista, 0); });
  cerca.forEach(function (x) { wsuPintar(ctx, V, wsuGeom(x), '#EEF1F4', '#B9C5D2', 0.8); });
  var col = wsuColores(items);
  items.forEach(function (x) {
    var es = sig && x.u === sig.u.slice(0, x.u.length);
    wsuPintar(ctx, V, wsuGeom(x), es ? WSU_RES : col[x.u], '#5A6B7D', es ? 1.6 : 1);
  });
  var ocupados = [ [ W - 100, 0, W, 110 ], [ 0, H - 70, 330, H ], [ W - 520, H - 30, W, H ] ];   // norte, escala y fuente
  wsuNombres(ctx, V, items, sig, W, H, ocupados);
  if (nivel !== 'pais') wsuNombres(ctx, V, cerca, null, W, H, ocupados);
  if (mar) {
    WSU_PAISES.forEach(function (p) { var a = V.P([ p[1], p[2] ]); if (a[0] > 40 && a[0] < W - 40 && a[1] > 30 && a[1] < H - 30) wsuTexto(ctx, p[0], a[0], a[1], 17, '#6A7889', true); });
    var o = V.P([ -81.6, -12.5 ]); wsuTexto(ctx, 'OCÉANO', o[0], o[1] - 11, 16, '#3D7DB8'); wsuTexto(ctx, 'PACÍFICO', o[0], o[1] + 11, 16, '#3D7DB8');
  }
  if (sig && nivel !== 'distrito') wsuRecuadro(ctx, V, wsuGeom(sig));
  if (nivel === 'distrito' && sig.cap) { var q = V.P(wsuPuntoNombre(wsuGeom(sig))); wsuTexto(ctx, 'Capital: ' + sig.cap, q[0], q[1] + 30, 14, WSU_TXT, false, true); }
  wsuNorte(ctx, W - 56, 40);
  wsuEscala(ctx, V, 34, H - 34, W);
  ctx.font = "500 12px Poppins, 'Segoe UI', Arial, sans-serif"; ctx.textAlign = 'right'; ctx.textBaseline = 'bottom';
  var f = WSU_FUENTE + (mar ? '; países: Natural Earth' : ''), fw = ctx.measureText(f).width;
  ctx.fillStyle = 'rgba(255,255,255,.8)'; ctx.fillRect(W - fw - 14, H - 24, fw + 10, 20); ctx.fillStyle = '#5C7390'; ctx.fillText(f, W - 8, H - 8);
  ctx.strokeStyle = WSU_AZUL; ctx.lineWidth = 3; ctx.strokeRect(1.5, 1.5, W - 3, H - 3);
  return wsuImagen(c, 'mapa_' + nivel + '.png');
}
function wsuImagen(c, nombre) {
  var data = c.toDataURL('image/png');
  if (data.length > 3e5) data = c.toDataURL('image/jpeg', .9);
  if (data.length > 3e5) data = c.toDataURL('image/jpeg', .75);
  if (data.length > 34e4) data = c.toDataURL('image/jpeg', .6);
  return { data: data, width: c.width, height: c.height, fileName: nombre };
}
// Toda imagen cargada se ajusta al mismo marco de los mapas automáticos (sin deformarla; el resto queda en blanco).
async function wsuEncajar(image) {
  if (!image || !image.data) return image;
  var img = await new Promise(function (res, rej) { var i = new Image; i.onload = function () { res(i); }; i.onerror = function () { rej(Error('No se pudo leer la imagen.')); }; i.src = image.data; });
  var c = document.createElement('canvas'); c.width = WSU_W; c.height = WSU_H;
  var ctx = c.getContext('2d'), k = Math.min(WSU_W / img.width, WSU_H / img.height), w = img.width * k, hh = img.height * k;
  ctx.fillStyle = '#fff'; ctx.fillRect(0, 0, WSU_W, WSU_H);
  ctx.imageSmoothingQuality = 'high'; ctx.drawImage(img, (WSU_W - w) / 2, (WSU_H - hh) / 2, w, hh);
  ctx.strokeStyle = WSU_AZUL; ctx.lineWidth = 3; ctx.strokeRect(1.5, 1.5, WSU_W - 3, WSU_H - 3);
  var out = wsuImagen(c, image.fileName || 'mapa.png');
  if (out.data.length > 35e4) throw Error('La imagen contiene demasiado detalle. Recorte el mapa antes de cargarlo.');
  return out;
}

// ------------------------------------------------------------------ estado
var WSU_NIVELES = { pais: 0, region: 1, provincia: 2, distrito: 3 };
// Redibuja los mapas automáticos (o vacíos) afectados por un cambio de ubigeo. Un mapa propio no se toca.
function wsuRegenerar(setState, u, niveles, forzar) {
  setState(function (prev) {
    var g = wsGeo(prev), maps = (g.maps || []).slice();
    niveles.forEach(function (nivel) {
      var i = maps.findIndex(function (m) { return m.level === nivel; }), m = i >= 0 ? maps[i] : { level: nivel, points: [], mode: 'point' };
      if (m.image && !m.auto && !(forzar && forzar === nivel)) return;
      var need = [ 'dep', 'dep', 'prov', 'dist' ][WSU_NIVELES[nivel]];
      var n = Object.assign({}, m, { points: [], closed: false, auto: true });
      if (!u[need] && nivel !== 'pais') { n.image = null; }
      else { try { n.image = wsuDibujar(nivel, u); } catch (e) { return; } }
      if (!n.source || m.auto) n.source = WSU_FUENTE;
      if (i >= 0) maps[i] = n; else maps.push(n);
    });
    return Object.assign({}, prev, { project: Object.assign({}, prev.project, { geography: Object.assign({}, g, { maps: maps }) }) });
  });
}
function wsuElegir(props, nivel, valor) {
  var st = props.state, g = wsGeo(st), u = wsuUbigeo(g), x = wsuPorU(valor), patch = {};
  if (nivel === 'region') { u = { dep: valor, prov: '', dist: '' }; patch = { region: x ? x.n : '', province: '', district: '' }; }
  else if (nivel === 'provincia') { u = { dep: u.dep, prov: valor, dist: '' }; patch = { province: x ? x.n : '', district: '' }; }
  else { u = { dep: u.dep, prov: u.prov, dist: valor }; patch = { district: x ? x.n : '' }; }
  patch.ubigeo = u;
  wsSetGeo(props.setState, patch);
  var afecta = { region: [ 'pais', 'region', 'provincia', 'distrito' ], provincia: [ 'region', 'provincia', 'distrito' ], distrito: [ 'provincia', 'distrito' ] }[nivel];
  wsuRegenerar(props.setState, u, afecta);
}

// Barra de cada recuadro: lista desplegable del nivel y botón para usar el mapa automático.
function WsAutoMapa(props) {
  var st = props.state, level = props.level, m = props.map, g = wsGeo(st), u = wsuUbigeo(g);
  if (!wsuDatos()) return null;
  if (level === 'localidad') return h('p', { className: 'muted small' }, 'Cargue la foto o captura de la localidad: el programa la ajusta al mismo tamaño de los demás mapas.');
  var sel, opciones = [], valor = '';
  if (level === 'pais') opciones = [ [ 'PE', 'Perú' ] ], valor = 'PE';
  else if (level === 'region') { opciones = wsuLista('region').map(function (x) { return [ x.u, x.n ]; }); valor = u.dep || ''; }
  else if (level === 'provincia') { opciones = u.dep ? wsuLista('provincia', u.dep).map(function (x) { return [ x.u, x.n ]; }) : []; valor = u.prov || ''; }
  else { opciones = u.prov ? wsuLista('distrito', u.prov).map(function (x) { return [ x.u, x.n ]; }) : []; valor = u.dist || ''; }
  var etiqueta = { pais: 'País', region: 'Departamento', provincia: 'Provincia', distrito: 'Distrito' }[level];
  var falta = level === 'provincia' && !u.dep ? 'Primero elija el departamento.' : level === 'distrito' && !u.prov ? 'Primero elija la provincia.' : '';
  sel = h('label', { className: 'ws-field wsu-sel', style: { flex: '1 1 320px', maxWidth: 420, minWidth: 0 } }, h('span', null, etiqueta),
    h('select', { 'aria-label': etiqueta + ' del mapa', value: valor, style: { width: '100%' }, disabled: level === 'pais' || !!falta,
      onChange: function (e) { wsuElegir(props, level, e.target.value); } },
      (level === 'pais' ? [] : [ h('option', { key: '', value: '' }, falta || '— Elija —') ]).concat(opciones.map(function (o) { return h('option', { key: o[0], value: o[0] }, o[1]); }))));
  var listo = level === 'pais' || (level === 'region' ? u.dep : level === 'provincia' ? u.prov : u.dist);
  var boton = listo && !(m.image && m.auto) ? h(Btn, { onClick: function () { wsuRegenerar(props.setState, u, [ level ], level); props.message('Mapa automático dibujado con los límites del INEI.'); } },
    m.image ? 'Usar el mapa automático' : 'Dibujar el mapa') : null;
  return h('div', { className: 'ws-actions wsu-barra', style: { alignItems: 'flex-end' } }, sel, boton, m.image && m.auto ? h('span', { className: 'muted small' }, 'Mapa automático (INEI)') : null);
}
