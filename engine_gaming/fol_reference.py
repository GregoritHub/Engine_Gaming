"""Independent small-world truth-set evaluator. No production decision imports."""
from itertools import product

ARITIES={'Person':1,'Item':1,'Context':1,'Claim':1,'Interpretation':1,'Event':1,
         'Owns':2,'Holds':2,'Serviceable':1,'Damaged':1,'Inside':2}
def evaluate_reference(world,formula,assignment=None,budget=100000):
    remaining=budget;count=0
    def variable(t):
        if type(t) not in (tuple,list) or len(t)!=2 or t[0] not in ('var','const') or type(t[1]) is not str or not t[1].strip():raise ValueError('bad term')
        if t[0]=='const' and t[1] not in world.constants:raise ValueError('bad constant')
        return {t[1]} if t[0]=='var' else set()
    def space(names):
        nonlocal remaining
        for values in product(world.domain,repeat=len(names)):
            remaining-=1
            if remaining<0:raise RuntimeError('reference evaluation unfinished')
            yield values
    def relation(f,depth=0):
        nonlocal count
        count+=1
        if depth>64 or count>4096 or type(f) not in (tuple,list) or not f:raise ValueError('bad syntax')
        op=f[0]
        if op in ('atom','eq'):
            if op=='atom':
                if len(f)<2 or type(f[1]) is not str or f[1] not in ARITIES or len(f)!=ARITIES[f[1]]+2:raise ValueError('bad atom')
                ts=f[2:]
            else:
                if len(f)!=3:raise ValueError('bad equality')
                ts=f[1:]
            ns=tuple(sorted(set().union(*(variable(t) for t in ts))))
            rows=set()
            for values in space(ns):
                env=dict(zip(ns,values));args=tuple(world.constants[t[1]] if t[0]=='const' else env[t[1]] for t in ts)
                if (args in world.extensions[f[1]]) if op=='atom' else (args[0]==args[1]):rows.add(values)
            return ns,rows
        if op=='not' and len(f)==2:
            ns,rows=relation(f[1],depth+1);return ns,set(space(ns))-rows
        if op in ('and','or','implies') and len(f)==3:
            an,ar=relation(f[1],depth+1);bn,br=relation(f[2],depth+1);ns=tuple(sorted(set(an)|set(bn)));out=set()
            for values in space(ns):
                env=dict(zip(ns,values));a=tuple(env[x] for x in an) in ar;b=tuple(env[x] for x in bn) in br
                if {'and':a and b,'or':a or b,'implies':not a or b}[op]:out.add(values)
            return ns,out
        if op in ('forall','exists') and len(f)==3 and type(f[1]) is str and f[1].strip():
            bn,br=relation(f[2],depth+1);ns=tuple(n for n in bn if n!=f[1]);out=set()
            for values in space(ns):
                env=dict(zip(ns,values));matches=0
                for entity in world.domain:
                    env[f[1]]=entity
                    matches+=tuple(env[n] for n in bn) in br
                if matches==(len(world.domain)) if op=='forall' else matches>0:out.add(values)
            return ns,out
        raise ValueError('bad operator')
    ns,rows=relation(formula);env={} if assignment is None else dict(assignment)
    if set(env)!=set(ns) or any(type(v) is not str or v not in world.domain for v in env.values()):raise ValueError('bad assignment')
    return tuple(env[n] for n in ns) in rows
