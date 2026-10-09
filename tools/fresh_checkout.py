"""Prove a clean checkout works using the exact local Git objects offline."""
import pathlib,tempfile,subprocess,sys
ROOT=pathlib.Path(__file__).resolve().parents[1]
with tempfile.TemporaryDirectory(prefix='engine-gaming-clean-') as temp:
    target=pathlib.Path(temp)/'game'
    subprocess.run(['git','clone','--no-hardlinks','--branch','engine-gaming',str(ROOT),str(target)],check=True)
    subprocess.run(['git','config','submodule.vendor/socionics.url',str(ROOT/'vendor/socionics')],cwd=target,check=True)
    subprocess.run(['git','-c','protocol.file.allow=always','submodule','update','--init','--recursive'],cwd=target,check=True)
    commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=target/'vendor/socionics',text=True).strip()
    assert commit=='ab674a36e9234dcbf46634367bfc2b42b8b3cd18'
    result=subprocess.run([sys.executable,'-m','engine_gaming','--demo'],cwd=target,text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
    print(result.stdout);assert result.returncode==0 and 'Could not finish' not in result.stdout
    assert 'Received allocation limits: 1' in result.stdout and 'Consumed 1 supply units' in result.stdout
    print('CLEAN CHECKOUT PASSED; pinned inherited commit verified.')
