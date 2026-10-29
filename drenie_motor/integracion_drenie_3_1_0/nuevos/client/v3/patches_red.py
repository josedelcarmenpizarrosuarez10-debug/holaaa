"""DrenIE 3.1.0 · página Red de cunetas (paso 15) y visor del motor de la red.
Se ejecuta después de patches_workspace.py (usa R). El visor sale de motor_red/visor/visor.html (el mismo que entrega el
motor en cada proyecto), con la letra Poppins
incrustada y sin recursos externos; queda en src/visor-red.html, cubierto por la comprobación de integridad."""
R("state.step === 14 ? h(WsPlan,{state:state,setState:setState,onStep:setStep}) :",
  "state.step === 14 ? h(WsPlan,{state:state,setState:setState,onStep:setStep}) : state.step === 15 ? h(RcPage,{state:state,setState:setState,onStep:setStep}) :",
  1, '3.1.0 página Red de cunetas')
R("state.step === 15 ? h(RcPage,{state:state,setState:setState,onStep:setStep}) :",
  "state.step === 15 ? h(RcPage,{state:state,setState:setState,onStep:setStep}) : state.step === 16 ? h(DvPage,{state:state,setState:setState,onStep:setStep}) :",
  1, '3.1.0 página Drenaje vial')
R("else if (tab === 'red') body = v3RedRibbon(props);", "else if (tab === 'red') body = v3RedRibbon(props);\n  else if (tab === 'vial') body = v3VialRibbon(props);",
  1, '3.1.0 cinta DRENAJE VIAL')
R("red:[15], lluvia: [1]", "red:[15], vial:[16], lluvia: [1]", 1, '3.1.0 pestaña DRENAJE VIAL abre su página')

vis = open(os.path.join(CLIENT, '..', 'motor_red', 'visor', 'visor.html'), encoding='utf-8').read()
vis = re.sub(r'<link rel="stylesheet" href="https://fonts\.googleapis\.com[^>]*>\n?', '', vis)
vis = re.sub(r'<meta name="claude:[^>]*>\n?', '', vis)
if re.search(r'https?://|<script\s+src=|<link\s', vis):
    sys.exit('El visor de la red no puede cargar recursos externos.')
cuerpo = vis.index('<div class="app">')
pagina = ('<!doctype html>\n<html lang="es"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">'
          '<style id="drenie-v3-fonts">' + ''.join(fonts) + '</style>\n' + vis[:cuerpo] + '</head><body>\n' + vis[cuerpo:] + '\n</body></html>\n')
open(os.path.join(CLIENT, 'src', 'visor-red.html'), 'w', encoding='utf-8').write(pagina)

# ---------------------------------------------------------------- mapas de ubicación automáticos (Datos del proyecto)
# Límites del INEI incorporados (el mismo archivo del motor de la red): País → Departamento → Provincia → Distrito sin internet.
lim = json.load(open(os.path.join(CLIENT, '..', 'motor_red', 'drenie_motor', 'limites_peru.json'), encoding='utf-8'))
lim_js = json.dumps({k: lim[k] for k in ('fuente', 'fuente_corta', 'departamentos', 'provincias', 'distritos', 'paises')}, ensure_ascii=False, separators=(',', ':'))
R("\n/* ===== fin DrenIE 3.0 ===== */\n",
  "\nvar WS_LIMITES_PERU = " + lim_js.replace('<', '\\u003C') + ";\n/* ===== fin DrenIE 3.0 ===== */\n", 1, '3.1.0 límites del INEI incorporados')
R("""    }, wsMapName(st, level))), h('div', {
        className: 'ws-actions'
    }, h(Btn, {
        onClick: function() {
            file.current.click();""", """    }, wsMapName(st, level))), h(WsAutoMapa, {
        state: st,
        setState: props.setState,
        level: level,
        map: m,
        message: message[1]
    }), h('div', {
        className: 'ws-actions'
    }, h(Btn, {
        onClick: function() {
            file.current.click();""", 1, '3.1.0 lista desplegable en cada mapa de ubicación')
R("""            var image = await wsReadMap(f);
            if (projectRuntime.id !== projectId) return;
            update({
                image: image,
                points: [],
                closed: false
            });""", """            var image = await wsuEncajar(await wsReadMap(f));
            if (projectRuntime.id !== projectId) return;
            update({
                image: image,
                points: [],
                closed: false,
                auto: false
            });""", 1, '3.1.0 imagen cargada ajustada al tamaño de los mapas')
