'use strict';
// DrenIE 3.1.0 · página Red de cunetas en Chromium real con el motor real (python -m drenie_motor). El puente de Windows se
// simula: motor_red llama al motor por este servidor de prueba y motor_elegir devuelve archivos de prueba.
// Uso: DRENIE_MOTOR_DIR=<carpeta drenie_motor> DRENIE_RED_PLANO=<plano.dxf> node tests/red_cunetas_ui.cjs
const fs = require('fs'), path = require('path'), http = require('http'), os = require('os'), assert = require('assert/strict'), { spawn } = require('child_process');
const { chromium } = require('playwright');
const root = path.resolve(__dirname, '..'), base = path.join(root, 'client/src');
const motorDir = process.env.DRENIE_MOTOR_DIR, plano = process.env.DRENIE_RED_PLANO;
const out = process.env.DRENIE_RED_UI_OUT || path.resolve(root, '../verificacion_red_cunetas'); fs.mkdirSync(out, { recursive: true });
const carpeta = fs.mkdtempSync(path.join(os.tmpdir(), 'drenie-red-'));
const report = { scope: 'React/Chromium reales y motor real; puente Windows simulado. No acredita instalación Windows.', checks: [], pageErrors: [] };
if (!motorDir || !plano) { console.error('Defina DRENIE_MOTOR_DIR y DRENIE_RED_PLANO.'); process.exit(2); }

function motor(accion, args, entrada) {
  return new Promise((res) => {
    const p = spawn(process.env.PYTHON || 'python3', ['-m', 'drenie_motor', accion, ...args], { cwd: motorDir, env: Object.assign({}, process.env, { PYTHONIOENCODING: 'utf-8' }) });
    let o = '', e = ''; p.stdout.on('data', d => o += d); p.stderr.on('data', d => e += d);
    p.on('close', () => res(o.trim() || JSON.stringify({ error: 'sin respuesta: ' + e.slice(-400) })));
    p.stdin.end(entrada || '');
  });
}
const server = http.createServer((req, res) => {
  const url = new URL(req.url, 'http://localhost');
  if (url.pathname === '/__motor') {
    let cuerpo = ''; req.on('data', d => cuerpo += d);
    req.on('end', async () => { const a = JSON.parse(cuerpo); res.setHeader('Content-Type', 'application/json; charset=utf-8'); res.end(await motor(a.accion, a.args || [], a.entrada)); });
    return;
  }
  let file = path.resolve(base, '.' + url.pathname); if (file === base) file += '/index.html';
  if (!file.startsWith(base + '/')) return res.writeHead(403).end();
  fs.readFile(file, (err, b) => {
    if (err) return res.writeHead(404).end();
    res.setHeader('Content-Type', file.endsWith('.html') ? 'text/html; charset=utf-8' : file.endsWith('.js') ? 'application/javascript' : 'application/octet-stream'); res.end(b);
  });
});
async function main() {
  let browser;
  try {
    await new Promise(r => server.listen(0, '127.0.0.1', r));
    browser = await chromium.launch({ headless: true, args: ['--no-sandbox'] });
    const context = await browser.newContext({ viewport: { width: 1600, height: 1000 }, timezoneId: 'America/Lima' });
    await context.addInitScript(([plano, carpeta]) => {
      if (window.parent !== window) return;          // solo la ventana principal tiene el puente nativo
      window.__calls = [];
      window.__TAURI__ = { core: { invoke: async (cmd, args) => {
        window.__calls.push({ cmd, args });
        if (cmd === 'license_status') return { full: true, kind: 'owner', modules: ['calculate', 'projects', 'import', 'assistant', 'reports', 'export'], holder: 'Prueba', machine: 'TEST', demo_active: false };
        if (cmd === 'motor_red') { const r = await fetch('/__motor', { method: 'POST', body: JSON.stringify(args) }); return r.text(); }
        if (cmd === 'motor_elegir') return args.tipo === 'dxf' ? plano : args.tipo === 'carpeta' ? carpeta : null;
        return null;
      } } };
    }, [plano, carpeta]);
    const page = await context.newPage();
    page.on('pageerror', e => report.pageErrors.push('ventana: ' + e.message));
    page.on('console', m => { if (m.type() === 'error' && !/Failed to load resource/.test(m.text())) report.pageErrors.push('consola: ' + m.text()); });
    await page.goto('http://127.0.0.1:' + server.address().port + '/');
    await page.waitForFunction(() => window.__APP_MOUNTED__);
    await page.evaluate(() => { try { localStorage.removeItem('drenie-red-recientes'); } catch (e) {} });
    // Curva IDF del proyecto en la pestaña LLUVIA (la de ejemplo del programa): la red la toma de ahí.
    await page.getByRole('tab', { name: 'LLUVIA', exact: true }).click();
    const idf = [[10, 142], [30, 94], [60, 67], [120, 43], [360, 22], [720, 13]];
    for (let i = 0; i < idf.length; i++) {
      await page.getByLabel('Duración fila ' + (i + 1), { exact: true }).fill(String(idf[i][0]));
      await page.getByLabel('Intensidad fila ' + (i + 1), { exact: true }).fill(String(idf[i][1]));
    }
    const tab = page.getByRole('tab', { name: 'RED DE CUNETAS', exact: true });
    await tab.click();
    await page.getByRole('heading', { name: 'Red de cunetas desde el plano', exact: true }).waitFor();
    assert.equal(await tab.getAttribute('aria-selected'), 'true');
    const pestanas = await page.getByRole('tab').allTextContents();
    assert.equal(pestanas[pestanas.indexOf('LLUVIA') + 1], 'RED DE CUNETAS', 'la red va después de LLUVIA: ' + pestanas.join(', '));
    const rib = page.locator('.rb-panel');
    for (const b of ['Nuevo desde plano DXF', 'Calcular todo', 'Entregables', 'Eje de cuneta', 'Montante', 'Sumidero', 'Descarga', 'Asignar superficie', 'Polilínea', 'Recortar', 'Distancia'])
      assert.equal(await rib.getByRole('button', { name: b, exact: true }).count(), 1, 'falta el botón ' + b);
    await page.screenshot({ path: path.join(out, '01_inicio_red.png') });
    report.checks.push({ name: 'Pestaña RED DE CUNETAS con su cinta de iconos y su página', passed: true });

    await rib.getByRole('button', { name: 'Nuevo desde plano DXF', exact: true }).click();
    await page.getByRole('button', { name: 'Elegir plano DXF', exact: true }).click();
    await page.getByRole('heading', { name: '2 · Datos del proyecto' }).waitFor({ timeout: 120000 });
    assert.equal(await page.getByLabel('Cerco perimétrico (límite de intervención)').inputValue(), 'CERCO');
    await page.getByRole('textbox', { name: 'Nombre del proyecto', exact: true }).fill('Prueba de la red de cunetas');
    await page.getByRole('textbox', { name: 'NPT y borde de cuneta (m)', exact: true }).fill('195.86');
    assert.match(await page.locator('.rc-lluvia b').innerText(), /^142[.,]00 mm\/h$/);           // curva IDF del proyecto, tc = 10 min
    assert.match(await page.locator('.rc-lluvia small').innerText(), /Pestaña LLUVIA de DrenIE/);
    await page.getByRole('button', { name: 'Carpeta del proyecto', exact: true }).click();
    await page.getByText(carpeta, { exact: true }).waitFor();
    await page.screenshot({ path: path.join(out, '02_asistente.png'), fullPage: true });
    report.checks.push({ name: 'Asistente: capas del plano sugeridas, datos, niveles y lluvia de la pestaña LLUVIA', passed: true });

    await page.getByRole('button', { name: 'Crear y abrir el proyecto', exact: true }).click();
    const marco = page.frameLocator('.rc-visor iframe');
    await page.waitForFunction(() => window.__calls.filter(c => c.cmd === 'motor_red' && c.args.accion === 'leer').length === 1, null, { timeout: 300000 });
    await marco.locator('#historial').getByText(/Proyecto cargado/).waitFor({ timeout: 300000 });
    assert(fs.existsSync(path.join(carpeta, 'proyecto.json')));
    assert.equal(await marco.locator('#barra').isVisible(), false);    // la cinta de DrenIE reemplaza la barra del visor
    await page.waitForTimeout(500);
    await page.screenshot({ path: path.join(out, '03_visor_en_drenie.png') });
    report.checks.push({ name: 'Proyecto creado, plano leído y visor claro dentro de DrenIE', passed: true });

    await rib.getByRole('button', { name: 'Eje de cuneta', exact: true }).click();
    await marco.locator('#pregunta').filter({ hasText: /cuneta|punto/i }).waitFor();
    await page.keyboard.press('Escape');
    report.checks.push({ name: 'Los botones de la cinta inician los comandos del visor', passed: true });

    await rib.getByRole('button', { name: 'Calcular todo', exact: true }).click();
    await page.locator('.rc-velo').waitFor();
    await page.screenshot({ path: path.join(out, '04_calculando.png') });
    await page.locator('.rc-velo').waitFor({ state: 'detached', timeout: 600000 });
    await marco.locator('#historial').getByText(/Cálculo listo/).waitFor({ timeout: 60000 });
    assert(fs.existsSync(path.join(carpeta, 'salida', 'resultado.json')));
    const cfg = JSON.parse(fs.readFileSync(path.join(carpeta, 'proyecto.json'), 'utf8'));
    assert.equal(cfg.lluvia.I_mmh, 142); assert.match(cfg.lluvia.fuente, /Pestaña LLUVIA de DrenIE.*CURVA DE EJEMPLO/);
    assert.equal(await page.evaluate(() => window.__calls.filter(c => c.cmd === 'motor_red' && c.args.accion === 'datos').length), 1);
    await page.waitForTimeout(800);
    await page.screenshot({ path: path.join(out, '05_resultado_y_soluciones.png') });
    report.checks.push({ name: 'Calcular todo con el motor real desde la cinta', passed: true });

    await rib.getByRole('button', { name: 'Entregables', exact: true }).click();
    await marco.getByText('Entregables del último cálculo').waitFor();
    const n = await marco.locator('table.entreg tr').count(); assert(n > 10, 'pocos entregables: ' + n);
    await page.screenshot({ path: path.join(out, '06_entregables.png') });
    report.checks.push({ name: 'Entregables del cálculo (' + n + ' archivos)', passed: true });
    assert.deepEqual(report.pageErrors, []);
    report.passed = true;
  } catch (e) { report.error = e.stack; report.passed = false; process.exitCode = 1; }
  finally { if (browser) await browser.close(); server.close(); fs.writeFileSync(path.join(out, 'UI_RED_CUNETAS.json'), JSON.stringify(report, null, 2)); console.log(JSON.stringify(report, null, 2)); }
}
main();
