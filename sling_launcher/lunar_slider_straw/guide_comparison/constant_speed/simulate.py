"""Matched constant-cruise free-cable extension/retraction using the existing ALE dynamics."""
from pathlib import Path
import argparse
import numpy as np
from sling_launcher.spooled_tether_2d.model import Tether,Config
from sling_launcher.spooled_tether_2d import run as runner
from sling_launcher.staged_spool_bank.model import Model,Case
P=Path(__file__).parent
base=Model(Case());SPEED=base.L/(base.c.period_s/2);RAMP=30.;SEED=500.;DURATION=(base.L-SEED)/SPEED+RAMP
class ConstantTether(Tether):
 def motion(self,t,phase):
  if phase not in ['extend','retract']:return super().motion(t,phase)
  t=np.clip(t,0,self.c.travel_s);D=self.c.travel_s;u=SPEED;b=RAMP
  if t<b:
   q=u*(t-b/np.pi*np.sin(np.pi*t/b))/2;v=u*(1-np.cos(np.pi*t/b))/2;acc=u*np.pi*np.sin(np.pi*t/b)/(2*b)
  elif t<=D-b:q=u*(t-b/2);v=u;acc=0.
  else:
   z=t-(D-b);q=u*(D-1.5*b)+u*(z+b/np.pi*np.sin(np.pi*z/b))/2;v=u*(1+np.cos(np.pi*z/b))/2;acc=-u*np.pi*np.sin(np.pi*z/b)/(2*b)
  if phase=='retract':return self.L-q,-v,-acc
  return self.c.initial_length+q,v,acc
 def metadata(self):
  d=super().metadata();d.update(cruise_speed_m_s=SPEED,ramp_duration_s=RAMP,modeled_seed_length_m=SEED,full_length_reference_travel_s=base.c.period_s/2);return d
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--nodes',type=int,default=32);p.add_argument('--damping',type=float,default=.02);a=p.parse_args()
 runner.OUT=P;runner.Tether=ConstantTether
 c=Config(name='constant_speed' if a.damping==.02 else 'constant_speed_damping',nodes=a.nodes,target_tether_payload_ratio=3.,initial_length=SEED,travel_s=DURATION,payout_profile='constant_cruise',axial_relaxation_s=a.damping)
 runner.run(c)
