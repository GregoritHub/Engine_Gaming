"""Local finite allocation policy; no engine, world, hidden state or auditor."""
from hle_unified.crossing_content import decode
from .scenario import ROOM,CUE,TOPIC


def proposal(view,own):
    phase=own['phase']
    if phase=='initial':return {'action':'theorize','source':own['initial']}
    if phase=='await':
        models=[]
        for p in view.lookup(key='payload'):
            if p.source in own['used']:continue
            try:d=decode(p.value)
            except (ValueError,TypeError):continue
            if d.get('kind')=='model' and d.get('target')==TOPIC and d.get('context')==ROOM:
                models.append(p.source)
        if models:
            demand=5
            if own.get('limit_by_stock'):
                rows={}
                for p in view.lookup():
                    if p.source.identity.namespace=='eg.workshop' and p.source.identity.key==view.snapshot.actor.key+'-stock':rows.setdefault(p.source,{})[p.address.key]=p.value
                if rows:
                    row=rows[max(rows)]
                    if type(row.get('quantity')) is int and type(row.get('consumed')) is int:demand=min(5,row['quantity']-row['consumed'])
                if demand<=0:return None
            return {'action':'apply','source':min(models),'demand':demand}
    if phase in ('inspect','inspect_shared'):return {'action':phase}
    if phase=='embody':return {'action':'embody','source':own['observation']}
    if phase=='reframe':
        b=view._bindings.get(own['retained'])
        if b:
            d=decode(b.content[0].object)
            if d.get('kind')=='personal_policy' and type(d.get('cap')) is int:
                return {'action':'reframe','source':b.ref,'cap':d['cap']}
    if phase=='forward':return {'action':'theorize','source':own['intention']}
    return None
