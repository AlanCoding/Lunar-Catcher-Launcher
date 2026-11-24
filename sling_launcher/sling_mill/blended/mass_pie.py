"""Publication pie chart from the optimized iron reference."""
from pathlib import Path
import json
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
P=Path(__file__).parent
r=json.loads((P/'search_results/iron_reference.json').read_text());m=r['masses']
groups={
'Solar array':m.get('solar_array',0.),
'Support frames':m['frames'],
'Motors and installation':m['motors'],
'Foundations':m['foundations'],
'Power electronics / cabling':m['power_electronics'],
'Guides':m['guides'],
'Motor radiators':m['motor_radiators'],
'Belts, cables and contact layers':sum(m[k] for k in ['structural_belts','radial_members','torque_members','contact_layers']),
'Hubs, bearings and startup supports':sum(m[k] for k in ['hubs','bearings','startup_supports'])}
assert abs(sum(groups.values())-sum(m.values()))<1e-6
plt.rcParams.update({'svg.fonttype':'none','font.family':'DejaVu Sans'})
fig,ax=plt.subplots(figsize=(11,6.2));fig.subplots_adjust(left=.01,right=.58,bottom=.08,top=.86)
colors=['#b59b59','#49677e','#426e60','#c9bb98','#a25c43','#839f99','#9ba8b4','#b5ad99','#d4d8d0']
wedges,_,_=ax.pie(groups.values(),colors=colors,startangle=100,counterclock=False,
    autopct=lambda p:f'{p:.1f}%' if p>8 else '',pctdistance=.7,
    textprops={'color':'white','fontsize':15,'weight':'bold'},wedgeprops={'edgecolor':'white','linewidth':1.5})
total=sum(groups.values())
labels=[f'{k}\n{v/1000:,.1f} t  ·  {100*v/total:.2f}%' for k,v in groups.items()]
for i,((name,value),color) in enumerate(zip(groups.items(),colors)):
    y=.83-i*.081
    fig.add_artist(Rectangle((.585,y-.006),.022,.012,transform=fig.transFigure,facecolor=color,edgecolor='white'))
    fig.text(.62,y,name,fontsize=10,va='center',ha='left')
    fig.text(.62,y-.029,f'{value/1000:,.1f} t  ·  {100*value/total:.2f}%',fontsize=10,va='center',ha='left')
fig.text(.055,.94,'Sling mill: where the mass goes',fontsize=20,weight='bold',color='#426e60')
for suffix in ['svg','png']:fig.savefig(P.parent/'figures'/f'06_machine_mass_pie.{suffix}',dpi=170,facecolor='white')
plt.close(fig)
print('Pie totals match optimized inventory:',total)
