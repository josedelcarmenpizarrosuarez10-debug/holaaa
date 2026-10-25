"""DrenIE 3.1.0 · página Red de cunetas (paso 15) y visor del motor de la red.
Se ejecuta después de patches_workspace.py (usa R). El visor sale de motor_red/visor/visor.html (el mismo que entrega el
motor en cada proyecto), con la letra Poppins
incrustada y sin recursos externos; queda en src/visor-red.html, cubierto por la comprobación de integridad."""
R("state.step === 14 ? h(WsPlan,{state:state,setState:setState,onStep:setStep}) :",
  "state.step === 14 ? h(WsPlan,{state:state,setState:setState,onStep:setStep}) : state.step === 15 ? h(RcPage,{state:state,setState:setState,onStep:setStep}) :",
  1, '3.1.0 página Red de cunetas')

vis = open(os.path.join(CLIENT, '..', 'motor_red', 'visor', 'visor.html'), encoding='utf-8').read()
vis = re.sub(r'<link rel="stylesheet" href="https://fonts\.googleapis\.com[^>]*>\n?', '', vis)
vis = re.sub(r'<meta name="claude:[^>]*>\n?', '', vis)
if re.search(r'https?://|<script\s+src=|<link\s', vis):
    sys.exit('El visor de la red no puede cargar recursos externos.')
cuerpo = vis.index('<div class="app">')
pagina = ('<!doctype html>\n<html lang="es"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">'
          '<style id="drenie-v3-fonts">' + ''.join(fonts) + '</style>\n' + vis[:cuerpo] + '</head><body>\n' + vis[cuerpo:] + '\n</body></html>\n')
open(os.path.join(CLIENT, 'src', 'visor-red.html'), 'w', encoding='utf-8').write(pagina)
