"""Workshop opportunities; all attribution, correction and costs remain native."""
from .scenario import ref,TOPIC,ROOM,CUE,TRIGGER,perform,disclose
from hle_unified.records import ObjectRef,ObjectVersion,Role
from hle_unified.operation_records import WRITER
from hle_unified.material import attributes
from hle_unified.shell_records import EncounterRequest,PatternSeed,Effect
from hle_unified.development_records import DevelopmentRequest
from hle_unified.development_policy import opportunity


def evidence(e,actor,target=TOPIC):
    view=e.participant_view(actor)
    return tuple(p.address for s in opportunity(view,target,ROOM)[1] for p in view.resolve(s))


def supply(e,actor,key,target=TOPIC,deliver=True,read=True,**terms):
    identity=ref('facts:'+actor.key+':'+target.identity.key+':'+str(target.revision)).identity
    try:old=e.world.head(identity).ref
    except KeyError:old=None
    r=ObjectRef(identity,old.revision+1 if old else 1)
    values=dict(schema='u7.encounter-facts-v1',receiver=actor,target=target,context=ROOM,trigger=TRIGGER,available=True,safe=True,requires_partner=False,willing=True,approval_required=False,approved=False,feedback='neutral',recommended='engage',partner=ObjectRef(actor,1))
    if set(terms)-set(values):raise ValueError('unknown opportunity field')
    values.update(terms)
    e.declare('facts:'+key,(ObjectVersion(r,WRITER,'Supplied encounter facts',(Role.RECORD,),previous=old,attributes=attributes(values)),))
    if deliver:disclose(e,actor,r,'facts:'+key,subject=target,read=read)
    return r


def generated(e,actor):
    for n,target in enumerate((TOPIC,ref(actor.key+'-stock'))):
        key='origin:'+actor.key+':'+str(n);supply(e,actor,key,target,feedback='blame')
        d=perform(e,EncounterRequest(key,actor,target,ROOM,CUE,ObjectRef(actor,1),ObjectRef(actor,1),evidence(e,actor,target)))
        if d['status']!='succeeded':raise ValueError('origin encounter incomplete')
    return e.pattern_view(actor)[0]


def fixture(e,actor,kind,route='*'):
    seed=PatternSeed(actor,ROOM,CUE,TRIGGER,TOPIC,(Effect(kind,route,-1 if kind=='salience' else 1),),tuple(p.address for p in e.participant_view(actor).resolve(TOPIC)))
    return e.inject_pattern_fixture('fixture:'+actor.key+':'+kind,seed)


def release(e,actor,pattern,key='release',target=TOPIC,evidence_=None):
    r=DevelopmentRequest(key,actor,'release',pattern.ref if hasattr(pattern,'ref') else pattern,ROOM,CUE,(target,),evidence(e,actor,target) if evidence_ is None else evidence_,ObjectRef(actor,1))
    return perform(e,r)


def enable(field,phase='admission'):
    if phase not in ('admission','after_first_step'):raise ValueError('unknown Shell phase')
    for actor in field.actors:supply(field.engine,actor,'current:'+actor.key)
    field.shell_phase=phase
    return field
