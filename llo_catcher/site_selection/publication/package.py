"""Copy approved publication assets and tabulate saved results; no new physics."""
from pathlib import Path
import shutil,json,csv,hashlib
ROOT=Path(__file__).resolve().parent
SITE=ROOT.parent
LLO=SITE.parent

def main():
    assets=ROOT/'assets';assets.mkdir(exist_ok=True);manifest=[]
    def copy(source,name):
        target=assets/name;shutil.copy2(source,target)
        manifest.append(dict(file=name,source=str(source.relative_to(LLO)),sha256=hashlib.sha256(source.read_bytes()).hexdigest()))
    figures=[(SITE/'equatorial_context/equatorial_elevation','01_equatorial_elevation'),
      (SITE/'equatorial_context/trajectory_144','02_trajectory_144'),
      (SITE/'global_hills/outcomes','03_hub_scan_east_west'),
      (SITE/'launch_ridges/catalog/equator_strips','10_equatorial_ridges'),
      (SITE/'radial_terrain/selected_hill_terrain','11_selected_hill_terrain')]
    for i in range(1,5):
        figures.append((SITE/f'launch_ridges/expanded/P{i}_ridge_match',f'07_P{i}_terrain'))
    ids=['H0333','H4765','H6308','H6941']
    for i,h in enumerate(ids,1):figures.append((SITE/f'featured_four/adjusted_hilltops/maps/P{i}_{h}_hilltop_15km',f'07_alternative_P{i}_sling_footprint'))
    for source,stem in figures:
        for ext in ['png','svg']:copy(source.with_suffix('.'+ext),stem+'.'+ext)
    radial=json.loads((SITE/'radial_terrain/results.json').read_text())
    copy(SITE/f"radial_terrain/{radial['selected_site']}_profile.csv",'11_selected_hill_terrain.csv')
    copy(SITE/'featured_four/adjusted_hilltops/publication_sites.csv','05_four_hills.csv')
    copy(SITE/'launch_ridges/catalog/featured_hubs.csv','09_hilltop_ridges.csv')
    copy(SITE/'launch_ridges/catalog/ridges.csv','08_ridge_catalog.csv')
    raw=json.loads((SITE/'global_hills/results.json').read_text())
    stats=json.loads((SITE/'global_hills/nonoverlap_results.json').read_text())['stats']
    selection=json.loads((SITE/'featured_four/results.json').read_text())['counts']
    catalog=json.loads((SITE/'launch_ridges/catalog/ridges.json').read_text())
    expanded=json.loads((SITE/'launch_ridges/expanded/results.json').read_text())
    stages=[('Native-grid local peaks examined in the hub search bands',sum(r['native_local_peaks'] for r in raw['sectors'])),('Candidate peaks with terrain-clear tip circles',raw['all_peaks_stats']['count']),('Selected hubs with non-overlapping sweep disks',stats['count']),('Selected hubs clearing eastward',stats['east_clear']),('East-clear hubs with reference-arm equator offset ≤100 m',selection['aligned']),('Also meeting minimum tip-circle clearance ≥100 m',selection['clearance_qualified']),('Featured hubs selected for regional diversity',4)]
    text=['# Hub search and down-selection','','| Stage | Locations |','|---|---:|']+[f'| {a} | {b:,} |' for a,b in stages]
    text+=['','The final four were subsequently moved onto their nearby summits and their flight paths rechecked. The featured-hill table reports those adjusted positions. The 695-hub plot and population counts retain the original global-search placements.','',
      '| Outcome among the 695 selected hubs | Hubs |','|---|---:|','| Eastward clears only | 39 |','| Westward clears only | 39 |','| Both directions clear | 3 |','| Both directions hit terrain before the catcher | 614 |','| Total | 695 |','',
      'Each panel in the scan figure shows the same 695 hubs: 42 green and 653 red. Green denotes terrain clearance to the catcher in the panel’s direction. There are 81 distinct hubs clearing at least one direction.','']
    (assets/'04_hub_scan_tables.md').write_text('\n'.join(text))
    publication=(SITE/'featured_four/adjusted_hilltops/PUBLICATION.md').read_text();start=publication.index('| Site | Hub latitude');end=publication.index('\n\n',start)
    (assets/'05_four_hills.md').write_text('# Four featured hilltops\n\n'+publication[start:end]+'\n\nCoordinates are signed decimal degrees, north/east positive. Elevation is above the lunar reference sphere. Tip offset is signed north-positive. Tip clearance is the minimum around the rotating circumference. Westward clearance checks cover the outbound trajectory to first 25 km apoapsis, with horizontal release at the actual tip latitude.\n')
    downstream=sum(r['extra_release_height_m']>.1 and r['contact_anomaly_deg']>.05 for r in expanded['rows'])
    named=sum(r['samples'] for r in catalog['ridges'])
    text=['# Ridge search accounting','','| Stage | Count | Unit |','|---|---:|---|',
      f"| Starting locations across four regional windows | {len(expanded['rows']):,} | Seed trajectories |",
      f'| Qualifying downstream terrain contacts | {downstream:,} | Contact samples, including repeat discoveries |',
      f'| Samples belonging to named connected segments | {named:,} | Contact samples |',
      f"| Samples left isolated or with insufficient trace | {catalog['unnamed_contact_samples']:,} | Contact samples |",
      f"| Named ridge segments after grouping | {len(catalog['ridges'])} | Connected segments |",
      '| Named segments associated with the featured hilltops | 4 | Connected segments |','',
      'Every seed also received a fresh-launch height calculation at its limiting contact. The 3,354 qualifying downstream samples split into 3,335 samples in named segments and 19 remaining samples. The 84 figure counts connected segments; multiple samples contribute to each segment.','',
      'Seeds span four 12° longitude windows at 1.5° spacing and ±6 km north/south at 125 m spacing, with the hub and intended-release latitudes added. Contacts are connected using the catalog’s documented distance and adjacency rules. Finite coverage and spacing can miss qualifying ridges and narrow branches.','']
    (assets/'08_ridge_scan_table.md').write_text('\n'.join(text))
    text=['# Featured hilltops and their ridges','','| Hilltop | Hub latitude | Hub longitude | Ridge |','|---|---:|---:|---|']
    for r in catalog['featured_hubs']:text.append(f"| {r['site']} | {r['hub_latitude_deg']:+.8f} | {r['hub_longitude_deg']:+.8f} | {r['ridge']} |")
    (assets/'09_hilltop_ridges.md').write_text('\n'.join(text)+'\n')
    lowered_path=SITE/'radial_terrain/lowered_release.json'
    if lowered_path.exists():
        lowered=json.loads(lowered_path.read_text())
        copy(SITE/'radial_terrain/lowered_release.csv','12_lowered_release.csv')
        text=['# Closing example: P1 releases below the summit tangent plane','','| Release case | Height relative to hub tangent plane (m) | Minimum outbound clearance (m) | Eastward clears? |','|---|---:|---:|:---:|']
        for r in lowered['cases']:
            text.append(f"| {r['case']} | {r['tip_plane_offset_m']:+.2f} | {r['minimum_outbound_clearance_m']:.1f} | {'Yes' if r['eastward_clears'] else 'No'} |")
        text += ['', 'P1 retains its 5.716 km arm radius. Shots are horizontal and eastward, with speed adjusted to reach a 25 km apoapsis. The published reference apex height is 28.68 m; subtracting it from the existing endpoint height gives −27.30 m relative to the hub tangent plane. The model uses spherical gravity, lunar rotation and the existing terrain data. Tether-shape and support sizing are a separate design step.','']
        (assets/'12_lowered_release.md').write_text('\n'.join(text))
    # Include prose tables in the integrity manifest as locally assembled artifacts.
    for path in sorted(assets.glob('*.md')):manifest.append(dict(file=path.name,source='Compiled from saved results by publication/package.py',sha256=hashlib.sha256(path.read_bytes()).hexdigest()))
    (ROOT/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    print('Packaged',len(manifest),'files; no numerical models rerun.')
if __name__=='__main__':main()
