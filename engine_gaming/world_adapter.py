"""Versioned read-only mapping from native journal snapshots into FOL."""
import json
from .fol import Snapshot,SIGNATURE,InvalidWorld
from hle_unified.records import ObjectId,Material,Role,Occurrence,Lifecycle

ROLE_MAP={Role.PERSON:'Person',Role.MATERIAL:'Item',Role.CONTEXT:'Context',
          Role.CLAIM:'Claim',Role.INTERPRETATION:'Interpretation'}
def identity(value):
    if type(value) is not ObjectId:raise InvalidWorld('native ObjectId required')
    return json.dumps([value.namespace,value.key],separators=(',',':'))

def from_store(store,through=None,aliases=None):
    journal=store.journal()
    through=len(journal) if through is None else through
    if type(through) is not int or not 1<=through<=len(journal):raise InvalidWorld('existing nonempty journal prefix required')
    heads={}
    for tx in journal[:through]:
        for version in tx.versions:heads[version.ref.identity]=version
    active={k:v for k,v in heads.items() if v.lifecycle==Lifecycle.ACTIVE}
    extensions={k:set() for k in SIGNATURE};unsupported=[]
    for key,value in active.items():
        entity=identity(key)
        for role in value.roles:
            if role in ROLE_MAP:extensions[ROLE_MAP[role]].add((entity,))
            else:unsupported.append((entity,'role',role.value))
        if value.occurrence==Occurrence.ACTUAL_EVENT:extensions['Event'].add((entity,))
        material=value.facet(Material)
        if material:
            extensions['Item'].add((entity,));extensions['Owns'].add((identity(material.owner),entity));extensions['Holds'].add((identity(material.custodian),entity))
            if material.condition in ('serviceable','damaged'):extensions[material.condition.title()].add((entity,))
            else:unsupported.append((entity,'condition',material.condition))
        for facet in value.facets:
            if type(facet) is not Material:unsupported.append((entity,'facet',type(facet).__name__))
    constants={k:identity(v) for k,v in (aliases or {}).items()}
    s=Snapshot(tuple(identity(k) for k in active),constants,extensions,
               {identity(k):v.ref.revision for k,v in active.items()},
               {identity(k):v.label for k,v in active.items()},through)
    return s,tuple(unsupported)

class Projection:
    """Display positions and labels are metadata; facts retain stable IDs."""
    def __init__(self,snapshot,mode='text',camera=0,labels=None):
        if mode not in ('text','board'):raise ValueError('text or board required')
        self.snapshot=snapshot;self.mode=mode;self.camera=camera
        self.labels=dict(snapshot.labels) if labels is None else dict(labels)
    def render(self):
        entities=[{'id':x,'label':self.labels.get(x,x),'screen':((i%4+self.camera)%4,i//4)} for i,x in enumerate(self.snapshot.domain)]
        return {'mode':self.mode,'entities':entities,'interpretation':self.snapshot.data()}
    def query(self,formula,assignment=None):
        from .fol import evaluate
        return evaluate(self.snapshot,formula,assignment)
