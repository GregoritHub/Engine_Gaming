import unittest
from dataclasses import replace
from engine_gaming.scenario import setup,TOPIC,ROOM,CUE,ref
from engine_gaming.field import Field
from engine_gaming.shell_adapter import enable,generated,fixture,supply,release,evidence
from hle_unified.material import attrs,attributes
from hle_unified.records import ObjectRef
from hle_unified.crux_shell_audit import audit
from hle_unified.crux_shell_records import ShellMovementRequest

class Shells(unittest.TestCase):
    def base(self,kind='approval',phase='admission'):
        f=Field(*setup());a=f.actors[1]
        p=generated(f.engine,a) if kind=='approval' else fixture(f.engine,a,kind)
        enable(f,phase);return f,p
    def consumed(self,f,key):return attrs(f.engine.world.head(ref(key+'-stock').identity))['consumed']
    def test_all_five_effects_and_paid_correction(self):
        for kind in ('approval','obligation','salience','forecast','exclude_route'):
            with self.subTest(kind=kind):
                f,p=self.base(kind);c=Field.restore(f.checkpoint())
                if kind in ('approval','obligation'):
                    before=c.engine.wallet(c.actors[1])['energy'];d=release(c.engine,c.actors[1],p)
                    self.assertEqual(d['status'],'succeeded');self.assertLess(c.engine.wallet(c.actors[1])['energy'],before)
                else:c=enable(Field(*setup()))
                f.run(600);c.run(600)
                self.assertFalse(f.rejections,f.rejections);self.assertFalse(c.rejections,c.rejections)
                self.assertEqual(self.consumed(f,'bryn'),0);self.assertEqual(self.consumed(c,'bryn'),5)
                self.assertTrue(audit(f.engine.world.journal(),f.engine.access.checkpoint())['passed'])
                self.assertTrue(audit(c.engine.world.journal(),c.engine.access.checkpoint())['passed'])
    def test_interruption_retains_paid_step_without_destination(self):
        f,p=self.base(phase='after_first_step');f.run(350)
        a=audit(f.engine.world.journal(),f.engine.access.checkpoint())
        interrupted=[attrs(v) for tx in f.engine.world.journal() for v in tx.versions if v.ref.identity.namespace=='c5.interruption']
        self.assertEqual(len(interrupted),1);self.assertGreater(interrupted[0]['spent'],0)
        self.assertTrue(interrupted[0]['intermediate']);self.assertFalse(interrupted[0]['original_obligation_met'])
        self.assertEqual(self.consumed(f,'bryn'),0);self.assertTrue(a['passed'])
    def test_generated_origin_retained_and_restriction_recurs(self):
        f,p=self.base();a=f.actors[1];self.assertEqual(p.origin_mode,'generated')
        release(f.engine,a,p);supply(f.engine,a,'renewed',safe=False);f.run(450)
        self.assertEqual(self.consumed(f,'bryn'),0);self.assertEqual(f.engine.pattern_view(a)[0].origin,p.origin)
        self.assertFalse(f.engine.development_view(a)['capacities'])
    def test_other_target_release_does_not_clear(self):
        f,p=self.base();a=f.actors[1];t=ref('bryn-stock');supply(f.engine,a,'different',t)
        release(f.engine,a,p,target=t);f.run(450);self.assertEqual(self.consumed(f,'bryn'),0)
    def test_unsupported_and_irrelevant_correction_refused(self):
        for kind in ('salience','forecast','exclude_route'):
            f,p=self.base(kind)
            with self.assertRaises(ValueError):release(f.engine,f.actors[1],p)
        f,p=self.base();a=f.actors[1]
        with self.assertRaises(ValueError):release(f.engine,a,p,evidence_=tuple(x.address for x in f.engine.participant_view(a).resolve(TOPIC)))
    def test_unread_and_stale_admission_cannot_bypass(self):
        f,p=self.base();a=f.actors[0];choice=dict(action='theorize',source=f.own[a]['initial'])
        r=f._request(a,choice);old=evidence(f.engine,a)
        supply(f.engine,a,'changed',safe=False)
        q=ShellMovementRequest('bad',r,ObjectRef(a,1),ObjectRef(a,1),old)
        with self.assertRaises(ValueError):f.engine.start('bad-start',q)
        with self.assertRaises(ValueError):ShellMovementRequest('empty',r,ObjectRef(a,1),ObjectRef(a,1),())
    def test_auditor_rejects_false_success_and_bypass(self):
        f,p=self.base();f.run(450)
        for field,value in [('movement_complete',True),('admitted',True),('admission_spent',0)]:
            txs=[]
            for tx in f.engine.world.journal():
                vs=tuple(replace(v,attributes=attributes({**attrs(v),field:value})) if v.ref.identity.namespace=='c5.admission' and attrs(v)['actor']==f.actors[1] else v for v in tx.versions)
                txs.append(replace(tx,versions=vs))
            with self.assertRaises(ValueError):audit(txs,f.engine.access.checkpoint())
