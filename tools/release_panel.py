"""Predeclared bounded performance and causal panel. Run under verify_batch freeze."""
import sys,pathlib
sys.path.insert(0,str(pathlib.Path(__file__).resolve().parents[1]))
import engine_gaming,time,json,gzip,resource,hashlib,dataclasses
from engine_gaming.scenario import setup,ref
from engine_gaming.field import Field
from engine_gaming.shell_adapter import enable
from engine_gaming.loop_audit import inspect
from engine_gaming.session import Session,DEFAULT
from hle_unified.records import ObjectRef
from hle_unified.selection_records import dumps

def refs(value):
    if type(value) is ObjectRef:yield value
    elif dataclasses.is_dataclass(value):
        for f in dataclasses.fields(value):yield from refs(getattr(value,f.name))
    elif type(value) in (tuple,list):
        for x in value:yield from refs(x)
    elif type(value) is dict:
        for x in value.values():yield from refs(x)

def depth(journal):
    # Atomic commits are nodes. Outputs within one commit are not parents.
    depths={};edge_count=0
    for tx in journal:
        parents={r for lineage in tx.lineage for r in (*lineage.inputs,*lineage.evidence) if r in depths}
        d=1+max((depths[r] for r in parents),default=0)
        edge_count+=len(parents)
        for v in tx.versions:depths[v.ref]=d
    return max(depths.values(),default=0),edge_count

def run(out):
    out.mkdir(parents=True,exist_ok=False);rows=[]
    cases=(('two',2,(12,8),4000,17,600,False),('three',3,(12,8,4),4000,17,600,False),('four',4,(12,8,4,2),4000,17,1200,False),('four_severed',4,(12,8,4,2),4000,17,1200,True),('exhausted',3,(12,8,4),80,1,600,False))
    for name,n,stocks,budget,quantum,horizon,cut in cases:
        start=time.perf_counter();f=enable(Field(*setup(n,budget,stocks),quantum=quantum));latency=[]
        if cut:f.edges.remove((f.actors[1],f.actors[2]))
        for _ in range(horizon):
            t=time.perf_counter();f.step();latency.append(time.perf_counter()-t)
        simulation=time.perf_counter()-start;cp=f.checkpoint();journal=f.engine.world.journal()
        t=time.perf_counter();report=inspect(journal,f.engine.access.checkpoint(),f.data(),not cut and name!='exhausted');audit_seconds=time.perf_counter()-t
        turns=[r for r in f.events if r['kind']=='turn'];deliveries=[r for r in f.events if r['kind']=='delivery'];longest,edges=depth(journal)
        by_actor={a.key:sum(r['actor']==a for r in turns) for a in f.actors}
        remaining=[f.engine.wallet(a)['energy'] for a in f.actors]
        rows.append(dict(name=name,simulation_seconds=simulation,audit_seconds=audit_seconds,p95_step_seconds=sorted(latency)[int(.95*(len(latency)-1))],max_step_seconds=max(latency),checkpoint_bytes=len(cp.encode()),transactions=len(journal),peak_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,turns_by_actor=by_actor,idle=sum(r['action']=='idle' for r in turns),exhausted_turns=sum(r['action']=='exhausted' for r in turns),stopped=sum(r['kind']=='stopped' for r in f.events),refusals=len(f.rejections),full_loop=report['full_loop'],consumed=report['consumed'],generated_deliveries=len(deliveries),unique_deliveries=len({(r['source'],r['receiver']) for r in deliveries}),lineage_depth=longest,lineage_reference_edges=edges,generated_intention_transformations=report['field']['derived_intentions'],remaining_energy=remaining))
        row=rows[-1]
        (out/(name+'.json.gz')).write_bytes(gzip.compress(cp.encode(),mtime=0));(out/(name+'-audit.json')).write_text(dumps(report))
        (out/'metrics.json').write_text(json.dumps(rows,indent=2))
        assert simulation<=90 and audit_seconds<=180 and row['p95_step_seconds']<=1 and row['max_step_seconds']<=5,row
        assert len(cp.encode())<=32_000_000 and len(journal)<=5000 and row['peak_rss_kib']<=768*1024,row
        assert max(by_actor.values())-min(by_actor.values())<=1 and min(remaining)>=0,row
        assert row['generated_deliveries']==row['unique_deliveries'] and not f.rejections,row
        if name=='exhausted':assert row['exhausted_turns'] and min(remaining)==0,row
        else:assert not any(f.pending.values()),row
        if cut:assert report['consumed']['alice']==0,row
        print(json.dumps(row),flush=True)
    s=Session({**DEFAULT,'shell':'corrected'})
    for c in (dict(id='one',kind='advance',turns=600),dict(id='renew',kind='renew'),dict(id='two',kind='advance',turns=600)):assert s.act(c)['ok']
    cp=s.checkpoint();start=time.perf_counter();restored=Session.restore(cp);seconds=time.perf_counter()-start
    assert restored.checkpoint()==cp and seconds<=90
    (out/'continued-session.json.gz').write_bytes(gzip.compress(cp.encode(),mtime=0));(out/'restore.json').write_text(json.dumps(dict(seconds=seconds,bytes=len(cp.encode()),exact=True),indent=2))
    (out/'SHA256.json').write_text(json.dumps({p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in out.iterdir() if p.name!='SHA256.json'},indent=2))
if __name__=='__main__':run(pathlib.Path(sys.argv[1]))
