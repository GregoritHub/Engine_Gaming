"""Participant-only play views and a separate explicit truth inspector."""
import json
from .scenario import ref
from hle_unified.crossing_content import decode


def player_snapshot(session):
    f=session.field;a=f.actors[0];view=f.engine.participant_view(a)
    stock=ref(a.key+'-stock').identity
    sources={p.source for p in view.lookup() if p.source.identity==stock}
    current=max(sources,key=lambda r:r.revision) if sources else None
    details={p.address.key:p.value for p in view.resolve(current)} if current else {}
    quantity=details.get('quantity');consumed=details.get('consumed')
    remaining=quantity-consumed if type(quantity) is int and type(consumed) is int else None
    models=[]
    for p in view.lookup(key='payload'):
        try:d=decode(p.value)
        except (TypeError,ValueError):continue
        if d.get('kind')=='model':models.append(dict(source=p.source.identity.key,revision=p.source.revision,cap=d['cap']))
    return dict(player=a.key,turn=f.turn,budget=f.engine.wallet(a)['energy'],remaining=remaining,revision=None if current is None else current.revision,
                phase=f.own[a]['phase'],cycles=f.own[a]['cycles'],models=models,pending=bool(f.pending[a] or f.queues[a]),pattern_count=len(f.engine.pattern_view(a)))


def render(session,mode='text'):
    if mode not in ('text','board'):raise ValueError('unknown view')
    d=player_snapshot(session);stock='unknown' if d['remaining'] is None else str(d['remaining'])
    state={'initial':'Ready to propose','await':'Waiting for a reply','done':'Allocation returned','stopped':'Paused; inspect the situation or reconsider','inspect':'Checking remaining supplies','embody':'Learning from the observation','reframe':'Forming the next proposal','forward':'Preparing a new message','reading_observation':'Reading the observation'}.get(d['phase'],'Working')
    if d['pending']:state+='; work pending — advance turns to continue'
    messages=', '.join(str(x['cap']) for x in d['models']) or 'none received'
    if mode=='board':return '\n'.join(('WORKSHOP / ALICE',f'SUPPLIES  {stock}  |  WORK BUDGET  {d["budget"]}',f'TURN  {d["turn"]}  |  COMPLETED RETURNS  {d["cycles"]}',f'RECEIVED LIMITS  {messages}',f'STATE  {state}',f'Last known supplies revision: {d["revision"]}. Other inventories are unknown.'))
    return f'Alice · turn {d["turn"]}\nLast known supplies: {stock} (revision {d["revision"]}). Work budget: {d["budget"]}.\n{state}. Completed returns: {d["cycles"]}.\nReceived allocation limits: {messages}. Other inventories are unknown.'


def inspect_truth(session):
    from .field_audit import audit
    f=session.field
    return dict(mode='OMNISCIENT INSPECTOR — not player knowledge',interpretation=f.snapshot().data(),
                audit=audit(f.engine.world.journal(),f.engine.access.checkpoint(),f.data()))
