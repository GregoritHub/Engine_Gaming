import unittest,json,gzip,pathlib,time,hashlib
from engine_gaming.session import Session,DEFAULT
from engine_gaming.scenario import setup,ref,TOPIC,ROOM,CUE,perform
from engine_gaming.field import Field
from engine_gaming.shell_adapter import generated,enable,supply,release,evidence
from engine_gaming.development_adapter import train
from hle_unified.material import attrs,attributes
from hle_unified.records import ObjectRef,ObjectVersion,Role
from hle_unified.operation_records import WRITER
from hle_unified.shell_records import EncounterRequest
from hle_unified.crux_shell_audit import audit
from hle_unified.selection_records import dumps

class Persistence(unittest.TestCase):
    def ready(self,**c):return Session({**DEFAULT,'shell':'corrected',**c})
    def test_exact_partial_replay_and_future(self):
        s=self.ready(quantum=1);s.act(dict(id='first',kind='advance',turns=41));saved=s.checkpoint();t=Session.restore(saved)
        self.assertEqual(saved,t.checkpoint())
        for x in (s,t):x.act(dict(id='next',kind='advance',turns=700))
        self.assertEqual(s.checkpoint(),t.checkpoint())
    def test_forged_save_and_duplicate_commands(self):
        s=self.ready();c=dict(id='tick',kind='advance',turns=10);s.act(c);cp=s.checkpoint();s.act(c);self.assertEqual(cp,s.checkpoint())
        with self.assertRaises(ValueError):s.act({**c,'turns':11})
        d=json.loads(cp);d['state']=d['state'].replace('"turn":10','"turn":11')
        with self.assertRaises(ValueError):Session.restore(json.dumps(d))
        with self.assertRaises(ValueError):Session.restore('{"schema":1,"schema":2}')
    def test_cancel_keeps_spending_and_stops_reward(self):
        s=self.ready(quantum=1);a=s.field.actors[0]
        s.act(dict(id='work',kind='advance',turns=7));before=s.field.engine.wallet(a)['energy']
        self.assertTrue(s.act(dict(id='cancel',kind='cancel'))['ok']);self.assertEqual(before,s.field.engine.wallet(a)['energy'])
        self.assertEqual(Session.restore(s.checkpoint()).checkpoint(),s.checkpoint())
    def test_new_episode_reuses_generated_experience(self):
        s=self.ready();s.act(dict(id='one',kind='advance',turns=600));a=s.field.actors[0]
        self.assertEqual(s.field.own[a]['cycles'],1)
        self.assertTrue(s.act(dict(id='renew',kind='renew'))['ok'])
        s.act(dict(id='two',kind='advance',turns=600))
        self.assertTrue(s.field.own[a]['retained'])
        self.assertTrue(any(x['kind']=='choice' and x['actor']==a and x['action']=='reframe' for x in s.field.events))
        audit(s.field.engine.world.journal(),s.field.engine.access.checkpoint())
        root=pathlib.Path('evidence/EG06')/('continuation-'+str(time.time_ns()));root.mkdir()
        (root/'session.json.gz').write_bytes(gzip.compress(s.checkpoint().encode(),mtime=0))
        (root/'metrics.json').write_text(json.dumps(dict(turns=s.field.turn,cycles=s.field.own[a]['cycles'],refusals=len(s.field.rejections),idle=sum(x.get('action')=='idle' for x in s.field.events),sha256=hashlib.sha256(s.checkpoint().encode()).hexdigest()),indent=2))
    def test_relevant_correction_and_irrelevant_history(self):
        s=Session();s.act(dict(id='blocked',kind='advance',turns=300));self.assertEqual(s.field.own[s.field.actors[0]]['phase'],'stopped')
        s.act(dict(id='reflect',kind='reflect'));s.act(dict(id='retry',kind='advance',turns=600));self.assertEqual(s.field.own[s.field.actors[0]]['cycles'],1)
        f=enable(Field(*setup()));g=Field.restore(f.checkpoint())
        g.engine.declare('irrelevant',(ObjectVersion(ref('unread-ornament'),WRITER,'Unseen ornament',(Role.RECORD,),attributes=attributes({'colour':'blue'})),))
        f.run(600);g.run(600)
        for a in f.actors:self.assertEqual(f.own[a],g.own[a])
    def test_acquired_capacity_depends_on_independent_observed_practice(self):
        f=Field(*setup());a=f.actors[1];p=generated(f.engine,a);enable(f)
        control=Field.restore(f.checkpoint());train(f.engine,a,p)
        self.assertTrue(f.engine.development_view(a)['capacities']);self.assertFalse(control.engine.development_view(a)['capacities'])
        for x,expected in ((f,'engage'),(control,'wait')):
            target=ObjectRef(a,1);supply(x.engine,a,'new-target',target)
            d=perform(x.engine,EncounterRequest('new-demand',a,target,ROOM,CUE,target,target,evidence(x.engine,a,target)))
            self.assertEqual(attrs(x.engine.world.resolve(d['encounter']))['route'],expected)
        restored=Field.restore(f.checkpoint());self.assertEqual(f.checkpoint(),restored.checkpoint())
        report=audit(f.engine.world.journal(),f.engine.access.checkpoint());self.assertTrue(report['passed'])
        supply(restored.engine,a,'danger',ObjectRef(a,1),safe=False)
        d=perform(restored.engine,EncounterRequest('danger',a,ObjectRef(a,1),ROOM,CUE,ObjectRef(a,1),ObjectRef(a,1),evidence(restored.engine,a,ObjectRef(a,1))))
        self.assertEqual(attrs(restored.engine.world.resolve(d['encounter']))['route'],'wait')
        root=pathlib.Path('evidence/EG06')/('capacity-'+str(time.time_ns()));root.mkdir()
        (root/'trained.json.gz').write_bytes(gzip.compress(f.checkpoint().encode(),mtime=0));(root/'audit.json').write_text(dumps(report))
