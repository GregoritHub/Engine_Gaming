"""Full relevant release commands; prospective panel is in contracts/EG08."""
import pathlib,sys,json,hashlib
from verify_batch import run,ROOT,freeze
attempt=sys.argv[1]
native=['tests_u2.test_acceptance','tests_u2.test_controls','tests_u2.test_legacy_sequences','tests_u3.test_acceptance','tests_u3.test_controls',
 'tests_c5.test_shell_routes.ShellRouteTests.test_active_interruption_preserves_first_step_and_exact_resume',
 'tests_c5.test_shell_routes.ShellRouteTests.test_local_release_does_not_clear_another_target',
 'tests_c5.test_shell_routes.ShellRouteTests.test_raw_auditor_rejects_false_completion_endpoint_and_child',
 'tests_c5.test_shell_routes.ShellRouteTests.test_unsupported_effect_cannot_be_cleared']
script='import engine_gaming,unittest,sys;sys.path.insert(0,str(engine_gaming.SOURCE/"baseline"/"HLE_Rebuild_R21B")); suite=unittest.defaultTestLoader.loadTestsFromNames('+repr(native)+'); r=unittest.TextTestRunner(verbosity=2).run(suite);sys.exit(not r.wasSuccessful())'
commands=[[sys.executable,'-m','unittest','discover','-s','tests','-v'],
 [sys.executable,'-c',script],
 [sys.executable,'-m','unittest','discover','-s','vendor/socionics/baseline/HLE_Rebuild_R21B/tests','-t','vendor/socionics/baseline/HLE_Rebuild_R21B','-p','test_socion.py','-v'],
 [sys.executable,'tools/release_panel.py','evidence/EG08/'+attempt+'/panel'],
 [sys.executable,'tools/fresh_checkout.py']]
reuse=None
if '--tooling-recheck' in sys.argv:
    old=json.loads((ROOT/'evidence/EG08/attempt1/freeze.json').read_text())
    result=json.loads((ROOT/'evidence/EG08/attempt1/result.json').read_text())
    current=freeze()
    relevant=lambda files:{p:h for p,h in files.items() if p.startswith(('engine_gaming/','tests/','contracts/'))}
    if relevant(current)!=relevant(old['files']) or not result['source_unchanged'] or any(result['results'][i]['exit_code']!=0 for i in (0,2)):
        raise ValueError('previous passing tests do not identify this exact runtime/test/contract candidate')
    reuse=dict(previous='evidence/EG08/attempt1',commands=(0,2),game_methods=43,sealed_social_methods=32,exact_game_test_contract_hashes=relevant(current),source_commit=old['source_commit'])
    commands=[commands[i] for i in (1,3,4)]
code=run('EG08',attempt,commands)
if reuse:
    out=ROOT/'evidence/EG08'/attempt
    current_manifest=json.loads((out/'freeze.json').read_text())
    assert current_manifest['source_commit']==reuse['source_commit']
    (out/'reused_checks.json').write_text(json.dumps(reuse,indent=2)+'\n')
    (out/'SHA256.json').write_text(json.dumps({p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in out.iterdir() if p.is_file() and p.name!='SHA256.json'},indent=2)+'\n')
sys.exit(code)
