"""Deterministic Phase 2 simulation; rendering never changes game rules."""
import json
import math
import random
from pathlib import Path

T = json.loads((Path(__file__).resolve().parents[1] / 'game.contract.json').read_text(encoding='utf-8'))['tuning']
HZ = 60


def d(a, b): return math.hypot(a[0] - b[0], a[2] - b[2])


def vec(v):
    if not isinstance(v, list) or len(v) != 3 or any(type(x) not in (int, float) or not math.isfinite(x) for x in v):
        raise ValueError('expected finite [x,y,z]')
    return [float(x) for x in v]


def pt(cx, cz, r, deg, y=0):
    a = math.radians(deg)
    return [round(cx + r * math.cos(a), 3), float(y), round(cz + r * math.sin(a), 3)]


def norm(x, z):
    a = math.hypot(x, z)
    return (x / a, z / a) if a else (1.0, 0.0)


def map_for(n):
    if n == 1:
        return ([[0,0,25],[23.8,0,7.7],[14.7,0,-20.2],[-14.7,0,-20.2],[-23.8,0,7.7]],
                [pt(0,0,12,i*45) for i in range(8)]+[pt(0,0,33,i*22.5) for i in range(16)],
                [pt(0,0,37,15+i*30) for i in range(12)], [], 40)
    if n == 2:
        return ([[0,0,20],[17,0,-10],[-17,0,-10],[70,0,20],[87,0,-10],[53,0,-10]],
                [pt(c,0,10,i*90) for c in (0,70) for i in range(4)]+[pt(c,0,22,i*45) for c in (0,70) for i in range(8)],
                [pt(c,0,26,22.5+i*45) for c in (0,70) for i in range(8)], [[35,0,0]], 28)
    return ([[0,6,6],[18,3,10],[-18,3,10],[35,0,-10],[-35,0,-10],[20,0,-35],[-20,0,-35]],
            [pt(0,0,34,i*20) for i in range(18)]+[pt(0,0,18,20+i*20,3) for i in range(8)]+[pt(0,0,5,45+i*90,6) for i in range(4)],
            [pt(0,0,43,i*22.5) for i in range(16)], [[30,0,25],[-30,0,25]], 45)


def obstacles_for(n):
    # (x, z, radius); mirrored by the WebGL scene. Keep spawn, objectives and launch pads clear.
    if n==1: return [(-9,14,1.4),(9,19,1.2),(-20,-5,1.6),(20,-8,1.5),(4,-25,1.3)]
    if n==2: return [(-12,8,1.4),(10,-14,1.5),(62,12,1.4),(80,-15,1.5),(35,4,1.0)]
    return [(-30,-8,1.5),(29,-7,1.5),(-18,-29,1.8),(19,-29,1.8),(31,12,1.2),(-31,12,1.2)]


class Game:
    def __init__(self, seed=0, scenario=None, night=1):
        if night not in (1,2,3): raise ValueError('night must be 1, 2, or 3')
        if scenario is None: scenario = {}
        if not isinstance(scenario, dict): raise ValueError('scenario must be object')
        self.night, self.rng = night, random.Random(seed)
        self.tick = self.sim_tick = 0
        self.state, self.score, self.events = 'playing', 0, []
        self.duration = [0,T['night1_duration_s'],T['night2_duration_s'],T['night3_duration_s']][night]
        self.successful_lights=0
        self.player = {'pos':[0.,6.,5.] if night==3 else [0.,0.,0.], 'vel':[0.,0.,0.], 'flames':3, 'carried':0}
        self.invuln = self.dash_cd = self.dash_left = self.pulse_cd = self.charm_ticks = self.fall_wait = 0
        self.facing = self.dash_dir = (0.,1.)
        self.launch = None
        self.wind_enabled = True
        self.wind = {'active':False,'dir_deg':None}
        self.wind_dir = 0
        self.random_motes = self.random_shades = self.random_drifters = True
        lanterns, self.mote_points, self.shade_points, charms, self.radius = map_for(night)
        self.lanterns = [{'id':f'L{i+1}','pos':vec(p),'lit':False,'deposited':0,'fuel_u':0,'ever_lit':False,'relit_count':0} for i,p in enumerate(lanterns)]
        self.obstacles=obstacles_for(night)
        self.motes = [self.mote(f'M{i+1}',p) for i,p in enumerate(self.mote_points[:20])]
        self.next_mote = len(self.motes)+1
        self.shades, self.drifters = [], []
        self.next_shade = self.next_drifter = 1
        self.charms = [{'id':f'C{i+1}','pos':vec(p),'available':True,'respawn':0} for i,p in enumerate(charms)]
        self.apply_scenario(scenario)

    def mote(self, id, p, kind='random', ttl=None, born=0):
        return {'id':id,'pos':vec(p),'kind':kind,'ttl':ttl,'born':born}

    def apply_scenario(self,s):
        if set(s)-{'player','random_motes','random_shades','random_drifters','motes','shades','drifters','charms','lanterns','time_left_s','wind_enabled'}: raise ValueError('unknown scenario field')
        if 'player' in s:
            p=s['player']
            if not isinstance(p,dict) or set(p)-{'pos','vel','carried','flames','invuln_ticks','dash_cd_ticks','pulse_cd_ticks','charm_ticks','successful_lights'}: raise ValueError('invalid player')
            for k in ('pos','vel'):
                if k in p: self.player[k]=vec(p[k])
            for k in ('carried','flames'):
                if k in p:
                    if type(p[k]) is not int or p[k]<0: raise ValueError('invalid player value')
                    self.player[k]=p[k]
            if 'successful_lights' in p: self.successful_lights=int(p['successful_lights'])
            for k,a in (('invuln_ticks','invuln'),('dash_cd_ticks','dash_cd'),('pulse_cd_ticks','pulse_cd'),('charm_ticks','charm_ticks')):
                if k in p:
                    if type(p[k]) is not int or p[k]<0: raise ValueError('invalid timer')
                    setattr(self,a,p[k])
        for k in ('random_motes','random_shades','random_drifters','wind_enabled'):
            if k in s:
                if type(s[k]) is not bool: raise ValueError('invalid flag')
                setattr(self,k,s[k])
        if s.get('random_motes') is False and 'motes' not in s: self.motes=[]
        if 'motes' in s:
            if not isinstance(s['motes'],list): raise ValueError('invalid motes')
            self.motes=[self.mote(f'M{i+1}',p) for i,p in enumerate(s['motes'])]
            self.next_mote=len(self.motes)+1
        if 'shades' in s:
            if not isinstance(s['shades'],list): raise ValueError('invalid shades')
            self.shades=[]
            for i,sh in enumerate(s['shades']):
                if not isinstance(sh,dict) or set(sh)-{'id','pos','state','state_ticks_left'} or 'pos' not in sh: raise ValueError('invalid shade')
                state=sh.get('state','chase')
                if state not in ('spawning','wander','chase','recoil','stunned'): raise ValueError('invalid shade state')
                self.shades.append({'id':sh.get('id',f'S{i+1}'),'pos':vec(sh['pos']),'state':state,'timer':sh.get('state_ticks_left',0),'push':(1.,0.),'safe_exit':0})
            self.next_shade=len(self.shades)+1
        if 'drifters' in s:
            if not isinstance(s['drifters'],list): raise ValueError('invalid drifters')
            self.drifters=[]
            for i,dr in enumerate(s['drifters']):
                if not isinstance(dr,dict) or set(dr)-{'id','pos','state','stolen','state_ticks_left'} or 'pos' not in dr: raise ValueError('invalid drifter')
                state=dr.get('state','idle')
                if state not in ('idle','chase','flee','removed'): raise ValueError('invalid drifter state')
                self.drifters.append({'id':dr.get('id',f'D{i+1}'),'pos':vec(dr['pos']),'state':state,'stolen':dr.get('stolen',0),'timer':dr.get('state_ticks_left',0)})
            self.next_drifter=len(self.drifters)+1
        if 'charms' in s:
            if not isinstance(s['charms'],list): raise ValueError('invalid charms')
            self.charms=[]
            for i,c in enumerate(s['charms']):
                if not isinstance(c,dict) or set(c)-{'id','pos','available','respawn_ticks'} or 'pos' not in c: raise ValueError('invalid charm')
                self.charms.append({'id':c.get('id',f'C{i+1}'),'pos':vec(c['pos']),'available':c.get('available',True),'respawn':c.get('respawn_ticks',0)})
        if 'lanterns' in s:
            if not isinstance(s['lanterns'],list): raise ValueError('invalid lanterns')
            seen=set()
            for q in s['lanterns']:
                if not isinstance(q,dict) or set(q)-{'id','pos','lit','deposited','fuel','ever_lit'} or q.get('id') not in {l['id'] for l in self.lanterns} or q['id'] in seen: raise ValueError('invalid lantern')
                seen.add(q['id'])
                l=next(l for l in self.lanterns if l['id']==q['id'])
                if 'pos' in q: l['pos']=vec(q['pos'])
                if 'lit' in q:
                    if type(q['lit']) is not bool: raise ValueError('invalid lit')
                    l['lit']=q['lit']
                    l['fuel_u']=6000 if q['lit'] and 'fuel' not in q else 0
                if 'fuel' in q:
                    if type(q['fuel']) not in (int,float) or not math.isfinite(q['fuel']) or not 0<=q['fuel']<=100: raise ValueError('invalid fuel')
                    l['fuel_u']=round(q['fuel']*60)
                    l['lit']=l['fuel_u']>0
                if 'ever_lit' in q: l['ever_lit']=bool(q['ever_lit'])
                if l['lit']: l['ever_lit']=True
                if 'deposited' in q:
                    if type(q['deposited']) is not int or q['deposited']<0: raise ValueError('invalid deposited')
                    l['deposited']=q['deposited']
        if 'time_left_s' in s:
            v=s['time_left_s']
            if type(v) not in (int,float) or not math.isfinite(v) or v<0: raise ValueError('invalid time')
            self.duration=float(v)

    def emit(self,name,data): self.events.append({'type':'event','tick':self.tick,'name':name,'data':data})
    def time_left(self): return max(0.,self.duration-self.sim_tick/HZ)

    def ground(self,x,z,y=0):
        if self.night==1: return 0. if math.hypot(x,z)<=40 else None
        if self.night==2:
            return 0. if math.hypot(x,z)<=28 or math.hypot(x-70,z)<=28 or (26<=x<=44 and -2<=z<=2) else None
        r=math.hypot(x,z)
        if r>45: return None
        if r<=8 and y>=5.8: return 6.
        if 12<=r<=24 and z>0 and y>=2.8: return 3.
        for deg in (30,150):
            a=math.radians(deg); along=x*math.cos(a)+z*math.sin(a); across=-x*math.sin(a)+z*math.cos(a)
            if 24<=along<=30 and abs(across)<=1.5: return (30-along)/2
        return 0.

    def elevated_surface(self,x,z):
        if self.night!=3: return 0.
        r=math.hypot(x,z)
        if r<=8: return 6.
        if 12<=r<=24 and z>0: return 3.
        for deg in (30,150):
            a=math.radians(deg); along=x*math.cos(a)+z*math.sin(a); across=-x*math.sin(a)+z*math.cos(a)
            if 24<=along<=30 and abs(across)<=1.5: return (30-along)/2
        return 0.

    def obstacle_at(self,x,z):
        return any(math.hypot(x-ox,z-oz)<radius+.45 for ox,oz,radius in self.obstacles)

    def drop(self,count,where):
        for _ in range(count):
            a=self.rng.random()*math.tau; r=1.5+self.rng.random()
            self.motes.append(self.mote(f'M{self.next_mote}',[where[0]+r*math.cos(a),where[1],where[2]+r*math.sin(a)],'dropped',480,self.sim_tick))
            self.next_mote+=1

    def finish(self,state,reason):
        if self.state not in ('playing','paused'): return
        self.state=state
        if state=='won': self.score+=sum(50+int(l['fuel_u']//60) for l in self.lanterns if l['lit'])+self.player['flames']*50
        self.emit('game_over',{'result':state,'reason':reason})

    def step(self,controls,edges):
        if self.state in ('won','lost'): return
        self.events=[]; self.tick+=1
        if edges.get('pause'):
            self.state='playing' if self.state=='paused' else 'paused'
            self.emit('resumed' if self.state=='playing' else 'paused',{})
            return
        if self.state=='paused': return
        self.sim_tick+=1; t=self.sim_tick; p=self.player
        for k in ('invuln','dash_cd','pulse_cd','charm_ticks'): setattr(self,k,max(0,getattr(self,k)-1))
        for c in self.charms:
            if not c['available']:
                c['respawn']=max(0,c['respawn']-1)
                if not c['respawn']: c['available']=True
        self.motes=[m for m in self.motes if m['ttl'] is None or m['ttl']>1]
        for m in self.motes:
            if m['ttl'] is not None: m['ttl']-=1
        for l in self.lanterns:
            if l['lit']:
                l['fuel_u']=max(0,l['fuel_u']-1)
                if l['fuel_u']==0:
                    l['lit']=False; l['deposited']=0
                    self.emit('lantern_out',{'lantern_id':l['id']})
        for sh in self.shades:
            if sh['state']=='drain' and sh.get('target_lantern_id'):
                l=next((q for q in self.lanterns if q['id']==sh['target_lantern_id']),None)
                if l and l['lit']:
                    l['fuel_u']=max(0,l['fuel_u']-5)
                    if t%60==0:self.emit('fuel_drain',{'lantern_id':l['id'],'shade_id':sh['id'],'fuel':round(l['fuel_u']/60,1)})
                    if l['fuel_u']==0:
                        l['lit']=False;l['deposited']=0;self.emit('lantern_out',{'lantern_id':l['id']})
        if self.fall_wait:
            self.fall_wait-=1
            if not self.fall_wait:
                p['pos']=[0.,0.,0.]; p['vel']=[0.,0.,0.]; self.invuln=90
            self.spawn_finish(); return
        move=controls.get('move',[0,0]); yaw=math.radians(controls.get('cam_yaw_deg',0))
        dx=move[0]*math.cos(yaw)+move[1]*math.sin(yaw)
        dz=-move[0]*math.sin(yaw)+move[1]*math.cos(yaw)
        mag=math.hypot(dx,dz)
        if mag>1: dx/=mag; dz/=mag
        if mag: self.facing=norm(dx,dz)
        old_ground=self.ground(p['pos'][0],p['pos'][2],p['pos'][1])
        grounded=old_ground is not None and p['pos'][1]<=old_ground+1e-6 and p['vel'][1]<=0
        if edges.get('jump') and grounded: p['vel'][1]=7.; grounded=False
        if edges.get('dash') and not self.dash_left and (not self.dash_cd or self.charm_ticks):
            self.dash_left=12; self.dash_cd=90; self.dash_dir=self.facing; self.emit('dash',{})
        if self.night==3 and self.wind_enabled:
            phase=t%1800
            if phase==0: self.wind_dir=self.rng.randrange(360)
            self.wind={'active':t>=1800 and phase<300,'dir_deg':self.wind_dir if t>=1800 else None}
        else: self.wind={'active':False,'dir_deg':None}
        if grounded and self.launch is None:
            if self.night==2:
                for pad,dest in (([20,0,18],[70,0,0]),([50,0,-18],[0,0,0])):
                    if d(p['pos'],pad)<=T['jump_pad_radius']:
                        ux,uz=norm(dest[0]-pad[0],dest[2]-pad[2]); self.launch=(24*ux,24*uz); p['vel'][1]=14.; grounded=False; break
            if self.night==3 and d(p['pos'],[0,3,13])<=T['jump_pad_radius'] and abs(p['pos'][1]-3)<.2:
                self.launch=(0.,-8.); p['vel'][1]=12.; grounded=False
        dashing=bool(self.dash_left)
        if dashing:
            vx,vz=self.dash_dir[0]*14,self.dash_dir[1]*14; self.dash_left-=1
        elif self.launch is not None: vx,vz=self.launch
        else:
            speed=7.2 if self.charm_ticks else 6.
            vx,vz=dx*speed,dz*speed
        if self.wind['active']:
            vx+=2*math.cos(math.radians(self.wind_dir)); vz+=2*math.sin(math.radians(self.wind_dir))
        nx,nz=p['pos'][0]+vx/HZ,p['pos'][2]+vz/HZ
        if self.obstacle_at(nx,nz): nx,nz=p['pos'][0],p['pos'][2]
        if self.night==3 and math.hypot(nx,nz)<2 and p['pos'][1]<8.5:
            radius=math.hypot(p['pos'][0],p['pos'][2])
            if radius<2:
                ux,uz=norm(p['pos'][0],p['pos'][2]); p['pos'][0],p['pos'][2]=ux*2.05,uz*2.05
            nx,nz=p['pos'][0],p['pos'][2]
        # Elevated tiers are solid vertical walls from below. Access them via the ramps/jump pad,
        # while stepping off their edges still lets the player fall to a lower floor.
        next_floor=self.elevated_surface(nx,nz)
        on_ramp=any(24<=nx*math.cos(math.radians(deg))+nz*math.sin(math.radians(deg))<=30 and abs(-nx*math.sin(math.radians(deg))+nz*math.cos(math.radians(deg)))<=1.5 for deg in (30,150))
        if self.night==3 and grounded and next_floor>p['pos'][1]+.05 and not on_ramp:
            nx,nz=p['pos'][0],p['pos'][2]
        p['pos'][0],p['pos'][2]=nx,nz; p['vel'][0],p['vel'][2]=vx,vz
        floor=self.ground(nx,nz,p['pos'][1])
        if floor is None: grounded=False
        if (not grounded or p['vel'][1]>0) and not dashing:
            p['vel'][1]-=20/HZ; p['pos'][1]+=p['vel'][1]/HZ
        floor=self.ground(nx,nz,p['pos'][1])
        if floor is not None and p['vel'][1]<=0 and p['pos'][1]<=floor and (old_ground is not None or self.launch is not None):
            p['pos'][1]=floor; p['vel'][1]=0.; self.launch=None
        if p['pos'][1]<-10:
            lost=p['carried']; p['carried']=0; p['flames']-=1
            self.emit('player_hit',{'by':'fall','flames':p['flames'],'dropped':0,'lost':lost})
            if p['flames']>0: self.fall_wait=60
            self.spawn_finish(); return
        for m in list(self.motes):
            if m['born']<t and p['carried']<self.capacity() and d(p['pos'],m['pos'])<=1+1e-9 and abs(p['pos'][1]-m['pos'][1])<=1.5:
                self.motes.remove(m); p['carried']+=1; self.emit('mote_picked',{'carried':p['carried']})
        for c in self.charms:
            if c['available'] and d(p['pos'],c['pos'])<=1 and abs(p['pos'][1]-c['pos'][1])<=1.5:
                c['available']=False; c['respawn']=2700; self.charm_ticks=600
                self.emit('charm_picked',{'charm_id':c['id'],'charm_ticks':600})
        if edges.get('interact'):
            options=[l for l in self.lanterns if ((not l['lit']) or l['fuel_u']<6000) and d(p['pos'],l['pos'])<=2+1e-9 and abs(p['pos'][1]-l['pos'][1])<=1.5]
            if options:
                l=min(options,key=lambda x:(d(p['pos'],x['pos']),x['id']))
                if l['lit']:
                    used=min(p['carried'],math.ceil((6000-l['fuel_u'])/600))
                    if used:
                        old=l['fuel_u'];p['carried']-=used;l['fuel_u']=min(6000,l['fuel_u']+used*600);self.score+=used*5
                        self.emit('refuel',{'lantern_id':l['id'],'amount':used,'fuel':round(l['fuel_u']/60,1)})
                        if old<1800<=l['fuel_u']:
                            for sh in self.shades:
                                if d(sh['pos'],l['pos'])<6:sh['safe_exit']=30
                            for sh in self.shades:
                                if sh['state']=='drain' and sh.get('target_lantern_id')==l['id']:sh['state']='wander'
                else:
                    cost=5 if l['ever_lit'] else 10
                    amount=min(p['carried'],max(0,cost-l['deposited']))
                    if amount:
                        p['carried']-=amount;l['deposited']+=amount;self.score+=amount*5
                        self.emit('deposit',{'lantern_id':l['id'],'amount':amount,'deposited':l['deposited']})
                    if l['deposited']>=cost:
                        relight=l['ever_lit'];l['lit']=True;l['ever_lit']=True;l['fuel_u']=6000;l['deposited']=0
                        self.successful_lights+=1;self.score+=40 if relight else 100
                        self.emit('lantern_lit',{'lantern_id':l['id'],'relight':relight})
                        for sh in self.shades:
                            if d(sh['pos'],l['pos'])<6:sh['safe_exit']=30
                        for sh in self.shades:
                            if sh['state']=='drain' and sh.get('target_lantern_id')==l['id']:sh['state']='wander'
        if edges.get('pulse') and p['carried']>=3 and not self.pulse_cd:
            p['carried']-=3; self.pulse_cd=180; hit=[]
            drain_hits=0
            for sh in sorted(self.shades,key=lambda x:x['id']):
                if math.dist([p['pos'][0],p['pos'][1]+.8,p['pos'][2]],sh['pos'])<=5+1e-9:
                    if sh['state']=='drain':drain_hits+=1
                    hit.append(sh['id']); sh['state']='stunned'; sh['timer']=120
                    sh['push']=norm(sh['pos'][0]-p['pos'][0],sh['pos'][2]-p['pos'][2])
            for dr in self.drifters:
                if dr['state'] in ('chase','flee') and math.dist([p['pos'][0],p['pos'][1]+.8,p['pos'][2]],dr['pos'])<=5+1e-9:
                    if dr['state']=='flee' and dr['stolen']:
                        self.drop(dr['stolen'],dr['pos']); self.emit('drifter_drop',{'drifter_id':dr['id'],'amount':dr['stolen']})
                        dr['stolen']=0; dr['timer']=120
                    else: dr['state']='flee'; dr['timer']=240
            self.score+=len(hit)*5+drain_hits*10; self.emit('pulse',{'stunned_ids':hit})
        self.move_shades(); self.move_drifters()
        for dr in sorted(self.drifters,key=lambda x:x['id']):
            if dr['state']=='chase' and d(dr['pos'],p['pos'])<=1.2 and abs(dr['pos'][1]-p['pos'][1])<=1.5:
                amount=min(3,p['carried']); p['carried']-=amount; dr['stolen']+=amount
                dr['state']='flee'; dr['timer']=240
                self.emit('drifter_steal',{'drifter_id':dr['id'],'amount':amount,'carried':p['carried']})
        if not self.invuln:
            for sh in sorted(self.shades,key=lambda x:x['id']):
                safe=any(l['lit'] and d(p['pos'],l['pos'])<=6 for l in self.lanterns)
                if not safe and not sh['safe_exit'] and sh['state'] not in ('stunned','spawning','recoil') and d(p['pos'],sh['pos'])<=1+1e-9 and abs(p['pos'][1]-sh['pos'][1])<=1.5:
                    p['flames']-=1; dropped=p['carried']//2; p['carried']-=dropped; self.drop(dropped,p['pos'])
                    self.invuln=90; sh['state']='recoil'; sh['timer']=60
                    sh['push']=norm(sh['pos'][0]-p['pos'][0],sh['pos'][2]-p['pos'][2])
                    self.emit('player_hit',{'by':sh['id'],'flames':p['flames'],'dropped':dropped})
                    break
        self.spawn_finish()

    def move_shades(self):
        p=self.player['pos']
        for sh in self.shades:
            if sh['safe_exit']:
                sh['safe_exit']-=1
                for l in self.lanterns:
                    if l['lit'] and d(sh['pos'],l['pos'])<6:
                        ux,uz=norm(sh['pos'][0]-l['pos'][0],sh['pos'][2]-l['pos'][2])
                        step=(6-d(sh['pos'],l['pos']))/max(1,sh['safe_exit']+1)
                        sh['pos'][0]+=ux*step; sh['pos'][2]+=uz*step
                continue
            if sh['state'] in ('spawning','stunned','recoil'):
                if sh['state']=='stunned' and sh['timer']>105:
                    sh['pos'][0]+=sh['push'][0]*4/15; sh['pos'][2]+=sh['push'][1]*4/15
                if sh['state']=='recoil':
                    sh['pos'][0]+=sh['push'][0]*2/60; sh['pos'][2]+=sh['push'][1]*2/60
                sh['timer']-=1
                if sh['timer']<=0: sh['state']='wander'
                continue
            distance=d(sh['pos'],p)
            if sh['state']=='chase' and distance>=18: sh['state']='wander'
            elif sh['state']=='wander' and distance<=12: sh['state']='chase'
            if sh['state']=='chase' and distance:
                speed=4.5 if self.night==3 else 4.
                nx=sh['pos'][0]+(p[0]-sh['pos'][0])/distance*speed/HZ
                nz=sh['pos'][2]+(p[2]-sh['pos'][2])/distance*speed/HZ
                if not any(l['lit'] and d([nx,0,nz],l['pos'])<6 for l in self.lanterns):
                    sh['pos'][0],sh['pos'][2]=nx,nz

    def move_drifters(self):
        p=self.player['pos']
        for dr in self.drifters:
            if dr['state']=='removed': continue
            if dr['state']=='flee':
                ux,uz=norm(dr['pos'][0]-p[0],dr['pos'][2]-p[2])
                dr['pos'][0]+=ux*7/HZ; dr['pos'][2]+=uz*7/HZ; dr['timer']-=1
                if dr['timer']<=0: dr['state']='removed'
            else:
                dr['state']='chase' if self.player['carried']>=5 and d(dr['pos'],p)<=15 else 'idle'
                if dr['state']=='chase':
                    ux,uz=norm(p[0]-dr['pos'][0],p[2]-dr['pos'][2])
                    dr['pos'][0]+=ux*7/HZ; dr['pos'][2]+=uz*7/HZ
                else:
                    angle=self.sim_tick/90
                    dr['pos'][0]+=math.cos(angle)*2/HZ
                    dr['pos'][2]+=math.sin(angle)*2/HZ

    def spawn_finish(self):
        t=self.sim_tick
        if self.random_motes and t%240==0 and len(self.motes)<30:
            occupied={tuple(m['pos']) for m in self.motes}
            choices=[p for p in self.mote_points if tuple(p) not in occupied]
            if choices:
                p=self.rng.choice(choices); self.motes.append(self.mote(f'M{self.next_mote}',p,born=t)); self.next_mote+=1
        interval={1:480,2:420,3:360}[self.night]; cap={1:6,2:8,3:10}[self.night]
        if self.random_shades and t>=300 and (t-300)%interval==0:
            for _ in range(2 if t==300 else 1):
                if len(self.shades)>=cap: break
                choices=[p for p in self.shade_points if d(p,self.player['pos'])>=15 and not any(d(p,sh['pos'])<.01 for sh in self.shades)]
                if not choices: break
                p=self.rng.choice(choices)
                sh={'id':f'S{self.next_shade}','pos':p[:],'state':'wander','timer':0,'push':(1.,0.),'safe_exit':0}
                self.shades.append(sh); self.next_shade+=1; self.emit('shade_spawned',{'id':sh['id']})
        if self.night>=2 and self.random_drifters and t%1200==0 and len([dr for dr in self.drifters if dr['state']!='removed'])<2:
            choices=[p for p in self.shade_points if d(p,self.player['pos'])>=15]
            if choices:
                dr={'id':f'D{self.next_drifter}','pos':self.rng.choice(choices)[:],'state':'idle','stolen':0,'timer':0}
                self.drifters.append(dr); self.next_drifter+=1
        if self.player['flames']<=0: self.finish('lost','no_flames')
        elif self.time_left()<=0:
            threshold=math.ceil(.6*len(self.lanterns))
            if sum(l['lit'] for l in self.lanterns)>=threshold:self.finish('won','dawn_survived')
            else:self.finish('lost','dawn')

    def capacity(self): return min(10+2*self.successful_lights,20)

    def snapshot(self):
        r=lambda x:round(x,3)
        p=self.player; floor=self.ground(p['pos'][0],p['pos'][2],p['pos'][1])
        return {'type':'snapshot','tick':self.tick,'sim_tick':self.sim_tick,'night':self.night,'state':self.state,
                'time_left_s':r(self.time_left()),'score':self.score,'wind':self.wind.copy(),
                'obstacles':[{'pos':[r(x),0.,r(z)],'radius':r(radius)} for x,z,radius in self.obstacles],
                'player':{'pos':[r(v) for v in p['pos']],'vel':[r(v) for v in p['vel']],'flames':p['flames'],'carried':p['carried'],
                          'grounded':floor is not None and abs(p['pos'][1]-floor)<.001,'capacity':self.capacity(),
                          'invuln':self.invuln>0,'dash_cd_s':r(self.dash_cd/HZ),'pulse_cd_s':r(self.pulse_cd/HZ),'charm_s':r(self.charm_ticks/HZ)},
                'lanterns':[{'id':l['id'],'pos':[r(v) for v in l['pos']],'lit':l['lit'],'deposited':l['deposited'],'fuel':round(l.get('fuel_u',0)/60,1) if l['lit'] else 0,'ever_lit':l.get('ever_lit',False),'relit_count':l.get('relit_count',0)} for l in self.lanterns],
                'shades':[{'id':sh['id'],'pos':[r(v) for v in sh['pos']],'state':sh['state'],'target_lantern_id':sh.get('target_lantern_id')} for sh in self.shades],
                'motes_active':len(self.motes),'motes':[{'id':m['id'],'pos':[r(v) for v in m['pos']],'kind':m['kind'],'ttl_s':None if m['ttl'] is None else r(m['ttl']/HZ)} for m in self.motes],
                'drifters':[{'id':dr['id'],'pos':[r(v) for v in dr['pos']],'state':dr['state'],'stolen':dr['stolen']} for dr in self.drifters],
                'charms':[{'id':c['id'],'available':c['available'],'respawn_s':r(c['respawn']/HZ)} for c in self.charms]}
