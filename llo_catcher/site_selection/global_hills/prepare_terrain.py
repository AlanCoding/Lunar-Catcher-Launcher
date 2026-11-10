"""Prepare the shared final DEM band; existing valid cache is reused."""
from ..support.fetch_terrain import fetch
if __name__=='__main__':
    for west in range(0,360,45):
        fetch(west)
        print('Ready:',west)
