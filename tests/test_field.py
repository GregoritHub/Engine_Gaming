import unittest
from engine_gaming.scenario import setup,ACTORS,ref,ROOM,TOPIC
from engine_gaming.field import Field
from engine_gaming.field_policy import proposal
from hle_unified.material import attrs
from engine_gaming.field_audit import audit
from hle_unified.operation_records import OperationRequest
from hle_unified.records import Material
class Connections(unittest.TestCase):
    def make(self,n=2,edges=None,quantum=17):
        e,a,t,i=setup(n,stocks=(12,8,4)[:n]);return Field(e,a,t,i,edges,quantum)
    def test_processed_delivery_changes_material_outcome(self):
        f=self.make().run(200);self.assertFalse(f.rejections,f.rejections)
        self.assertGreater(attrs(f.engine.world.head(ref('bryn-stock').identity))['consumed'],0)
        off=self.make(edges=set()).run(200)
        self.assertEqual(attrs(off.engine.world.head(ref('bryn-stock').identity))['consumed'],0)
        self.assertTrue(any(e['kind']=='processed' for e in f.events))
        audit(f.engine.world.journal(),f.engine.access.checkpoint(),f.data())
    def test_three_agents_and_fair_turns(self):
        f=self.make(3).run(450);self.assertFalse(f.rejections,f.rejections)
        turns=[e for e in f.events if e['kind']=='turn']
        self.assertEqual([e['actor'] for e in turns],list(f.actors)*150)
        self.assertEqual(len([e for e in f.events if e['kind']=='delivery']),3)
        self.assertTrue(f.snapshot().domain)
    def test_undelivered_hidden_change_not_policy_input(self):
        f=self.make(edges=set());b=f.actors[1];before=proposal(f.engine.participant_view(b),f.own[b])
        for _ in range(120):f.step()
        self.assertEqual(proposal(f.engine.participant_view(b),f.own[b]),before)
    def test_delivery_not_read_and_duplicate(self):
        f=self.make(quantum=1)
        for _ in range(400):
            f.step()
            if any(e['kind']=='delivery' for e in f.events):break
        d=next(e for e in f.events if e['kind']=='delivery');b=d['receiver']
        self.assertEqual(f.engine.participant_view(b).resolve(d['source']),())
        self.assertFalse(f.transmit(d['sender'],b,d['source']))
        self.assertFalse(f.transmit(b,d['sender'],d['source'])) if (b,d['sender']) not in f.edges else None
    def test_asymmetric_edge_and_unavailable(self):
        f=self.make(edges={(ACTORS[0],ACTORS[1])});f.active.remove(ACTORS[1]);f.run(150)
        self.assertFalse(any(e['kind']=='delivery' for e in f.events))
    def test_indirect_shared_object_subscription(self):
        f=self.make(3);f.edges={(f.actors[0],f.actors[1])};f.observations={(f.actors[1],f.actors[2])};f.run(230)
        self.assertTrue(any(e['kind']=='observation_delivery' for e in f.events))
        self.assertTrue(any(e['kind']=='choice' and e['actor']==f.actors[2] and e['action']=='inspect_shared' for e in f.events))
    def test_forged_processing_rejected(self):
        from copy import deepcopy
        f=self.make().run(160);d=f.data();d['events']=(*d['events'],dict(kind='processed',actor=f.actors[1],delivery='forged',source=TOPIC,key='forged'))
        with self.assertRaises(ValueError):audit(f.engine.world.journal(),f.engine.access.checkpoint(),d)
    def test_finite_exhaustion_keeps_paid_partial_work(self):
        e,a,t,i=setup(2,budget=18,stocks=(12,8));f=Field(e,a,t,i,quantum=1).run(100)
        self.assertEqual(e.wallet(a[0])['energy'],0)
        self.assertFalse(any(x['kind']=='delivery' for x in f.events))
        self.assertTrue(f.pending[a[0]])
        before=e.wallet(a[0]);f.run(10);self.assertEqual(before,e.wallet(a[0]))
    def test_stale_competing_actions_and_duplicate_command(self):
        f=self.make();e=f.engine;a=f.actors[0];stock=ref('alice-stock')
        evidence=tuple(p.address for p in e.participant_view(a).resolve(stock))
        for k in ('one','two'):e.start('start-'+k,OperationRequest(k,a,'consume',ROOM,stock=stock,evidence=evidence))
        e.advance('work-one',a,'one',3);e.commit('commit-one',a,'one')
        wallet=e.wallet(a);e.commit('commit-one',a,'one');self.assertEqual(wallet,e.wallet(a))
        e.advance('work-two',a,'two',3);e.commit('commit-two',a,'two')
        self.assertEqual(e.job_status(a,'two')['failure'],'stale_dependency')
        self.assertEqual(attrs(e.world.head(stock.identity))['consumed'],1)
        self.assertEqual(e.job_status(a,'two')['spent'],3)
    def test_partial_processing_and_restore(self):
        f=self.make(quantum=1).run(90);saved=f.checkpoint();restored=Field.restore(saved)
        self.assertEqual(saved,restored.checkpoint())
        f.run(200);restored.run(200);self.assertEqual(f.checkpoint(),restored.checkpoint())
if __name__=='__main__':unittest.main()
