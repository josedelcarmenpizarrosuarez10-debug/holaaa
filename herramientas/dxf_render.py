"""Render de laminas DXF a PNG (para revision) con ezdxf + matplotlib."""
import sys, ezdxf, matplotlib; matplotlib.use("Agg")
from ezdxf.addons.drawing import RenderContext, Frontend
from ezdxf.addons.drawing.matplotlib import MatplotlibBackend
from ezdxf.addons.drawing.config import Configuration, BackgroundPolicy, ColorPolicy, LineweightPolicy
import matplotlib.pyplot as plt

def render(dxf, png, box, dpi=110, ancho_in=23.4, color=False):
    doc = ezdxf.readfile(dxf); msp = doc.modelspace()
    cfg = Configuration(background_policy=BackgroundPolicy.WHITE, color_policy=ColorPolicy.COLOR if color else ColorPolicy.BLACK, lineweight_policy=LineweightPolicy.ABSOLUTE, min_lineweight=0.08)
    ctx = RenderContext(doc); ctx.set_current_layout(msp)
    x0, y0, x1, y1 = box; w, h = x1 - x0, y1 - y0
    fig = plt.figure(figsize=(ancho_in, ancho_in * h / w)); ax = fig.add_axes([0, 0, 1, 1])
    Frontend(ctx, MatplotlibBackend(ax), config=cfg).draw_layout(msp, finalize=False)
    ax.set_xlim(x0, x1); ax.set_ylim(y0, y1); ax.set_aspect("equal", adjustable="box"); ax.axis("off")
    fig.savefig(png, dpi=dpi); plt.close(fig)

if __name__ == "__main__":
    render(sys.argv[1], sys.argv[2], tuple(float(v) for v in sys.argv[3:7]), dpi=int(sys.argv[7]) if len(sys.argv) > 7 else 110, color=len(sys.argv) > 8)
