"""Linear inventory equivalents for an explicit 10 Mt/year useful-delivery target."""
from pathlib import Path
import json
P=Path(__file__).parent/'results/reference'
def main():
 s=json.loads((P/'summary.json').read_text());annual=s['schedule']['useful_LLO_kg_s']*365*86400*.5;rows=[]
 for label,delivery in [('Useful caught at LLO',annual),('Useful shielding delivered to L1',s['payback']['annual_L1_kg_at50pct'])]:
  k=1e10/delivery
  rows.append(dict(target=label,reference_equivalents=k,working_tether_tonnes=k*144,guide_tonnes=k*6,imported_specialized_equipment_proxy_tonnes=k*s['totals']['assumed_imported_kg']/1000,fabricated_tonnes=k*s['totals']['fabricated_kg']/1000,discarded_countermass_tonnes_per_year=k*annual/1000,operating_supply_GW=k*s['battery']['constant_source_W']/1e9))
 (P/'scale_10million.json').write_text(json.dumps(rows,indent=2)+'\n')
if __name__=='__main__':main()
