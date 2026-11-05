"""Extend the cached 315–360 E sector for possible westward return paths."""
import json
from pathlib import Path
from ...hub_footprints.terrain import fetch as inner
from ..extend import fetch as outer

if __name__=='__main__':
    records=[inner(315),outer(315)]
    Path(__file__).with_name('terrain_extension.json').write_text(json.dumps(records,indent=2)+'\n')
