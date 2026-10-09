import copy,json,unittest
from itertools import product
from engine_gaming.fol import *
from engine_gaming.fol_reference import evaluate_reference
from engine_gaming.world_adapter import from_store,Projection,identity

def sample(tick=0,service=True):
    ex={p:[] for p in SIGNATURE};ex.update(Person=[('a',),('b',)],Item=[('tool',)],Owns=[('a','tool')],Holds=[('b','tool')],Serviceable=[('tool',)] if service else [],Damaged=[] if service else [('tool',)])
    return Snapshot(('a','b','tool'),{'Alice':'a','Alias':'a','Bob':'b','Tool':'tool'},ex,dict.fromkeys(('a','b','tool'),1),{'a':'Alice','b':'Bob','tool':'Saw'},tick)
V=lambda x:['var',x]
C=lambda x:['const',x]
A=lambda p,*ts:['atom',p,*ts]
class Semantics(unittest.TestCase):
    def test_independent_truth_sets_scope_and_connectives(self):
        s=sample();atoms=[A('Person',V('x')),A('Item',V('x')),['eq',V('x'),V('y')],A('Owns',V('x'),V('y'))]
        forms=atoms+[['not',a] for a in atoms]+[[op,a,b] for a in atoms for b in atoms for op in ('and','or','implies')]
        forms += [['forall','x',['exists','y',A('Owns',V('x'),V('y'))]],['exists','y',['forall','x',A('Owns',V('x'),V('y'))]],['forall','x',['exists','x',A('Person',V('x'))]]]
        for f in forms:
            free=sorted(validate(f,s))
            for xs in product(s.domain,repeat=len(free)):
                env=dict(zip(free,xs));self.assertEqual(evaluate(s,f,env),evaluate_reference(s,f,env))
    def test_all_tiny_unary_interpretations(self):
        s=sample()
        for bits in product((False,True),repeat=3):
            ex=dict(s.extensions);ex['Claim']=[(x,) for x,b in zip(s.domain,bits) if b]
            w=Snapshot(s.domain,s.constants,ex,s.revisions,s.labels)
            for op in ('forall','exists'):
                f=[op,'x',['implies',A('Person',V('x')),A('Claim',V('x'))]]
                self.assertEqual(evaluate(w,f),evaluate_reference(w,f))
    def test_aliases_are_identity_not_label(self):
        s=sample();self.assertTrue(evaluate(s,['eq',C('Alice'),C('Alias')]))
        self.assertFalse(evaluate(s,A('Holds',C('Alice'),C('Tool'))))
        self.assertTrue(evaluate(s,A('Owns',C('Alice'),C('Tool'))))
    def test_malformed_and_hidden_branches_reject(self):
        s=sample()
        for f in (['or',['eq',C('Alice'),C('Alice')],['bogus']],A('Owns',C('Alice')),A('Unknown',V('x')),['eq',['const',True],C('Alice')],['forall','',A('Person',V('x'))],['eq',['const','Missing'],C('Alice')]):
            with self.assertRaises(ValueError):evaluate(s,f)
            with self.assertRaises(ValueError):evaluate_reference(s,f)
    def test_open_assignment_and_budget(self):
        s=sample();f=A('Person',V('x'))
        for assignment in (None,{'x':True},{'x':'a','z':'a'},{'x':1}):
            with self.assertRaises(InvalidFormula):evaluate(s,f,assignment)
        with self.assertRaises(EvaluationIncomplete):evaluate(s,['forall','x',f],budget=1)
    def test_invariants(self):
        s=sample()
        for pred,rows in [('Holds',[('a','tool'),('b','tool')]),('Owns',[]),('Inside',[('tool','tool')]),('Damaged',[('tool',)]),('Holds',[(True,'tool')])]:
            ex=dict(s.extensions);ex[pred]=rows
            with self.assertRaises(InvalidWorld):Snapshot(s.domain,s.constants,ex,s.revisions,s.labels)
        with self.assertRaises(InvalidWorld):Snapshot((),{},s.extensions,{}, {})
    def test_save_revalidate_and_immutable(self):
        s=sample();self.assertEqual(s.dumps(),Snapshot.loads(s.dumps()).dumps())
        with self.assertRaises(TypeError):s.constants['x']='a'
        raw=json.loads(s.dumps());raw['snapshot']['domain']=[]
        with self.assertRaises(InvalidWorld):Snapshot.loads(json.dumps(raw))
        raw['sha256']=hashlib.sha256(canonical(raw['snapshot']).encode()).hexdigest()
        with self.assertRaises(InvalidWorld):Snapshot.loads(json.dumps(raw))
    def test_atomic_stale_and_historical_queries(self):
        w=World(sample());w.commit(0,sample(1,False))
        with self.assertRaises(InvalidWorld):w.commit(0,sample(1))
        self.assertEqual(len(w.history),2);self.assertEqual(len(w.rejections),1)
        self.assertTrue(evaluate(w.history[0],A('Serviceable',C('Tool'))));self.assertFalse(evaluate(w.current,A('Serviceable',C('Tool'))))
    def test_text_board_label_camera_equivalence(self):
        s=sample();forms=[A('Owns',C('Alice'),C('Tool')),['exists','x',A('Holds',V('x'),C('Tool'))]]
        for mode in ('text','board'):
            for camera in range(4):
                p=Projection(s,mode,camera,{'a':'Renamed'})
                self.assertEqual(p.render()['interpretation'],s.data())
                for f in forms:self.assertEqual(p.query(f),evaluate_reference(s,f))
    def test_native_adapter_and_hidden_view(self):
        from tests_u4.fixtures import setup,ALICE,BOB,SAW,ROOM
        from hle_unified.records import ObjectVersion,ObjectRef,Role,Account,Occurrence,Moment
        from hle_unified.operation_records import WRITER
        e=setup(prepare=False);before=e.participant_view(ALICE).bytes()
        s,unsupported=from_store(e.world,aliases={'A':ALICE,'T':SAW.identity})
        self.assertTrue(evaluate(s,A('Owns',C('A'),C('T'))));self.assertTrue(unsupported)
        self.assertEqual(before,e.participant_view(ALICE).bytes())
        self.assertEqual(e.participant_view(ALICE).resolve(SAW),())
        self.assertEqual(s.revisions[identity(SAW.identity)],1)
        self.assertEqual(from_store(e.world,through=1)[0].tick,1)
        with self.assertRaises(InvalidWorld):from_store(e.world,through=True)
if __name__=='__main__':unittest.main()
