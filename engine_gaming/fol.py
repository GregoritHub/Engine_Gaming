"""Classical finite FOL; partial participant knowledge is deliberately separate."""
from dataclasses import dataclass
from types import MappingProxyType
import hashlib
import json

SIGNATURE = {'Person':1,'Item':1,'Context':1,'Claim':1,'Interpretation':1,
             'Event':1,'Owns':2,'Holds':2,'Serviceable':1,'Damaged':1,'Inside':2}
class InvalidWorld(ValueError): pass
class InvalidFormula(ValueError): pass
class EvaluationIncomplete(RuntimeError): pass

def name(x): return type(x) is str and bool(x.strip())
def canonical(x): return json.dumps(x,sort_keys=True,separators=(',',':'),ensure_ascii=True,allow_nan=False)
def unique_pairs(rows):
    d={}
    for k,v in rows:
        if k in d: raise ValueError('duplicate JSON key')
        d[k]=v
    return d

@dataclass(frozen=True)
class Snapshot:
    domain: tuple
    constants: object
    extensions: object
    revisions: object
    labels: object
    tick: int = 0

    def __post_init__(self):
        if type(self.tick) is not int or self.tick<0: raise InvalidWorld('nonnegative integer time required')
        if type(self.domain) is not tuple or not self.domain or any(not name(x) for x in self.domain) or len(set(self.domain))!=len(self.domain):
            raise InvalidWorld('finite nonempty distinct string identities required')
        domain=set(self.domain)
        try:
            constants=dict(self.constants); revisions=dict(self.revisions); labels=dict(self.labels)
            ex={k:frozenset(tuple(row) for row in rows) for k,rows in self.extensions.items()}
        except (TypeError,AttributeError,ValueError) as exc: raise InvalidWorld('invalid interpretation shape') from exc
        if set(ex)!=set(SIGNATURE):raise InvalidWorld('exact complete predicate signature required')
        if any(not name(k) or type(v) is not str or v not in domain for k,v in constants.items()):raise InvalidWorld('every constant must denote an entity')
        if set(revisions)!=domain or any(type(v) is not int or v<1 for v in revisions.values()):raise InvalidWorld('positive exact revisions required')
        if set(labels)!=domain or any(not name(v) for v in labels.values()):raise InvalidWorld('one display label per entity')
        for pred,rows in ex.items():
            if any(len(row)!=SIGNATURE[pred] or any(type(x) is not str or x not in domain for x in row) for row in rows):raise InvalidWorld('predicate arity or domain mismatch')
        people={r[0] for r in ex['Person']};items={r[0] for r in ex['Item']}
        if people&items:raise InvalidWorld('Person and Item sorts disjoint')
        for pred in ('Owns','Holds'):
            if any(a not in people or b not in items for a,b in ex[pred]):raise InvalidWorld('ownership and custody are Person x Item')
            if any(sum(b==item for a,b in ex[pred])!=1 for item in items):raise InvalidWorld('each item has exactly one owner and custodian')
        if ex['Serviceable']&ex['Damaged']:raise InvalidWorld('condition predicates disjoint')
        if any(x not in items for p in ('Serviceable','Damaged') for x, in ex[p]):raise InvalidWorld('condition requires Item')
        if any(a not in items or b not in items or a==b for a,b in ex['Inside']):raise InvalidWorld('containment requires distinct Items')
        reach=set(ex['Inside'])
        while True:
            expanded=reach|{(a,d) for a,b in reach for c,d in reach if b==c}
            if any(a==b for a,b in expanded):raise InvalidWorld('containment cycle')
            if expanded==reach:break
            reach=expanded
        object.__setattr__(self,'domain',tuple(sorted(domain)))
        for k,v in (('constants',constants),('extensions',ex),('revisions',revisions),('labels',labels)):
            object.__setattr__(self,k,MappingProxyType(v))

    def data(self):
        return {'schema':'eg-fol-snapshot-v1','domain':list(self.domain),'constants':dict(self.constants),
                'extensions':{k:[list(r) for r in sorted(v)] for k,v in self.extensions.items()},
                'revisions':dict(self.revisions),'labels':dict(self.labels),'tick':self.tick}

    def dumps(self):
        d=self.data();return canonical({'snapshot':d,'sha256':hashlib.sha256(canonical(d).encode()).hexdigest()})

    @classmethod
    def loads(cls,text):
        try:
            raw=json.loads(text,object_pairs_hook=unique_pairs)
            if type(raw) is not dict or set(raw)!={'snapshot','sha256'}:raise InvalidWorld('invalid envelope')
            d=raw['snapshot']
            if hashlib.sha256(canonical(d).encode()).hexdigest()!=raw['sha256']:raise InvalidWorld('snapshot checksum mismatch')
            if set(d)!={'schema','domain','constants','extensions','revisions','labels','tick'} or d['schema']!='eg-fol-snapshot-v1':raise InvalidWorld('unknown snapshot schema')
            return cls(tuple(d['domain']),d['constants'],d['extensions'],d['revisions'],d['labels'],d['tick'])
        except (KeyError,TypeError,json.JSONDecodeError) as exc:raise InvalidWorld('malformed snapshot') from exc

def validate(formula,snapshot,max_nodes=4096,max_depth=64):
    """Validate all branches before any short circuit can hide malformed input."""
    nodes=0
    def term(t,bound):
        if type(t) not in (tuple,list) or len(t)!=2 or t[0] not in ('var','const') or not name(t[1]):raise InvalidFormula('invalid term')
        if t[0]=='const':
            if t[1] not in snapshot.constants:raise InvalidFormula('unknown constant')
            return set()
        return set() if t[1] in bound else {t[1]}
    def visit(f,bound,depth):
        nonlocal nodes
        nodes+=1
        if nodes>max_nodes or depth>max_depth:raise InvalidFormula('syntax limit exceeded')
        if type(f) not in (tuple,list) or not f or type(f[0]) is not str:raise InvalidFormula('invalid formula')
        op=f[0]
        if op=='atom':
            if len(f)<2 or type(f[1]) is not str or f[1] not in SIGNATURE or len(f)!=2+SIGNATURE[f[1]]:raise InvalidFormula('predicate or arity')
            return set().union(*(term(t,bound) for t in f[2:]))
        if op=='eq' and len(f)==3:return term(f[1],bound)|term(f[2],bound)
        if op=='not' and len(f)==2:return visit(f[1],bound,depth+1)
        if op in ('and','or','implies') and len(f)==3:return visit(f[1],bound,depth+1)|visit(f[2],bound,depth+1)
        if op in ('exists','forall') and len(f)==3 and name(f[1]):return visit(f[2],bound|{f[1]},depth+1)
        raise InvalidFormula('unknown operator or malformed node')
    return frozenset(visit(formula,set(),0))

def evaluate(snapshot,formula,assignment=None,budget=100000):
    free=validate(formula,snapshot)
    env={} if assignment is None else dict(assignment)
    if set(env)!=free or any(type(v) is not str or v not in snapshot.domain for v in env.values()):raise InvalidFormula('exact domain assignment for all free variables required')
    if type(budget) is not int or budget<1:raise EvaluationIncomplete('positive evaluation budget required')
    remaining=budget
    def term(t,e):return snapshot.constants[t[1]] if t[0]=='const' else e[t[1]]
    def go(f,e):
        nonlocal remaining
        remaining-=1
        if remaining<0:raise EvaluationIncomplete('evaluation unfinished')
        op=f[0]
        if op=='atom':return tuple(term(t,e) for t in f[2:]) in snapshot.extensions[f[1]]
        if op=='eq':return term(f[1],e)==term(f[2],e)
        if op=='not':return not go(f[1],e)
        if op=='and':return go(f[1],e) and go(f[2],e)
        if op=='or':return go(f[1],e) or go(f[2],e)
        if op=='implies':return not go(f[1],e) or go(f[2],e)
        values=(go(f[2],{**e,f[1]:x}) for x in snapshot.domain)
        return all(values) if op=='forall' else any(values)
    return go(formula,env)

class World:
    """Trusted atomic snapshot boundary, not a player truth-edit permission."""
    def __init__(self,initial):
        if type(initial) is not Snapshot:raise InvalidWorld('validated snapshot required')
        self.history=[initial];self.rejections=[]
    @property
    def current(self):return self.history[-1]
    def commit(self,expected_tick,candidate):
        try:
            if type(expected_tick) is not int or expected_tick!=self.current.tick:raise InvalidWorld('stale snapshot')
            if type(candidate) is not Snapshot or candidate.tick!=expected_tick+1:raise InvalidWorld('next snapshot required')
            candidate=Snapshot.loads(candidate.dumps())
        except ValueError as exc:
            self.rejections.append({'expected_tick':expected_tick,'reason':str(exc)})
            raise
        self.history.append(candidate);return candidate
