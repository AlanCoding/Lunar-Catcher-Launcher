"""Architecture-level flow and cable-inventory budget; no whole-machine mass scaling."""
from pathlib import Path
import json,math
P=Path(__file__).parent
s=json.loads((P.parent/'lunar_slider_straw/results/reference/summary.json').read_text())
T=s['schedule']['stroke_s']*2;year=365*86400;target=1e10;v=1684.523
a0=s['schedule']['useful_LLO_kg_s']*year*.5
rows=[]
for name,directions,duty,windows in [('Early site',1,.5,1),('Both directions captured',2,.5,1),('Continuous power',2,1,1),('Two catcher pairs',2,1,2)]:
 flow=8000/T*directions*duty*windows
 rows.append(dict(scenario=name,productive_directions=directions,duty=duty,windows_per_period=windows,annual_tonnes_at_1t_payload=flow*year/1000,required_payload_tonnes=target/year/flow,gain_vs_early=flow*year/a0))
# Every catcher window collects eight mirrored exchanges: eight loads per direction.
C=T/2;delta=C/8;payload=target/year*C/16
schedules=[]
for name,D in [('Faster exchange',T/4),('More simultaneous exchanges',T/2)]:
 active=round(D/delta);hold=C;groups=active+8;modules=2*groups;lines=4*groups
 # Check every window receives eight jobs and each completed group waits through capture.
 jobs=[]
 for n in range(-100,150):
  start=n*delta;end=start+D;capture=math.ceil(end/C-1e-10)*C;reuse=start+groups*delta
  assert reuse>=capture-1e-7 and reuse-end>=300
  jobs.append((start,end,capture,reuse))
 for k in range(1,10):assert sum(abs(j[2]-k*C)<1e-6 for j in jobs)==8
 schedules.append(dict(name=name,exchange_minutes=D/60,hold_minutes=hold/60,active_mirrored_groups=active,groups=groups,modules=modules,tethers=lines,loaded_outgoing_per_side=active,empty_incoming_per_side=active,working_fiber_tonnes=lines*3*payload/1000,guide_fiber_tonnes=2*3*payload/1000,total_fiber_tonnes=(lines+2)*3*payload/1000,full_tether_cycle_hours=2*(D+hold)/3600,mean_payout_m_s=(5787.088393934127-76.78937039996255)/D))
result=dict(target_tonnes_per_year=1e7,target='Useful caught mass summed across prograde and retrograde LLO catchers',catcher_period_s=T,catch_window_s=C,flow_kg_s=target/year,combined_batch_tonnes=target/year*C/1000,batch_per_direction_tonnes=target/year*C/2000,payload_tonnes=payload/1000,working_tether_tonnes_each=3*payload/1000,root_rope_diameter_m=.030266*math.sqrt(payload/1000),peak_line_tension_MN=1.140025*payload/1000,ideal_payload_power_MW=target/year*v*v/2/1e6,conditional_electrical_MW=s['battery']['constant_source_W']*(payload/1000)*2/1e6,architecture_steps=rows,schedules=schedules,L1_multiplier=1/0.71551)
(P/'results.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
