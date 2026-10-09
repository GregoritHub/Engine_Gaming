import unittest,json
from engine_gaming.session import Session,DEFAULT
from engine_gaming.fol import InvalidFormula,evaluate,EvaluationIncomplete
from engine_gaming.play import player_snapshot

class ReleaseControls(unittest.TestCase):
    def test_wrong_types_duplicate_identity_and_malformed_save(self):
        s=Session({**DEFAULT,'shell':'none'})
        s.act(dict(id='one',kind='advance',turns=1));before=s.checkpoint()
        with self.assertRaises(ValueError):s.act(dict(id='one',kind='advance',turns=True))
        self.assertEqual(before,s.checkpoint())
        for turns in (-1,True,1.5,1001):
            with self.assertRaises(ValueError):s.act(dict(id='bad',kind='advance',turns=turns))
        d=json.loads(before);d['results'][0]['ok']=False
        with self.assertRaises(ValueError):Session.restore(json.dumps(d))
        for text in ('[]','null','{"schema":"unknown"}','{bad','{"a":1,"a":2}'):
            with self.assertRaises(ValueError):Session.restore(text)
    def test_forged_budget_and_unknown_operations_reject(self):
        s=Session({**DEFAULT,'shell':'none'});d=json.loads(s.checkpoint());d['config']['budget']=4001
        with self.assertRaises(ValueError):Session.restore(json.dumps(d))
        before=s.checkpoint()
        with self.assertRaises(ValueError):s.act(dict(id='bad',kind='set_budget',amount=99999))
        self.assertEqual(before,s.checkpoint())
    def test_views_never_supply_foreign_inventory(self):
        s=Session({**DEFAULT,'shell':'none'});d=player_snapshot(s)
        self.assertNotIn('bryn',json.dumps(d));self.assertNotIn('cass',json.dumps(d))
        for key in ('world','truth','peer_memory','peer_inventory'):self.assertNotIn(key,d)
