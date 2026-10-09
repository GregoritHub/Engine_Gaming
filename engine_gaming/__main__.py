"""Run with python -m engine_gaming. Standard library only."""
import argparse,json,pathlib,shlex,sys,os
from .session import Session,DEFAULT
from .play import render,inspect_truth
from hle_unified.selection_records import dumps
HELP='''You are Alice in a shared workshop. Get an allocation reply that you can use.
Bryn and Cass form proposals from what their own work reveals.
Your past experience makes an available task feel as if it needs permission.
Try: propose 5, reflect, wait 600, inspect, wait 12, consume 1.
Work and supplies are finite. Reading, thinking and reconsidering cost work.

status / board       Show only your received information
propose N            Form an initial spending-limit intention
reflect              Reconsider your retained authorization pattern
wait N               Let the agents work for N turns (1–1000)
inspect              Pay to inspect your own supplies; wait to read the result
consume N            Use owned supplies through normal world validation
cancel               Stop your current work; spent resources stay spent
renew                Begin another allocation from actual retained experience
save PATH            Save the active field and history (new file only)
load PATH            Restore and verify a saved session
help / quit          Commands / exit
'''

def command(session,line,mode='text'):
    parts=shlex.split(line)
    if not parts:return session,''
    verb=parts[0].lower()
    if verb in ('status','board') and len(parts)==1:return session,render(session,'board' if verb=='board' else mode)
    if verb=='help' and len(parts)==1:return session,HELP
    if verb=='save' and len(parts)==2:
        p=pathlib.Path(parts[1]);p.parent.mkdir(parents=True,exist_ok=True)
        with p.open('x',encoding='utf-8') as out:out.write(session.checkpoint())
        return session,'Saved '+str(p)
    if verb=='load' and len(parts)==2:
        p=pathlib.Path(parts[1])
        if p.stat().st_size>32_000_000:raise ValueError('save exceeds 32 MB')
        session=Session.restore(p.read_text());return session,'Restored.\n'+render(session,mode)
    fields={'wait':'turns','propose':'cap','consume':'amount'}
    if verb in fields and len(parts)==2:extra={fields[verb]:int(parts[1])}
    elif verb in ('reflect','inspect','cancel','renew') and len(parts)==1:extra={}
    else:raise ValueError('Unknown command. Type help.')
    r=session.act(dict(id='play:'+str(len(session.commands)+1),kind='advance' if verb=='wait' else verb,**extra))
    return session,('Done.' if r['ok'] else 'Could not finish: '+r['error'])+'\n'+render(session,mode)

def main(argv=None):
    p=argparse.ArgumentParser(description='Finite agent workshop');p.add_argument('--load');p.add_argument('--view',choices=('text','board'),default='text');p.add_argument('--demo',action='store_true');p.add_argument('--inspect-truth',metavar='SAVE');args=p.parse_args(argv)
    if args.inspect_truth:
        path=pathlib.Path(args.inspect_truth)
        if path.stat().st_size>32_000_000:raise ValueError('save too large')
        print(dumps(inspect_truth(Session.restore(path.read_text()))));return 0
    s=Session.restore(pathlib.Path(args.load).read_text()) if args.load else Session()
    print(HELP);print(render(s,args.view))
    if args.demo:
        for line in ('propose 5','reflect','wait 600','board','inspect','wait 12','consume 1'):
            print('\n> '+line);s,out=command(s,line,args.view);print(out)
        return 0
    while True:
        try:line=input('\nworkshop> ')
        except (EOFError,KeyboardInterrupt):print();return 0
        if line.strip().lower()=='quit':return 0
        try:s,out=command(s,line,args.view);print(out)
        except (ValueError,OSError) as exc:print('Cannot do that:',exc)
if __name__=='__main__':sys.exit(main())
