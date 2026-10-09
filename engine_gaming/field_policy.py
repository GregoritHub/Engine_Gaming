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
        if models:return {'action':'apply','source':min(models)}
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
