"""Explicit workshop genesis and adapters. No research test fixture imports."""
from hle_unified.records import (ObjectId,ObjectRef,ObjectVersion,Role,Concept,Material,Definition,SourceStatus,Account,Occurrence,Proposition,TimeScope,Moment,ClaimStatus)
from hle_unified.operation_records import WRITER,LAW,OperationRequest
from hle_unified.operations import record,wallet_address
from hle_unified.material import OperationStore,attributes,attrs
from hle_unified.cognition import profile
from hle_unified.cognitive_records import catalog,reference
from hle_unified.crux_shell_execution import CruxShellEngine
from hle_unified.particulars import Selector
from hle_unified.crossing_content import encode,decode
from hle_unified.shell_records import PatternPolicy


def ref(key,revision=1):return ObjectRef(ObjectId('eg.workshop',key),revision)
ACTORS=tuple(ref(x).identity for x in ('alice','bryn','cass'))
ROOM,UNIT,LAW_REF,TOPIC,TRIGGER=map(ref,('workshop','unit','law','shared-task','entrusted-demand'))
CUE=reference('minor:Coin:10')

def perform(e,r,limit=100000):
    e.start('start:'+r.key,r);e.advance('work:'+r.key,r.actor,r.key,limit)
    if e.job_status(r.actor,r.key)['status']=='ready':e.commit('commit:'+r.key,r.actor,r.key)
    return e.job_status(r.actor,r.key)

def selectors(value):
    if value.ref.identity.namespace=='c3.message':
        return tuple(Selector(a.name,'detail',('attributes',str(i),'value')) for i,a in enumerate(value.attributes) if a.name=='payload')
    result=[Selector('name','name',('label',))]
    if value.facet(Material):result += [Selector(k,'detail',('facets','0',k)) for k in ('owner','custodian','condition','quantity')]
    result += [Selector(a.name,'detail',('attributes',str(i),'value')) for i,a in enumerate(value.attributes)]
    return tuple(result)

def disclose(e,actor,source,key,subject=None,read=True):
    e.disclose('delivery:'+key,actor,source,selectors(e.world.resolve(source)),subject or source)
    if read:perform(e,OperationRequest('read:'+key,actor,'read',ROOM,delivery='delivery:'+key))

def intention(e,actor,key,cap,source=None):
    """Owned draft. A derived draft takes its cap from a paid native personal output."""
    view=e.participant_view(actor)
    if source is None:
        evidence=tuple(p.address for p in view.resolve(TOPIC));basis=(TOPIC,)
    else:
        b=view._bindings.get(source)
        if b is None or source.identity.namespace!='c3.output':raise ValueError('native owned personal output required')
        d=decode(b.content[0].object)
        if d.get('kind')!='personal_policy' or type(d.get('cap')) is not int or d['cap']!=cap:raise ValueError('derived intention must preserve actual retained cap')
        evidence=b.particulars;basis=tuple(dict.fromkeys(view.detail(a).source for a in evidence))
    if type(cap) is not int or not 0<=cap<=1000:raise ValueError('bounded exact cap')
    value=ObjectVersion(ref(key),WRITER,'Initial goal' if source is None else 'Intention from retained experience',(Role.INTERPRETATION,),
        (Account(TOPIC,(Proposition(TOPIC,'c3.data',encode(dict(kind='intention',cap=cap,consent=True)),ROOM,TimeScope(Moment(0,0),None)),),Moment(0,0),actor,basis),),
        occurrence=Occurrence.INTERPRETATION,attributes=attributes(dict(cue=CUE,context=ROOM,meaning='Scoped allocation intention',endorsement=ClaimStatus.TENTATIVE.value,confidence=None,**({'link.0':source} if source else {}))))
    e.declare('draft:'+key,(value,))
    return value.ref,OperationRequest('bind:'+key,actor,'bind',ROOM,binding=value.ref,evidence=evidence)

def setup(population=3,budget=4000,stocks=(12,8,4),initial_cap=5):
    if type(population) is not int or not 2<=population<=8:raise ValueError('population 2–8 required')
    if type(budget) is not int or budget<0:raise ValueError('finite integer budget')
    actors=tuple(ref(('alice','bryn','cass')[i] if i<3 else 'agent'+str(i)).identity for i in range(population))
    types=('iee','sli','ile','esi','lie','eii','lse','sei')[:population]
    stocks=tuple(stocks)
    if len(stocks)!=population or any(type(n) is not int or not 1<=n<=1000 for n in stocks):raise ValueError('one finite stock per actor')
    world=OperationStore();versions=[]
    for actor,tim,quantity in zip(actors,types,stocks):
        versions.extend((ObjectVersion(ObjectRef(actor,1),WRITER,actor.key.title(),(Role.PERSON,)),
            record(wallet_address(actor),'Finite work budget',dict(record_type='wallet',actor=actor,energy=budget,time=budget,initial_energy=budget,initial_time=budget)),profile(actor,tim),
            ObjectVersion(ref(actor.key+'-stock'),WRITER,actor.key.title()+"'s supplies",(Role.MATERIAL,),
                (Material(actor,actor,quantity,UNIT,'stock'),),attributes=attributes(dict(consumed=0,purpose='consume')))))
    versions.extend((ObjectVersion(ROOM,WRITER,'The workshop',(Role.CONTEXT,)),
        ObjectVersion(UNIT,WRITER,'One supply unit',(Role.DEFINITION,),(Definition('Finite material quantum',SourceStatus.ENGINEERING),)),
        ObjectVersion(LAW_REF,WRITER,'Workshop action rules',(Role.DEFINITION,),(Definition('Inherited finite workshop actions',SourceStatus.ENGINEERING,attributes({'law':LAW})),)),
        ObjectVersion(TOPIC,WRITER,'Shared allocation task',(Role.CONCEPT,),(Concept(()),)),
        ObjectVersion(TRIGGER,WRITER,'Entrusted demand',(Role.DEFINITION,),(Definition('Supplied finite encounter cue',SourceStatus.ENGINEERING),)),*catalog()))
    world.create('genesis',WRITER,tuple(versions));e=CruxShellEngine(world,LAW_REF)
    for actor in actors:
        for source in (ROOM,CUE,TOPIC,TRIGGER,ObjectRef(actor,1),ref(actor.key+'-stock')):
            disclose(e,actor,source,'genesis:'+actor.key+':'+source.identity.key)
        e.configure_patterns('patterns:'+actor.key,PatternPolicy(actor,generate=True))
    initial,r=intention(e,actors[0],'initial-intention',initial_cap);perform(e,r)
    return e,actors,types,initial
