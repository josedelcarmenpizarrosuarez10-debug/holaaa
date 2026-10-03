import xml.etree.ElementTree as ET, pickle, collections
ns='{http://www.landxml.org/schema/LandXML-1.2}'
pts={};faces=[];cg=[];aligns={};groups=collections.Counter();surf_name=None
for ev,el in ET.iterparse('topo/TOPO FINAL.xml',events=('end',)):
    t=el.tag.replace(ns,'')
    if t=='P' and el.get('id'):
        n,e,z=map(float,el.text.split()); pts[int(el.get('id'))]=(e,n,z); el.clear()
    elif t=='F':
        faces.append(tuple(int(x) for x in el.text.split())); el.clear()
    elif t=='CgPoint' and el.text:
        n,e,z=map(float,el.text.split()[:3]); cg.append((el.get('name'),el.get('code'),e,n,z))
    elif t=='Alignment':
        aligns[el.get('name')]=ET.tostring(el)[:100000]
pickle.dump((pts,faces,cg),open('topo.pkl','wb'))
print(len(pts),'puntos sup',len(faces),'caras',len(cg),'cgpoints')
xs=[p[0] for p in pts.values()];ys=[p[1] for p in pts.values()];zs=[p[2] for p in pts.values()]
print('E',min(xs),max(xs),'N',min(ys),max(ys),'Z',min(zs),max(zs))
print(collections.Counter(c[1] for c in cg).most_common(25))
