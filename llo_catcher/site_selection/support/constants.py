"""Physical constants and the published endpoint-height convention."""
from pathlib import Path
import json
import numpy as np
RADIUS=1737400.
MU=4.902800118e12
MOON_OMEGA=2*np.pi/(655.720*3600)
REFERENCE=Path(__file__).resolve().parents[3]/'sling_launcher/blender/scene_inputs.json'
TIP_HEIGHT=float(json.loads(REFERENCE.read_text())['outward_points_m'][-1][2])
EXTRA_MARGIN=0.5
PLANE_OFFSET=TIP_HEIGHT+EXTRA_MARGIN
