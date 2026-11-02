"""Freeze the selected candidate and generate publication figures/payoff arithmetic."""
from pathlib import Path
import hashlib,json,math
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from lunar_slings.hub_study.environment import LunarEnvironment
from lunar_slings.hub_study.orbit import point_surface_reference
OUT=Path(__file__).resolve().parent
SOURCE=OUT.parent/'results/split_tie/all_estimates.json'
GROUPS={
 'Heat rejection & transport':['thermal'],
 'Reel drives & mechanical assemblies':['reel_motors','reel_inverters','reel_gearboxes','reel_mechanical'],
 'Eight wheel assemblies':['wheels'],
 'Solar power':['solar'],
 'Four wheel drives':['wheel_motors','wheel_inverters','wheel_gearboxes'],
 'Four poles & joints':['poles'],
 'Tethers, sheath & end fittings':['outward_cables','main_tie','low_tie','fittings_sheath','tie_end_fittings'],
 'Steering, retention & controls':['steering','retention','controls'],
}

def save(fig,name):
 for ext in ['svg','png']:
  p=OUT/f'{name}.{ext}';fig.savefig(p,dpi=180,bbox_inches='tight')
  if ext=='svg':p.write_text('\n'.join(line.rstrip() for line in p.read_text().splitlines())+'\n')
 plt.close(fig)

def produce():
 rows=json.loads(SOURCE.read_text())
 r=next(r for r in rows if r['converged'] and r['assumptions']['name']=='reference' and r['acceleration_g']==50 and r['rover_mph']==50 and r['passes']==1)
 assert r['low_tie_used'] and r['track_radius_m']<r['road_only_radius_threshold_m']
 m=r['masses_kg'];keys=[k for ks in GROUPS.values() for k in ks]
 assert len(keys)==len(set(keys))
 assert set(keys)==set(m)-{'ballast_local','central_pivot_and_stabilizers'}
 groups={name:sum(m[k] for k in ks) for name,ks in GROUPS.items()}
 total=sum(groups.values());assert abs(total-r['imported_total_kg'])<1e-6
 physical=total+r['ballast_kg'];assert abs(physical-r['permanent_physical_total_kg'])<1e-6
 (OUT/'candidate_50g.json').write_text(json.dumps(r,indent=2)+'\n')
 plt.rcParams.update({'font.size':11,'svg.hashsalt':'lunar-publication-50g'})
 colors=['#667a8a','#cc7850','#bba270','#d9ad39','#417b95','#6c9274','#8e7ca9','#a7a7a7']
 fig,ax=plt.subplots(figsize=(11,6.3));fig.subplots_adjust(left=.02,right=.53,top=.85,bottom=.12)
 wedges,_,_=ax.pie(list(groups.values()),colors=colors,startangle=90,counterclock=False,autopct=lambda p:f'{p:.1f}%' if p>=3 else '',pctdistance=.75,wedgeprops=dict(edgecolor='white',linewidth=1.5))
 labels=[f'{name}\n{v/1000:,.1f} t  •  {100*v/total:.1f}%' for name,v in groups.items()]
 ax.legend(wedges,labels,loc='center left',bbox_to_anchor=(1.01,.5),frameon=False,labelspacing=1.0,fontsize=10)
 fig.suptitle('Imported equipment mass: 1,253 tonnes',fontsize=18,y=.96)
 fig.text(.5,.90,'50 g payload release • 50 mph rover speed • One catcher pass • 1,000 kg useful payload',ha='center',fontsize=11)
 fig.text(.5,.035,'Permanent imported launcher equipment; excludes local ballast and expendable payload/countermass.\nConcept estimate, including stated subsystem allowances; excluded infrastructure is listed in CHECKPOINT.md.',ha='center',fontsize=10)
 save(fig,'imported_mass_pie')
 fig,ax=plt.subplots(figsize=(8.3,6.4));ax.pie([total,r['ballast_kg']],labels=[f'Imported equipment\n{total/1000:,.1f} t',f'Local rock ballast\n{r["ballast_kg"]/1000:,.1f} t'],colors=['#417b95','#bba270'],autopct='%1.1f%%',startangle=90,counterclock=False,wedgeprops=dict(edgecolor='white',linewidth=2),pctdistance=.65,labeldistance=1.05)
 ax.set_title(f'Total permanent machine mass: {physical/1000:,.1f} tonnes',fontsize=15,pad=23)
 fig.text(.5,.03,'Payload and expendable countermass are excluded; local ballast is permanent.',ha='center',fontsize=10)
 save(fig,'physical_mass_pie')
 T=point_surface_reference(LunarEnvironment(),20000)['site_revisit_s'];P=1000.
 ni=math.ceil(total/P);nt=math.ceil(physical/P)
 cases=[('Continuous operation — mathematical lower bound',1.,1.,1.),('Half-time sunlight; no further downtime',.5,1.,1.),('Half-time sunlight; 80% availability; 95% success',.5,.8,.95)]
 table=[]
 for label,sun,uptime,success in cases:
  rate=sun*uptime*success
  table.append(dict(label=label,sun_fraction=sun,availability=uptime,success_fraction=success,expected_useful_kg_per_calendar_day=P*86400/T*rate,imported_equal_mass_days=ni*T/86400/rate,physical_equal_mass_days=nt*T/86400/rate))
 payoff=dict(useful_payload_kg=P,cycle_s=T,imported_mass_kg=total,physical_mass_kg=physical,successful_launches_imported=ni,successful_launches_physical=nt,cases=table,annual_half_sun_useful_kg=365.25*86400/T*.5*P)
 (OUT/'payoff.json').write_text(json.dumps(payoff,indent=2)+'\n')
 (OUT/'mass_groups.json').write_text(json.dumps(dict(groups_kg=groups,imported_total_kg=total,local_ballast_kg=r['ballast_kg'],physical_total_kg=physical),indent=2)+'\n')
 lines=['# Mass payoff: when delivered mass equals machine mass','', 'This is a **mass-throughput benchmark**, not financial payback, avoided rocket propellant, or Earth-delivered mass. Useful output means payload successfully delivered to the modeled lunar-orbit catcher. Expendable countermass receives no output credit.','', '## Inputs and definitions','', f'- Useful payload per successful launch: **{P:,.0f} kg**.',f'- Imported permanent equipment: **{total:,.0f} kg**.',f'- Total permanent mass including local ballast: **{physical:,.0f} kg**.',f'- One site-relative catcher revisit: **{T/60:.6f} minutes**.', '- Loading and timing allowances already lie inside this cycle; do not add them again.', '- Direct solar operation has no nighttime battery-storage credit.','', 'For imported equipment mass M, useful payload P and N successful launches:', '', '    Cumulative useful output = N * P', '    Imported equipment mass per cumulative useful kg = M / (N * P)', '    Successful launches to equal imported mass = ceil(M / P)', '', f'The result is **{ni:,} successful launches**. At {ni-1:,} launches, output is still below imported mass. Counting local ballast too gives **{nt:,} successful launches**, a separate physical-inventory comparison rather than an imported-equipment payoff.','', '## Calendar-time scenarios','', 'Let f be usable-sunlight fraction, u availability during sunlight, and s successful-capture fraction. With cycle duration T, the long-run useful output rate is P*f*u*s/T. The corresponding equal-mass time is approximately ceil(M/P)*T/(f*u*s). These are expected/averaged rates, not an exact event schedule.','', '| Operating assumption | Useful output t/calendar day | Imported-mass equality days | Whole-machine equality days |','| --- | ---: | ---: | ---: |']
 for d in table:lines.append(f"| {d['label']} | {d['expected_useful_kg_per_calendar_day']/1000:.2f} | {d['imported_equal_mass_days']:.1f} | {d['physical_equal_mass_days']:.1f} |")
 lines+=['', '**The 96.3-day continuous figure is not a nighttime operating claim.** With the illustrative 50% sunlight assumption, the imported-mass benchmark is approximately **193 calendar days**. The 50% value is an assumed long-run fraction, not a site-specific illumination forecast. Day/night blocks, startup phase and weather-independent operational outages change the actual crossing date.','', f'At half-time sunlight with no further downtime or failures, expected output is about **{payoff["annual_half_sun_useful_kg"]/1000:,.0f} tonnes per 365.25-day year**. The one-year equipment burden is **{total/payoff["annual_half_sun_useful_kg"]:.3f} kg of imported launcher per kg of cumulative useful output**, without replacements.','', '## Countermass, replacement and system boundary','', f'At {ni:,} successful launches with no failed attempts, the launcher handles **{ni:,} tonnes of useful payload plus {ni:,} tonnes of expendable rock countermass**. That is {2*ni:,} tonnes handled; only the useful half counts as output. Permanent ballast is separate and is not reloaded every launch. Failed attempts can consume additional feedstock.','', 'If imported replacement equipment totals M_replace over N launches, the appropriate cumulative ratio is (M_import + M_replace)/(N*P), and the payoff condition becomes N*P >= M_import + M_replace. If replacement consumption per successful launch is a constant c kg, the threshold is ceil(M_import/(P-c)), provided c<P. No replacement-life allowance is quantified yet.','', 'This study does not include imported catcher construction or momentum restoration, delivery of equipment to the lunar surface, road construction, mining/loading infrastructure, or complete release/capture mechanisms. Central pivot/stabilizer mass is excluded by instruction. The assumed launch cadence and successful capture remain operational targets, not a demonstrated duty cycle. Those additions could materially lengthen the mass payoff.','', 'The imported and whole-machine benchmarks are deliberately both shown; using local rock as if it were imported equipment would answer a different question. No literature superiority claim is made without aligning boundaries and throughput assumptions.','', '[Publication checkpoint](CHECKPOINT.md) · [Exact payoff inputs/results](payoff.json) · [Frozen candidate](candidate_50g.json)']
 (OUT/'MASS_PAYOFF.md').write_text('\n'.join(lines)+'\n')
 mass_table=['| Imported subsystem | Tonnes | Share |','| --- | ---: | ---: |']+[f'| {k} | {v/1000:,.2f} | {100*v/total:.2f}% |' for k,v in groups.items()]
 (OUT/'MASS_TABLE.md').write_text('# Imported mass composition\n\n'+'\n'.join(mass_table)+f'\n| **Total** | **{total/1000:,.2f}** | **100%** |\n\nThe source grouping assigns every imported mass item exactly once.\n')
 (OUT/'manifest.json').write_text(json.dumps(dict(source=str(SOURCE.relative_to(OUT.parent)),source_sha256=hashlib.sha256(SOURCE.read_bytes()).hexdigest(),generator_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),date='2026-11-01'),indent=2)+'\n')
 assert (ni-1)*P<total<=ni*P and (nt-1)*P<physical<=nt*P
 print(f'Publication built: {total/1000:.2f} t imported; {ni} successful launches; {table[1]["imported_equal_mass_days"]:.2f} days at half-time sunlight.')
if __name__=='__main__':produce()
