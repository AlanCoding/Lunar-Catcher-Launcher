"""Fetch only missing public summit-band strips; preserves source byte hashes."""
from ...analysis.single_equatorial_release.hub_footprints.terrain import fetch as inner
from ...analysis.single_equatorial_release.summit_sites.extend import fetch as outer,CACHE
if __name__=='__main__':
    for west in range(0,360,45):
        if not (CACHE/f'{west:03d}.npy').exists():inner(west)
        outer(west)
        print('Ready:',west)
