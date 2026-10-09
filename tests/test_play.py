import unittest,tempfile,pathlib,json,time
from engine_gaming.session import Session
from engine_gaming.__main__ import command
from engine_gaming.play import player_snapshot,render
from engine_gaming.scenario import ref
from engine_gaming.world_adapter import from_store,Projection
from hle_unified.material import attrs

class Play(unittest.TestCase):
    def test_playable_path_views_and_further_informed_choice(self):
        s=Session();lines=[]
        for text in ('propose 5','reflect','wait 600','board','inspect','wait 12','consume 1'):
            s,out=command(s,text);lines.extend(('> '+text,out))
            self.assertNotIn('Could not finish',out)
        a=s.field.actors[0];d=player_snapshot(s)
        self.assertEqual(d['cycles'],1);self.assertEqual([m['cap'] for m in d['models']],[1])
        self.assertEqual(attrs(s.field.engine.world.head(ref('alice-stock').identity))['consumed'],2)
        before=s.checkpoint()
        for mode in ('text','board'):
            out=render(s,mode);self.assertIn('unknown',out);self.assertNotIn('bryn-stock',out)
        self.assertEqual(before,s.checkpoint())
        snapshot,_=from_store(s.field.engine.world,aliases={'alice':a,'stock':ref('alice-stock').identity})
        formula=['atom','Owns',['const','alice'],['const','stock']]
        self.assertTrue(Projection(snapshot,'text').query(formula));self.assertTrue(Projection(snapshot,'board').query(formula))
        root=pathlib.Path('evidence/EG07')/('play-'+str(time.time_ns()));root.mkdir()
        (root/'transcript.txt').write_text('\n\n'.join(lines)+'\n')
    def test_save_load_and_privileged_commands_not_in_play(self):
        s=Session();s,_=command(s,'reflect');s,_=command(s,'wait 25')
        with tempfile.TemporaryDirectory() as tmp:
            path=pathlib.Path(tmp)/'game.json';s,_=command(s,'save '+str(path))
            with self.assertRaises(FileExistsError):command(s,'save '+str(path))
            restored,_=command(s,'load '+str(path));self.assertEqual(s.checkpoint(),restored.checkpoint())
        for text in ('truth','consume bryn 2','give-budget 100','change-world'):
            with self.assertRaises(ValueError):command(s,text)
    def test_initial_intention_changes_generated_consequence(self):
        s=Session()
        for text in ('propose 4','reflect','wait 600'):s,out=command(s,text)
        self.assertEqual([m['cap'] for m in player_snapshot(s)['models']],[0])
        self.assertEqual(attrs(s.field.engine.world.head(ref('alice-stock').identity))['consumed'],0)
    def test_invalid_and_competing_player_actions_refuse(self):
        s=Session();s,_=command(s,'reflect');s,_=command(s,'wait 1')
        s,out=command(s,'consume 1');self.assertIn('finish or cancel',out)
        with self.assertRaises(ValueError):command(s,'wait -1')
