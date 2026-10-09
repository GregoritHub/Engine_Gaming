"""Raw field reconstruction; imports no field executor, policy or scheduler."""
from hle.model_a import element_at
from hle_unified.records import Account
from hle_unified.material import attrs
from hle_unified.crux_shell_audit import audit as native_audit
from hle_unified.crux_audit import _access
from hle_unified.crossing_content import decode


def audit(transactions,access_text,state):
    txs=tuple(transactions);native=native_audit(txs,access_text)
    versions={v.ref:v for tx in txs for v in tx.versions};heads={v.ref.identity:v for tx in txs for v in tx.versions}
    times={v.ref:tx.at.tick for tx in txs for v in tx.versions};details,bindings=_access(access_text,versions,times)
    actors=state['actors'];types=dict(zip(actors,state['types']));edges=set(state['edges']);deliveries={};count=0
    for row in state['events']:
        kind=row['kind']
        if kind=='delivery':
            key=row['key']
            if key in deliveries or (row['sender'],row['receiver']) not in edges:raise ValueError('duplicate or disconnected delivery')
            source=versions[row['source']];d=attrs(source)
            audience=tuple(v for k,v in d.items() if k.startswith('audience.'))
            if d.get('actor')!=row['sender'] or row['receiver'] not in audience or d.get('operation')!=row['operation']:raise ValueError('unaddressed source or forged origin')
            op=attrs(versions[row['operation']]);element=op['route.'+str(op['route_count']-1)+'.element']
            if row['element']!=element or element_at(types[row['sender']],row['sender_position'])!=element or element_at(types[row['receiver']],row['receiver_position'])!=element:raise ValueError('incorrect directional geometry')
            deliveries[key]=row;count+=1
        elif kind=='processed':
            evidence=[p for (actor,address),(p,at) in details.items() if actor==row['actor'] and address.delivery==row['delivery'] and p.source==row['source']]
            if not evidence:raise ValueError('processing flag without paid received particulars')
            jobs=[attrs(v) for v in heads.values() if attrs(v).get('record_type')=='operation' and attrs(v).get('actor')==row['actor'] and attrs(v).get('key')==row['key']]
            if len(jobs)!=1 or jobs[0].get('delivery')!=row['delivery'] or jobs[0]['status']!='succeeded':raise ValueError('processing lost native work')
    turns=[r for r in state['events'] if r['kind']=='turn']
    if len(turns)!=state['turn']:raise ValueError('missing scheduled turn')
    for i,row in enumerate(turns):
        if row['turn']!=i or row['actor']!=actors[i%len(actors)]:raise ValueError('unfair or forged turn')
        start,end=row['native_before'],row['native_after']
        if not 0<=start<=end<=len(txs):raise ValueError('invalid native interval')
        charges={a:0 for a in actors}
        for tx in txs[start:end]:
            for v in tx.versions:
                d=attrs(v)
                if d.get('record_type')=='wallet' and v.previous:
                    before=attrs(versions[v.previous]);charges[d['actor']]+=before['energy']-d['energy']
        if charges[row['actor']]!=row['spent'] or any(n for a,n in charges.items() if a!=row['actor']):raise ValueError('turn charge disagrees with native raw history')
    derived=0
    for v in versions.values():
        if v.label!='Intention from retained experience':continue
        source=attrs(v).get('link.0')
        if source not in bindings or times[source]>=times[v.ref]:raise ValueError('derived draft lacks prior owned retention')
        b,_=bindings[source];original=decode(b.content[0].object);a=v.facet(Account);d=decode(a.content[0].object)
        if b.actor!=a.holder or original.get('kind')!='personal_policy' or d!=dict(kind='intention',cap=original['cap'],consent=True):raise ValueError('draft changed retained semantic content')
        derived+=1
    return {'passed':True,'deliveries':count,'turns':len(turns),'derived_intentions':derived,'native_audit':native}
