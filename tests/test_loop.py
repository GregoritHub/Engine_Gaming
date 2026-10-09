import unittest,pathlib,gzip,json,hashlib,time
from engine_gaming.scenario import setup,ref
from engine_gaming.field import Field
from engine_gaming.shell_adapter import enable,generated,release
from engine_gaming.loop_audit import inspect
from hle_unified.selection_records import dumps
from hle_unified.material import attrs


def scenario(arm):
    f=Field(*setup());intervention=None
    if arm in ('shell','corrected'):
        p=generated(f.engine,f.actors[1]);enable(f)
        if arm=='corrected':release(f.engine,f.actors[1],p)
    else:enable(f)
    if arm=='severed':f.edges.remove((f.actors[1],f.actors[2]))
    if arm in ('withheld','constant_history'):
        phase='reframe' if arm=='withheld' else 'embody';pointer='retained' if arm=='withheld' else 'observation'
        while f.turn<600 and f.own[f.actors[1]]['phase']!=phase:f.step()
        assert f.turn<600
        own=f.own[f.actors[1]];intervention=dict(turn=f.turn,actor=f.actors[1],field=pointer,withheld=own[pointer])
        if pointer=='retained':own[pointer]=None
        else:
            # Freeze the local continuation before consuming newly generated experience.
            own['phase']='await';own['used']=tuple(p.source for p in f.engine.participant_view(f.actors[1]).lookup(key='payload'))
    f.run(600-f.turn)
    return f,intervention

class Generativity(unittest.TestCase):
    def test_declared_loop_and_all_counterfactuals(self):
        root=pathlib.Path('evidence/EG05')/('panel-'+str(time.time_ns()));root.mkdir(parents=True,exist_ok=True);rows={}
        for arm in ('connected','severed','withheld','constant_history','shell','corrected'):
            with self.subTest(arm=arm):
                f,control=scenario(arm);full=arm in ('connected','corrected')
                report=inspect(f.engine.world.journal(),f.engine.access.checkpoint(),f.data(),full)
                self.assertEqual(report['full_loop'],full)
                self.assertEqual(report['consumed']['alice'],1 if full else 0)
                self.assertFalse(f.rejections,f.rejections)
                report['intervention']=control
                report['wallets']=tuple((a,f.engine.wallet(a)) for a in f.actors)
                (root/(arm+'.json.gz')).write_bytes(gzip.compress(f.checkpoint().encode(),mtime=0))
                (root/(arm+'-report.json')).write_text(dumps(report))
                rows[arm]=dict(full_loop=full,consumed=report['consumed'],caps=report['transmitted_caps'],turns=f.turn)
        (root/'summary.json').write_text(json.dumps(rows,indent=2))
        (root/'SHA256.json').write_text(json.dumps({p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in root.iterdir() if p.name!='SHA256.json'},indent=2))
    def test_claim_without_return_refused(self):
        f,_=scenario('severed')
        with self.assertRaises(ValueError):inspect(f.engine.world.journal(),f.engine.access.checkpoint(),f.data(),True)
