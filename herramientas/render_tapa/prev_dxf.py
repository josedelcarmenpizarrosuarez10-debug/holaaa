import sys, ezdxf, matplotlib
matplotlib.use('Agg'); import matplotlib.pyplot as plt
from ezdxf.addons.drawing import RenderContext, Frontend
from ezdxf.addons.drawing.matplotlib import MatplotlibBackend
from ezdxf.addons.drawing.config import Configuration, BackgroundPolicy, ColorPolicy
doc = ezdxf.readfile(sys.argv[1])
fig = plt.figure(); ax = fig.add_axes([0, 0, 1, 1])
cfg = Configuration(background_policy=BackgroundPolicy.WHITE, color_policy=ColorPolicy.COLOR, min_lineweight=0.12)
Frontend(RenderContext(doc), MatplotlibBackend(ax), config=cfg).draw_layout(doc.modelspace(), finalize=True)
fig.set_size_inches(33.1, 23.4)
fig.savefig(sys.argv[2], dpi=int(sys.argv[3]), facecolor='white')
