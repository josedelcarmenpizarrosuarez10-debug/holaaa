import ezdxf, sys, collections, re, time
f=sys.argv[1]; t=time.time()
doc=ezdxf.readfile(f); msp=doc.modelspace()
print('leido', round(time.time()-t), 's', [l.name for l in doc.layouts])
c=collections.Counter(); tipos=collections.Counter()
for e in msp:
    c[e.dxf.layer]+=1; tipos[e.dxftype()]+=1
print(tipos.most_common(15))
for k,v in c.most_common(70): print(v,k)
txt=collections.Counter()
for e in msp.query('TEXT MTEXT'):
    try: s=e.plain_text() if e.dxftype()=='MTEXT' else e.dxf.text
    except Exception: continue
    s=s.strip().replace('\n',' ')
    if re.search(r'ELEVAC|CORTE|FACHADA|EDIFICACI|BLOQUE|LOSA|TECHO|NPT|N\.P\.T|PLANTA', s, re.I): txt[s[:60]]+=1
for k,v in txt.most_common(60): print('T',v,k)
