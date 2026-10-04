"""Recorta un DXF grande a una caja (sin achurados) para poder renderizarlo con poca memoria."""
import sys, ezdxf
def recortar(src, dst, box, sin_hatch=True):
    x0, y0, x1, y1 = box
    doc = ezdxf.readfile(src); msp = doc.modelspace()
    out = ezdxf.new("R2010"); om = out.modelspace()
    for l in doc.layers:
        if l.dxf.name not in out.layers: out.layers.add(l.dxf.name, color=l.color)
    def dentro(x, y): return x0 <= x <= x1 and y0 <= y <= y1
    n = 0
    for e in msp:
        t = e.dxftype()
        try:
            if t == "LINE":
                if dentro(e.dxf.start.x, e.dxf.start.y) or dentro(e.dxf.end.x, e.dxf.end.y):
                    om.add_line(e.dxf.start, e.dxf.end, dxfattribs={"layer": e.dxf.layer, "color": e.dxf.color}); n += 1
            elif t == "LWPOLYLINE":
                pts = list(e.get_points("xyb"))
                if any(dentro(p[0], p[1]) for p in pts):
                    om.add_lwpolyline([(p[0], p[1]) for p in pts], close=e.closed, dxfattribs={"layer": e.dxf.layer, "color": e.dxf.color}); n += 1
            elif t in ("TEXT", "MTEXT"):
                if dentro(e.dxf.insert.x, e.dxf.insert.y):
                    s = e.plain_text() if t == "MTEXT" else e.dxf.text
                    h = e.dxf.char_height if t == "MTEXT" else e.dxf.height
                    om.add_text(s[:60], height=h, dxfattribs={"layer": e.dxf.layer, "color": e.dxf.color}).set_placement(e.dxf.insert); n += 1
            elif t in ("ARC", "CIRCLE"):
                if dentro(e.dxf.center.x, e.dxf.center.y):
                    om.add_foreign_entity(e) if False else None
                    if t == "CIRCLE": om.add_circle(e.dxf.center, e.dxf.radius, dxfattribs={"layer": e.dxf.layer, "color": e.dxf.color})
                    else: om.add_arc(e.dxf.center, e.dxf.radius, e.dxf.start_angle, e.dxf.end_angle, dxfattribs={"layer": e.dxf.layer, "color": e.dxf.color})
                    n += 1
            elif t == "INSERT":
                if dentro(e.dxf.insert.x, e.dxf.insert.y):
                    for v in e.virtual_entities():
                        if v.dxftype() == "LINE": om.add_line(v.dxf.start, v.dxf.end, dxfattribs={"layer": e.dxf.layer})
                        elif v.dxftype() == "LWPOLYLINE": om.add_lwpolyline([(p[0], p[1]) for p in v.get_points("xy")], close=v.closed, dxfattribs={"layer": e.dxf.layer})
                    n += 1
        except Exception:
            pass
    out.saveas(dst); return n
if __name__ == "__main__":
    print(recortar(sys.argv[1], sys.argv[2], tuple(float(v) for v in sys.argv[3:7])))
