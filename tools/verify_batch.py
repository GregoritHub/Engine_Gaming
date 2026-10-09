"""Freeze first, execute declared commands without mutation, retain all outputs."""
import argparse, hashlib, json, pathlib, subprocess, sys, time
ROOT = pathlib.Path(__file__).resolve().parents[1]
def digest(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def freeze():
    paths = [p for folder in ('engine_gaming','tests','tools','contracts') for p in (ROOT/folder).rglob('*') if p.is_file() and '__pycache__' not in p.parts]
    return {str(p.relative_to(ROOT)):digest(p) for p in sorted(paths)}
def run(batch, attempt, commands):
    out=ROOT/'evidence'/batch/attempt;out.mkdir(parents=True,exist_ok=False)
    before=freeze()
    source=subprocess.check_output(['git','-C',str(ROOT/'vendor/socionics'),'rev-parse','HEAD'],text=True).strip()
    if subprocess.check_output(['git','-C',str(ROOT/'vendor/socionics'),'status','--porcelain'],text=True).strip():raise ValueError('modified inherited source')
    manifest={'source_commit':source,'files':before,'python':sys.version,'commands':commands}
    (out/'freeze.json').write_text(json.dumps(manifest,indent=2)+'\n')
    results=[]
    for i,command in enumerate(commands):
        start=time.monotonic()
        with (out/f'{i:02d}.log').open('w') as f:
            result=subprocess.run(command,cwd=ROOT,stdout=f,stderr=subprocess.STDOUT)
        results.append({'command':command,'exit_code':result.returncode,'seconds':time.monotonic()-start,'log':f'{i:02d}.log'})
    unchanged=before==freeze() and not subprocess.check_output(['git','-C',str(ROOT/'vendor/socionics'),'status','--porcelain'],text=True).strip()
    receipt={'passed':unchanged and all(r['exit_code']==0 for r in results),'source_unchanged':unchanged,'results':results}
    (out/'result.json').write_text(json.dumps(receipt,indent=2)+'\n')
    (out/'SHA256.json').write_text(json.dumps({p.name:digest(p) for p in sorted(out.iterdir()) if p.is_file()},indent=2)+'\n')
    print(json.dumps(receipt,indent=2));return 0 if receipt['passed'] else 1
if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('batch');parser.add_argument('attempt');parser.add_argument('tests',nargs='+');a=parser.parse_args()
    sys.exit(run(a.batch,a.attempt,[[sys.executable,'-m','unittest','-v',*a.tests]]))
