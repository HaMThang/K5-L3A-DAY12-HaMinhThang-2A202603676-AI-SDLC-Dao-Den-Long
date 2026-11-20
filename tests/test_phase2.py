"""Ticket-02 scenarios: each new simulation feature has a controlled setup."""
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from src.game import Game, T

ROOT=Path(__file__).resolve().parents[1]
STILL={'move':[0,0],'cam_yaw_deg':0}


class PhaseTwoTests(unittest.TestCase):
    def quiet(self, night=1, **extra):
        return Game(night=night, scenario={'random_motes':False,'random_shades':False,'random_drifters':False,'wind_enabled':False,**extra})

    def test_standard_maps_and_tuning(self):
        self.assertEqual(T['player_speed'],6)
        self.assertEqual(T['carry_capacity'],10)
        self.assertEqual(T['lantern_cost'],10)
        self.assertEqual([len(self.quiet(n).lanterns) for n in (1,2,3)],[5,6,7])
        self.assertEqual(self.quiet(1).lanterns[0]['pos'],[0.,0.,25.])
        self.assertEqual(self.quiet(2).lanterns[-1]['pos'],[53.,0.,-10.])
        self.assertEqual(self.quiet(3).lanterns[0]['pos'],[0.,6.,6.])

    def test_dash_air_height_and_pause_clock(self):
        g=self.quiet(1)
        g.step(STILL,{'jump':True})
        y=g.player['pos'][1]
        g.step(STILL,{'dash':True})
        self.assertEqual(g.events[0]['name'],'dash')
        self.assertEqual(g.player['pos'][1],y)
        before=g.time_left()
        g.step(STILL,{'pause':True})
        self.assertEqual(g.state,'paused')
        g.step(STILL,{})
        self.assertEqual(g.time_left(),before)
        self.assertEqual(g.sim_tick,2)
        g.step(STILL,{'pause':True})
        self.assertEqual(g.events[0]['name'],'resumed')

    def test_charm_pickup_speed_and_respawn(self):
        g=self.quiet(2,charms=[{'id':'C1','pos':[0,0,0]}])
        g.step(STILL,{})
        self.assertEqual(g.events[0]['name'],'charm_picked')
        self.assertEqual(g.charm_ticks,600)
        g.step({'move':[1,0],'cam_yaw_deg':0},{})
        self.assertAlmostEqual(g.player['pos'][0],7.2/60)
        self.assertFalse(g.charms[0]['available'])

    def test_drifter_steal_and_pulse_drop(self):
        g=self.quiet(2,player={'carried':8},drifters=[{'id':'D1','pos':[0,0,1],'state':'chase'}])
        g.step(STILL,{})
        self.assertEqual(g.player['carried'],5)
        self.assertEqual(g.events[0]['name'],'drifter_steal')
        g.step(STILL,{'pulse':True})
        self.assertIn('drifter_drop',[e['name'] for e in g.events])
        self.assertEqual(g.drifters[0]['stolen'],0)

    def test_mote_spawn_and_shade_spawn_schedule(self):
        g=Game(night=1,scenario={'random_shades':True,'random_motes':True})
        for _ in range(300): g.step(STILL,{})
        self.assertEqual([x['id'] for x in g.shades],['S1','S2'])
        self.assertEqual(g.next_mote,22)  # 20 initial, one at tick 240

    def test_headless_v11_scenario(self):
        with tempfile.TemporaryDirectory() as folder:
            folder=Path(folder)
            scenario=folder/'scenario.json'
            inputs=folder/'inputs.json'
            out=folder/'out.jsonl'
            scenario.write_text(json.dumps({'random_motes':False,'random_shades':False,'random_drifters':False,
                                            'player':{'carried':3},'charms':[{'pos':[0,0,0]}]}),encoding='utf-8')
            inputs.write_text(json.dumps({'frames':[{'tick':0,'dash':True},{'tick':1,'dash':False,'pause':True},
                                                    {'tick':2,'pause':False},{'tick':3,'pause':True}]}),encoding='utf-8')
            args=[sys.executable,'-m','src.headless','--seed','4','--night','2','--scenario',str(scenario),'--inputs',str(inputs),'--ticks','5','--out',str(out),'--snapshot-every','1']
            result=subprocess.run(args,cwd=ROOT,capture_output=True,text=True)
            self.assertEqual(result.returncode,0,result.stderr)
            records=[json.loads(line) for line in out.read_text(encoding='utf-8').splitlines()]
            self.assertEqual(records[0]['night'],2)
            self.assertEqual(records[0]['player']['charm_s'],0)
            self.assertTrue(all(k in records[0] for k in ('wind','drifters','charms','motes')))
            self.assertIn('paused',[r['name'] for r in records if r['type']=='event'])
            self.assertIn('dash',[r['name'] for r in records if r['type']=='event'])
            self.assertIn('charm_picked',[r['name'] for r in records if r['type']=='event'])


if __name__=='__main__': unittest.main()
