"""Bounded directed field around unchanged native paid operations."""
from copy import deepcopy
from hle.model_a import position_of,element_at
from hle.relations import landing_position
from hle_unified.records import ObjectRef,Material
from hle_unified.operation_records import OperationRequest
from hle_unified.crossing_records import CrossingRequest
from hle_unified.material import attrs
from hle_unified.selection_records import dumps,loads
from hle_unified.crux_shell_execution import CruxShellEngine
from .scenario import ROOM,CUE,TOPIC,ref,selectors,intention
from .field_policy import proposal
from .world_adapter import from_store
from .shell_adapter import evidence as shell_evidence
from hle_unified.crux_shell_records import ShellMovementRequest
from hle_unified.operations import address


class Field:
    SCHEMA='eg-agent-field-v1'
    def __init__(self,engine,actors,types,initial,edges=None,quantum=17):
        if len(set(actors))!=len(actors) or len(actors)!=len(types) or len(actors)<2:raise ValueError('distinct typed population')
        if type(quantum) is not int or quantum<1:raise ValueError('positive integer quantum')
        self.engine=engine;self.actors=tuple(actors);self.types=dict(zip(actors,types));self.quantum=quantum
        self.edges=set(zip(actors,(*actors[1:],actors[0]))) if edges is None else set(edges)
        if any(a not in actors or b not in actors or a==b for a,b in self.edges):raise ValueError('valid directed edges required')
        self.turn=0;self.serial=0;self.events=[];self.sent=set();self.queues={a:[] for a in actors};self.pending={a:None for a in actors}
        self.own={a:dict(phase='initial' if i==0 else 'await',initial=initial if i==0 else None,used=(),observation=None,retained=None,intention=None,cycles=0,forward=i!=0) for i,a in enumerate(actors)}
        self.active=set(actors);self.rejections=[];self.observations=set();self.shell_phase=None
    def key(self,actor,kind):
        self.serial+=1;return 'eg:'+actor.key+':'+kind+':'+str(self.serial)
    def snapshot(self):return from_store(self.engine.world)[0]
    def _known_stock(self,actor):
        refs=[p.source for p in self.engine.participant_view(actor).lookup() if p.source.identity==ref(actor.key+'-stock').identity]
        return max(refs,key=lambda x:x.revision)
    def _evidence(self,actor):return tuple(p.address for p in self.engine.participant_view(actor).resolve(TOPIC))
    def transmit(self,sender,receiver,source):
        """Trusted routing boundary; native disclosure enforces exact audience."""
        stamp=(sender,receiver,source)
        if (sender,receiver) not in self.edges or receiver not in self.active:return False
        if stamp in self.sent:return False
        m=self.engine._cross_public.get(source)
        if m is None or sender not in m['audience'] or receiver not in m['audience']:raise ValueError('addressed native output required')
        value=self.engine.world.resolve(source);d=attrs(value)
        if d.get('actor')!=sender:raise ValueError('sender must own the generated output')
        operation=d['operation'];job=attrs(self.engine.world.resolve(operation))
        # The source operation pins the actual last realized element.
        i=job['route_count']-1;element=job['route.'+str(i)+'.element']
        a=self.types[sender];b=self.types[receiver];p=position_of(a,element);q=landing_position(a,p,b)
        if element_at(b,q)!=element:raise ValueError('transport changed element')
        key=self.key(receiver,'delivery');self.engine.disclose(key,receiver,source,selectors(value),source)
        self.queues[receiver].append(dict(key=key,source=source,sender=sender,kind='message'))
        self.sent.add(stamp);self.events.append(dict(kind='delivery',turn=self.turn,sender=sender,receiver=receiver,source=source,operation=operation,key=key,element=element,sender_position=p,receiver_position=q))
        return True
    def _publish(self,actor,source):
        # Audience was specified in the local goal when constructing the request.
        for receiver in self.actors:
            if receiver!=actor:self.transmit(actor,receiver,source) if (actor,receiver) in self.edges else None
    def _peer(self,actor):return self.actors[(self.actors.index(actor)+1)%len(self.actors)]
    def observe(self,observer,event,owner):
        """Declared indirect subscription to an actual event on a shared object."""
        if (owner,observer) not in self.observations or observer not in self.active:return False
        ed=attrs(self.engine.world.resolve(event));source=ed.get('stock') or ed.get('target')
        if source is None or self.engine.world.resolve(source).facet(Material) is None:return False
        key=self.key(observer,'observe');self.engine.disclose(key,observer,source,selectors(self.engine.world.resolve(source)),source)
        self.queues[observer].append(dict(key=key,source=source,sender=owner,kind='shared_object',after='inspect_shared'))
        self.events.append(dict(kind='observation_delivery',turn=self.turn,sender=owner,receiver=observer,source=source,event=event,key=key))
        return True
    def _request(self,actor,choice):
        action=choice['action'];key=self.key(actor,action)
        if action in ('inspect','inspect_shared'):
            target=self.own[actor].get('shared_target') if action=='inspect_shared' else self._known_stock(actor)
            return OperationRequest(key,actor,'inspect',ROOM,target=target,evidence=tuple(p.address for p in self.engine.participant_view(actor).resolve(target)))
        if action=='reframe':
            out,r=intention(self.engine,actor,key,choice['cap'],choice['source']);self.own[actor]['intention']=out;return r
        recipes={'theorize':'theorize-expenditure-v1','apply':'apply-expenditure-v1','embody':'embody-expenditure-v1'}
        return CrossingRequest(key,actor,recipes[action],ROOM,CUE,(choice['source'],),self._evidence(actor),TOPIC,
            stock=self._known_stock(actor) if action=='apply' else None,peer=self._peer(actor) if action=='theorize' else None,demand=5)
    def _start_choice(self,actor,choice):
        request=self._request(actor,choice)
        pending={'key':request.key,'kind':choice['action'],'source':choice.get('source')}
        if self.shell_phase and choice['action'] in ('theorize','apply','embody'):
            gate=self.key(actor,'admission')
            request=ShellMovementRequest(gate,request,ObjectRef(actor,1),ObjectRef(actor,1),shell_evidence(self.engine,actor),phase=self.shell_phase)
            pending=dict(key=gate,kind='admission',child=pending)
        self.engine.start('start:'+request.key,request)
        self.pending[actor]=pending
        self.events.append(dict(kind='choice',turn=self.turn,actor=actor,action=choice['action'],key=request.key,source=choice.get('source')))
    def _finish(self,actor,pending,d):
        own=self.own[actor];kind=pending['kind']
        if kind=='admission' and d['status']=='succeeded':
            receipt=attrs(self.engine.world.resolve(address('c5.admission',actor,pending['key'])))
            self.events.append(dict(kind='admission',turn=self.turn,actor=actor,key=pending['key'],admitted=receipt['admitted'],child=receipt['child']))
            if receipt['child'] is not None:return pending['child']
            own['phase']='stopped';return
        if d['status']!='succeeded':
            own['phase']='stopped';self.events.append(dict(kind='stopped',actor=actor,turn=self.turn,key=pending['key'],reason=d.get('failure') or d['status']));return
        if kind=='read':
            self.events.append(dict(kind='processed',turn=self.turn,actor=actor,delivery=pending['delivery'],source=pending['source'],key=pending['key']))
            if pending.get('after'):
                own['phase']=pending['after']
                if pending['after']=='inspect_shared':own['shared_target']=pending['source']
        elif kind=='theorize':
            self._publish(actor,d['public.0']);own['phase']='await' if own['cycles']==0 else 'done'
        elif kind=='apply':
            own['used']=(*own['used'],pending['source']);own['cycles']+=1;own['phase']='inspect' if own['forward'] else 'done'
            for observer in self.actors:
                if observer!=actor:self.observe(observer,d['result'],actor)
        elif kind in ('inspect','inspect_shared'):
            key=self.key(actor,'self-observation');obs=self.engine.deliver_event(key,d['result'],actor)
            self.queues[actor].append(dict(key=key,source=obs,sender=actor,kind='observation',after='embody'))
            own['observation']=obs;own['phase']='reading_observation'
        elif kind=='embody':own['retained']=d['binding'];own['phase']='reframe'
        elif kind=='reframe':own['phase']='forward'
    def step(self):
        actor=self.actors[self.turn%len(self.actors)];turn=self.turn;self.turn+=1
        native_before=len(self.engine.world.journal())
        before={a:self.engine.wallet(a)['energy'] for a in self.actors}
        action='idle'
        if actor in self.active:
            p=self.pending[actor]
            if p:
                d=self.engine.job_status(actor,p['key'])
                if d['status'] in ('succeeded','failed','cancelled'):
                    self.pending[actor]=self._finish(actor,p,d);action='finish'
                elif d['status']=='ready':
                    self.engine.commit('commit:'+p['key'],actor,p['key']);action='commit'
                elif min(self.engine.wallet(actor)[k] for k in ('energy','time'))==0:action='exhausted'
                else:
                    self.engine.advance('advance:'+str(turn),actor,p['key'],self.quantum);action='work'
            elif self.queues[actor]:
                msg=self.queues[actor].pop(0);key=self.key(actor,'read')
                r=OperationRequest(key,actor,'read',ROOM,delivery=msg['key']);self.engine.start('start:'+key,r)
                self.pending[actor]=dict(key=key,kind='read',delivery=msg['key'],source=msg['source'],after=msg.get('after'));action='start_read'
            else:
                choice=proposal(self.engine.participant_view(actor),deepcopy(self.own[actor]))
                if choice:
                    try:self._start_choice(actor,choice);action='choose'
                    except ValueError as exc:
                        self.rejections.append(dict(turn=turn,actor=actor,reason=str(exc),choice=choice));self.own[actor]['phase']='stopped';action='refused'
        charged={a:before[a]-self.engine.wallet(a)['energy'] for a in self.actors}
        if any(v for a,v in charged.items() if a!=actor):raise ValueError('foreign payer charged')
        self.events.append(dict(kind='turn',turn=turn,actor=actor,action=action,spent=charged[actor],native_before=native_before,native_after=len(self.engine.world.journal())))
        return action
    def run(self,turns=600):
        if type(turns) is not int or turns<0:raise ValueError('bounded integer horizon')
        for _ in range(turns):self.step()
        return self
    def data(self):
        return dict(schema=self.SCHEMA,engine=self.engine.checkpoint(),actors=self.actors,types=tuple(self.types[a] for a in self.actors),quantum=self.quantum,
            edges=tuple(sorted(self.edges)),turn=self.turn,serial=self.serial,events=tuple(self.events),sent=tuple(sorted(self.sent)),queues=tuple(self.queues.items()),pending=tuple(self.pending.items()),own=tuple(self.own.items()),active=tuple(sorted(self.active)),rejections=tuple(self.rejections),observations=tuple(sorted(self.observations)),shell_phase=self.shell_phase)
    def checkpoint(self):return dumps(self.data())
    @classmethod
    def restore(cls,text):
        d=loads(text)
        expected={'schema','engine','actors','types','quantum','edges','turn','serial','events','sent','queues','pending','own','active','rejections','observations','shell_phase'}
        if set(d)!=expected or d['schema']!=cls.SCHEMA:raise ValueError('unknown field schema')
        e=CruxShellEngine.restore(d['engine']);obj=cls(e,d['actors'],d['types'],None,d['edges'],d['quantum'])
        for k in ('turn','serial','shell_phase'):setattr(obj,k,d[k])
        for k in ('queues','pending','own'):setattr(obj,k,dict(d[k]))
        obj.events=list(d['events']);obj.sent=set(d['sent']);obj.active=set(d['active']);obj.rejections=list(d['rejections']);obj.observations=set(d['observations'])
        if type(obj.turn) is not int or obj.turn<0 or type(obj.serial) is not int or obj.serial<0:raise ValueError('invalid cursor')
        return obj
