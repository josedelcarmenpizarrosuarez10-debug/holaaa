// DrenIE 3.1.0 · Actualizaciones automáticas firmadas. El programa consulta si hay una versión nueva (orden nativa
// buscar_actualizacion) y solo instala un instalador firmado por Hidroconsult (instalar_actualizacion comprueba la firma).
// Búsqueda automática: una vez al día, al abrir el programa, sin molestar si no hay conexión o si no hay versión nueva.
V3_RIB_ICONS.actualizar = '<circle cx="16" cy="16" r="11" fill="#E0F2FE" stroke="#0B2545" stroke-width="1.5"/><path d="M16 9v10" stroke="#1EA7F2" stroke-width="2.6" stroke-linecap="round"/><path d="M11 15l5 5 5-5" fill="none" stroke="#1EA7F2" stroke-width="2.6" stroke-linecap="round" stroke-linejoin="round"/><path d="M10 23h12" stroke="#0B2545" stroke-width="1.8" stroke-linecap="round"/>';
var ACT = { ocupado: false };
function v3Actualizar(silencioso) {
  if (!window.__TAURI__) { if (!silencioso) v3Notice('Las actualizaciones se buscan desde la aplicación de Windows.', { title: 'Actualizaciones' }); return; }
  if (ACT.ocupado) return;
  ACT.ocupado = true;
  nativeCall('buscar_actualizacion', {}).then(function (n) {
    try { localStorage.setItem('drenie-actualizacion-buscada', String(Date.now())); } catch (e) {}
    if (!n || !n.disponible) { if (!silencioso) v3Notice('Ya tiene la última versión de DrenIE (' + ((n && n.actual) || '') + ').', { title: 'Actualizaciones' }); return; }
    v3Ask('Hay una versión nueva de DrenIE: ' + n.version + (n.fecha ? ' (' + n.fecha + ')' : '') + '. Usted tiene la ' + n.actual + '.' +
      (n.notas ? '\n\nNovedades:\n' + n.notas : '') + '\n\nGuarde su proyecto antes de continuar: DrenIE se cerrará, se instalará la versión nueva (firmada por Hidroconsult) y se volverá a abrir. Su licencia se conserva.',
      function () {
        v3Notice('Descargando e instalando la versión ' + n.version + '. No apague el equipo.', { title: 'Actualizaciones' });
        nativeCall('instalar_actualizacion', {}).catch(function (e) { v3Notice(String(e && e.message || e), { title: 'Actualizaciones' }); });
      }, { ok: 'Sí, actualizar ahora', cancel: 'Más tarde', title: 'Actualización disponible' });
  }).catch(function (e) {
    if (!silencioso) v3Notice(String(e && e.message || e), { title: 'Actualizaciones' });
  }).finally(function () { ACT.ocupado = false; });
}
(function () {
  if (typeof window === 'undefined') return;
  var dia = 24 * 3600 * 1000;
  function auto() {
    if (!window.__TAURI__ || !window.__APP_MOUNTED__) return;
    var ult = 0; try { ult = +localStorage.getItem('drenie-actualizacion-buscada') || 0; } catch (e) {}
    if (Date.now() - ult >= dia) v3Actualizar(true);
  }
  window.addEventListener('load', function () { setTimeout(auto, 20000); });
})();
