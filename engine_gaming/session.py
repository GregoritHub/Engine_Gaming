"""Bounded user commands and replay-verified user saves."""
import json
from .scenario import setup,ref,ROOM,intention,perform,selectors
from .field import Field
from .shell_adapter import generated,enable,release
from .fol import unique_pairs
from hle_unified.material import attrs
from hle_unified.operation_records import OperationRequest

DEFAULT=dict(population=3,budget=4000,stocks=[12,8,4],initial_cap=5,quantum=17,shell='blocked',shell_actor=0)
class Session:
    SCHEMA='eg-session-v3'
    def __init__(self,config=None,version=None):
        self.version=version or self.SCHEMA
        if self.version not in (self.SCHEMA,'eg-session-v2'):raise ValueError('unknown session version')
        c=dict(DEFAULT if config is None else config)
        if set(c)!=set(DEFAULT) or c['shell'] not in ('none','blocked','corrected'):raise ValueError('exact session configuration required')
        if type(c['shell_actor']) is not int or not 0<=c['shell_actor']<c['population']:raise ValueError('valid Shell actor index required')
        if type(c['budget']) is not int or not 0<=c['budget']<=20000 or type(c['initial_cap']) is not int or not 0<=c['initial_cap']<=1000:raise ValueError('bounded exact budgets and intention')
        if type(c['quantum']) is not int or not 1<=c['quantum']<=1000:raise ValueError('bounded work quantum')
        self.config=c;self.field=Field(*setup(c['population'],c['budget'],tuple(c['stocks']),c['initial_cap']),quantum=c['quantum'])
        f=self.field
        if self.version=='eg-session-v2':
            f.legacy=True;f.refresh_inspections=False
            for own in f.own.values():own.pop('limit_by_stock',None)
        if c['shell']!='none':
            a=f.actors[c['shell_actor']];p=generated(f.engine,a)
        enable(f)
        if c['shell']=='corrected':release(f.engine,a,p,'genesis-correction')
        self.commands=[];self.results=[]
    def act(self,command):
        if type(command) is not dict or type(command.get('id')) is not str or not command['id'].strip() or len(command['id'])>100:raise ValueError('named command required')
        for old,result in zip(self.commands,self.results):
            if old['id']==command['id']:
                if old!=command:raise ValueError('command identity reused with different content')
                return result
        if len(self.commands)>=2048:raise ValueError('session command limit')
        kind=command.get('kind');fields={'advance':{'turns'},'cancel':set(),'renew':set(),'reflect':set(),'propose':{'cap'},'inspect':set(),'consume':{'amount'}}
        if kind not in fields or set(command)!={'id','kind',*fields[kind]}:raise ValueError('unknown command or fields')
        f=self.field;e=f.engine;a=f.actors[0]
        if kind=='advance':
            n=command['turns']
            if type(n) is not int or not 0<=n<=1000 or f.turn+n>10000:raise ValueError('bounded finite turns required')
        if kind in ('consume','propose'):
            n=command['amount' if kind=='consume' else 'cap']
            if type(n) is not int or not 1<=n<=(5 if kind=='propose' and self.version==self.SCHEMA else 1000):raise ValueError('proposal limit is 1–5; consumption quantity is 1–1000')
        try:
            if kind=='advance':f.run(command['turns'])
            elif kind=='cancel':
                p=f.pending[a]
                if p is None:raise ValueError('no active player work')
                e.cancel('player:'+command['id'],a,p['key']);f.pending[a]=None;f.own[a]['phase']='stopped'
            elif kind=='renew':
                if any(f.pending.values()) or any(f.queues.values()) or f.own[a]['phase']!='done' or not f.own[a]['cycles']:raise ValueError('finish this allocation before renewing')
                if any(f.own[actor]['phase'] not in ('await','done') for actor in f.actors[1:]):raise ValueError('unresolved participant stop')
                f.own[a]['phase']='inspect'
                for actor in f.actors[1:]:f.own[actor]['phase']='await'
            else:
                if f.pending[a] or f.queues[a]:raise ValueError('finish or cancel current work first')
                if kind=='reflect':
                    patterns=e.pattern_view(a)
                    if not patterns:raise ValueError('no retained authorization pattern')
                    d=release(e,a,patterns[0],'player:'+command['id'])
                    if d['status']!='succeeded':
                        f.pending[a]=dict(key='player:'+command['id'],kind='player',source=None)
                        raise ValueError('correction incomplete')
                    if f.own[a]['phase']=='stopped':f.own[a]['phase']='initial' if f.own[a]['cycles']==0 else 'await'
                elif kind=='propose':
                    if f.own[a]['cycles'] or f.own[a]['phase'] not in ('initial','stopped'):raise ValueError('proposal belongs before the first allocation')
                    out,r=intention(e,a,'player:'+command['id'],command['cap']);d=perform(e,r)
                    if d['status']!='succeeded':
                        f.pending[a]=dict(key=r.key,kind='player',source=None)
                        raise ValueError('intention binding incomplete')
                    f.own[a].update(initial=out,phase='initial')
                else:
                    target=f._known_stock(a);ev=tuple(p.address for p in e.participant_view(a).resolve(target));key='player:'+command['id']
                    r=OperationRequest(key,a,kind,ROOM,evidence=ev,**({'target':target} if kind=='inspect' else {'stock':target,'amount':command['amount']}))
                    d=perform(e,r)
                    if kind=='inspect' and d['status']=='succeeded':
                        if self.version=='eg-session-v2':
                            obs=e.deliver_event(key+':observed',d['result'],a)
                            f.queues[a].append(dict(key=key+':observed',source=obs,sender=a,kind='observation'))
                        else:
                            observed=attrs(e.world.resolve(d['result']))['target']
                            e.disclose(key+':observed',a,observed,selectors(e.world.resolve(observed)),observed)
                            f.queues[a].append(dict(key=key+':observed',source=observed,sender=a,kind='material_refresh'))
                    if d['status'] not in ('succeeded','failed','cancelled'):f.pending[a]=dict(key=key,kind='player',source=None)
                    if d['status']=='failed':raise ValueError(d['failure'])
            result=dict(ok=True,turn=f.turn)
        except ValueError as exc:result=dict(ok=False,error=str(exc),turn=f.turn)
        self.commands.append(dict(command));self.results.append(result);return result
    def checkpoint(self):
        return json.dumps(dict(schema=self.version,config=self.config,commands=self.commands,results=self.results,state=self.field.checkpoint()),sort_keys=True,separators=(',',':'))
    @classmethod
    def restore(cls,text):
        if type(text) is not str or len(text)>32_000_000:raise ValueError('save exceeds 32 MB bound')
        try:
            d=json.loads(text,object_pairs_hook=unique_pairs)
            if type(d) is not dict or set(d)!={'schema','config','commands','results','state'} or d['schema'] not in (cls.SCHEMA,'eg-session-v2'):raise ValueError('unsupported session schema; use Field.restore for trusted v1 research evidence')
            if type(d['commands']) is not list or len(d['commands'])>2048:raise ValueError('invalid command sequence')
            s=cls(d['config'],d['schema'])
            for c in d['commands']:s.act(c)
            if s.checkpoint()!=json.dumps(d,sort_keys=True,separators=(',',':')):raise ValueError('save differs from deterministic paid replay')
            return s
        except (KeyError,TypeError,OverflowError,RecursionError) as exc:raise ValueError('malformed session save') from exc
