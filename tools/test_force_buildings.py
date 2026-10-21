"""Force-limit building integration checks. Native runtime comparison is separate."""
from pathlib import Path
import re
import unittest
from decimal import Decimal as D
from sync_development_hooks import blocks
ROOT = Path(__file__).resolve().parents[1]
CONFIG = [(12,'regimental_camp','regimental_camp','conscription_center','land',1,1,2,200,200,'mil',8),
          (13,'conscription_center','regimental_camp','conscription_center','land',2,1,2,400,200,'mil',22),
          (14,'shipyard','shipyard','grand_shipyard','naval',2,2,4,100,100,'dip',8),
          (15,'grand_shipyard','shipyard','grand_shipyard','naval',4,2,4,300,100,'dip',24)]
class ForceBuildingChecks(unittest.TestCase):
    def test_installed_constants_and_technology(self):
        native = dict(blocks(Path('D:/SteamLibrary/steamapps/workshop/content/236850/2164202838/common/buildings/00_buildings.txt').read_text(encoding='utf-8-sig')))
        for idx,building,lower,upper,kind,bonus,lb,ub,cost,lc,tech,level in CONFIG:
            body=native[building]
            self.assertEqual(int(re.search(r'\bcost\s*=\s*(\d+)',body)[1]),cost)
            modifier=dict(blocks(body))['modifier']
            self.assertEqual(int(re.search(r'\b'+kind+r'_forcelimit\s*=\s*(\d+)',modifier)[1]),bonus)
            if building==upper:self.assertIn('make_obsolete = '+lower,body)
            data=(Path('D:/SteamLibrary/steamapps/common/Europa Universalis IV/common/technologies')/(tech+'.txt')).read_text(encoding='utf-8-sig')
            levels=[b for n,b in blocks(data) if n=='technology']
            self.assertRegex(levels[level],r'\b'+building+r'\s*=\s*yes')
    def test_live_and_preview_dispatch_agree(self):
        for file,process in [('events/dicm_bh_trade.txt','construct'),('common/scripted_effects/dicm_bh_estimate_effects.txt','estimate')]:
            script=(ROOT/file).read_text()
            for idx,building,lower,upper,kind,bonus,lb,ub,cost,lc,tech,level in CONFIG:
                call=f'dicm_bh_collect_force_candidates = {{ BUILDING = {building} LOWER = {lower} UPPER = {upper} TYPE = {kind} BONUS = {bonus} LOWER_BONUS = {lb} UPPER_BONUS = {ub} BASE_COST = {cost} LOWER_COST = {lc} }}'
                self.assertEqual(script.count(call),1)
                pos=script.index(call)
                self.assertIn(f'which = dicm_bh_selection value = {idx}',script[pos-300:pos])
                self.assertIn(f'{tech}_tech = {level}',script[pos-200:pos])
                self.assertIn(f'dicm_bh_{process}_trade_candidates = {{ BUILDING = {building} }}',script[pos:pos+500])
    def test_new_upgrade_eligibility_and_no_preview_mutations(self):
        collector=(ROOT/'common/scripted_effects/dicm_bh_force_pipeline_effects.txt').read_text()
        for text in ['dicm_bh_trade_province_free = yes','can_build = $BUILDING$','NOT = { has_building = $BUILDING$ }','owner = { has_country_flag = dicm_bh_trade_upgrade_mode }','has_building = $LOWER$','NOT = { OR = { has_building = $LOWER$ has_building = $UPPER$ } }','which = dicm_bh_trade_old_cost value = $LOWER_COST$']:
            self.assertIn(text,collector)
        math=(ROOT/'common/scripted_effects/dicm_bh_force_math_effects.txt').read_text()
        self.assertNotRegex(collector+math,r'\b(?:add_building|remove_building|add_treasury|add_manpower|add_sailors|add_base_\w+)\s*=')
        triggers=dict(blocks((ROOT/'common/scripted_triggers/dicm_bh_force_triggers.txt').read_text()))
        for idx in (12,14):self.assertNotIn(f'which = dicm_bh_selection value = {idx}',triggers['dicm_bh_force_upgrade_available'])
        for mode in ('build','upgrade'):
            self.assertIn(f'dicm_bh_force_{mode}_available = yes',(ROOT/'common/custom_gui/dicm_bh_ui.txt').read_text())
    def test_marginal_capacity_and_cost_cases(self):
        script=(ROOT/'common/scripted_effects/dicm_bh_force_math_effects.txt').read_text()
        self.assertIn('value = modifier:$TYPE$_forcelimit_modifier',script)
        self.assertIn('which = dicm_bh_trade_gain which = dicm_bh_force_province_gain',script)
        self.assertIn('which = dicm_bh_trade_gain which = dicm_bh_force_country_factor',script)
        self.assertIn('subtract_variable = { which = dicm_bh_force_delta which = dicm_bh_force_old_bonus }',script)
        for target,old,autonomy,modifier,expected in [(1,0,0,0,'1'),(2,1,20,'.5','1.2'),(4,2,'3.5','.25','2.4125'),(1,0,100,'.5','0'),(4,0,-10,-2,'0')]:
            gain=max(D(0),D(target)-D(old))*max(D(0),min(D(1),1-D(str(autonomy))/100))*max(D(0),1+D(str(modifier)))
            self.assertEqual(gain,D(expected))
        for target,lower,expected in [(400,200,160),(300,100,160),(200,0,160),(100,0,80)]:
            self.assertEqual((D(target)-D(lower))*D('.8'),D(expected))
if __name__=='__main__':unittest.main()
