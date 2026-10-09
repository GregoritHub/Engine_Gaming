"""Independent bounded-loop attribution from raw records; no field execution imports."""
from .field_audit import audit as field_audit
from hle_unified.records import ObjectId
from hle_unified.material import attrs
from hle_unified.crossing_content import decode


def inspect(transactions,access_text,state,require_loop=False):
    txs=tuple(transactions);base=field_audit(txs,access_text,state)
    versions={v.ref:v for t in txs for v in t.versions};heads={v.ref.identity:v for t in txs for v in t.versions}
    jobs={v.ref.identity:attrs(v) for v in heads.values() if attrs(v).get('record_type')=='operation'}
    consumed={a.key:attrs(heads[ObjectId('eg.workshop',a.key+'-stock')])['consumed'] for a in state['actors']}
    edges=[];caps=[];used=[]
    for row in state['events']:
        if row['kind']!='delivery':continue
        msg=attrs(versions[row['source']]);data=decode(msg['payload']);caps.append(data['cap'])
        producer=jobs[row['operation'].identity]
        if producer['status']!='succeeded' or producer.get('public.0')!=row['source']:raise ValueError('uncompleted producer')
        edges.append(dict(source=producer['source_input'],target=row['source'],action='paid Theorize',actor=row['sender']))
        applies=[d for d in jobs.values() if d.get('actor')==row['receiver'] and d.get('recipe_key')=='apply-expenditure-v1' and d.get('source_input')==row['source'] and d.get('status')=='succeeded']
        for d in applies:
            edges.append(dict(source=row['source'],target=d['result'],action='paid Apply',actor=row['receiver']))
            used.append((row['sender'],row['receiver']))
    for v in versions.values():
        if v.label=='Intention from retained experience':edges.append(dict(source=attrs(v)['link.0'],target=v.ref,action='paid retained-output adaptation'))
    a=state['actors'];ring=set(zip(a,(*a[1:],a[0])))
    full=set(used)==ring and len(used)==len(a)
    if require_loop and not full:raise ValueError('missing generated return pathway')
    if require_loop and len(a)==3 and (caps!=[5,3,1] or consumed!={'alice':1,'bryn':5,'cass':3}):raise ValueError('three-agent semantic/material prediction failed')
    return dict(passed=True,full_loop=full,consumed=consumed,transmitted_caps=tuple(caps),edges=tuple(edges),field=base)
