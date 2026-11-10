"""Regenerate only the four selected terrain maps, without impact overlays."""
from pathlib import Path
from ...analysis.single_equatorial_release.directional_sites import build_maps as renderer
from ..global_hills.search import GlobalTerrain
if __name__=='__main__':
    renderer.ROOT=Path(__file__).parent/'maps';renderer.ROOT.mkdir(exist_ok=True)
    renderer.Terrain=lambda *args,**kwargs:GlobalTerrain()
    renderer.main()
