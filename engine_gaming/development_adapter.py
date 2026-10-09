"""Native observed practice adapter; no invented learning or capacity grants."""
from .scenario import ROOM,CUE,TOPIC,ref,perform
from .shell_adapter import supply,evidence,release
from hle_unified.records import ObjectRef
from hle_unified.development_records import DevelopmentRequest
from hle_unified.operation_records import OperationRequest


def train(e,actor,pattern,key='practice'):
    targets=(TOPIC,ref(actor.key+'-stock'));observations=[]
    for i,t in enumerate(targets):
        supply(e,actor,key+':opportunity:'+str(i),t)
        d=release(e,actor,pattern,key+':release:'+str(i),t)
        if d['status']!='succeeded':raise ValueError('incomplete local foundation')
    for episode in range(2):
        stem=key+':'+str(episode)
        for i,t in enumerate(targets):supply(e,actor,stem+':facts:'+str(i),t)
        ev=tuple(dict.fromkeys(x for t in targets for x in evidence(e,actor,t)))
        r=DevelopmentRequest(stem,actor,'respond',pattern.ref,ROOM,CUE,targets,ev,ObjectRef(actor,1))
        d=perform(e,r)
        if d['status']!='succeeded':raise ValueError('response incomplete')
        obs=e.deliver_event(stem+':observation',d['result'],actor)
        perform(e,OperationRequest(stem+':read',actor,'read',ROOM,delivery=stem+':observation'))
        ev=tuple(p.address for p in e.participant_view(actor).resolve(obs))
        d=perform(e,DevelopmentRequest(stem+':practice',actor,'practice',pattern.ref,ROOM,CUE,targets,ev,ObjectRef(actor,1),obs))
        if d['status']!='succeeded':raise ValueError('practice incomplete')
        observations.append(obs)
    ev=tuple(dict.fromkeys(p.address for obs in observations for p in e.participant_view(actor).resolve(obs)))
    d=perform(e,DevelopmentRequest(key+':reorganize',actor,'reorganize',pattern.ref,ROOM,CUE,(TOPIC,),ev,ObjectRef(actor,1)))
    if d['status']!='succeeded':raise ValueError('reorganization incomplete')
    return d['development']
