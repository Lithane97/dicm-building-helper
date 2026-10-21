"""Coastal integration and ranking-policy checks; runtime validation is separate."""
from pathlib import Path
import re
import unittest
from sync_development_hooks import blocks

ROOT = Path(__file__).resolve().parents[1]
CONFIG = [(23, 'coastal_defence', 5, 100), (24, 'naval_battery', 12, 200)]

class CoastalChecks(unittest.TestCase):
    def test_installed_costs_and_unlocks(self):
        native = dict(blocks(Path('D:/SteamLibrary/steamapps/workshop/content/236850/2164202838/common/buildings/00_buildings.txt').read_text(encoding='utf-8-sig')))
        levels = [b for n,b in blocks(Path('D:/SteamLibrary/steamapps/common/Europa Universalis IV/common/technologies/dip.txt').read_text(encoding='utf-8-sig')) if n == 'technology']
        for _, building, tech, cost in CONFIG:
            self.assertRegex(native[building], rf'\bcost\s*=\s*{cost}\b')
            self.assertRegex(native[building], r'\bblock_slave_raid\s*=\s*yes')
            self.assertRegex(levels[tech], rf'\b{building}\s*=\s*yes')
        self.assertIn('make_obsolete = coastal_defence', native['naval_battery'])

    def test_dispatch_and_upgrade_boundary(self):
        for file, process in [('events/dicm_bh_trade.txt','construct'), ('common/scripted_effects/dicm_bh_estimate_effects.txt','estimate')]:
            script = (ROOT/file).read_text()
            for idx, building, tech, cost in CONFIG:
                call = f'dicm_bh_collect_coastal_candidates = {{ BUILDING = {building} BASE_COST = {cost} }}'
                self.assertEqual(script.count(call), 1)
                pos = script.index(call)
                self.assertIn(f'which = dicm_bh_selection value = {idx}', script[pos-300:pos])
                self.assertIn(f'dip_tech = {tech}', script[pos-200:pos])
                self.assertIn(f'dicm_bh_{process}_trade_candidates = {{ BUILDING = {building} }}', script[pos:pos+350])
        triggers = dict(blocks((ROOT/'common/scripted_triggers/dicm_bh_coastal_triggers.txt').read_text()))
        self.assertNotIn('value = 23', triggers['dicm_bh_coastal_upgrade_available'])
        self.assertIn('has_building = coastal_defence', triggers['dicm_bh_coastal_upgrade_available'])
        pipeline = (ROOT/'common/scripted_effects/dicm_bh_coastal_pipeline_effects.txt').read_text()
        for gate in ['has_port = yes', 'can_build = $BUILDING$', 'dicm_bh_trade_province_free = yes', 'owner = { has_country_flag = dicm_bh_trade_upgrade_mode }', 'NOT = { OR = { has_building = coastal_defence has_building = naval_battery } }']:
            self.assertIn(gate, pipeline)
        self.assertNotRegex(pipeline, r'\b(?:add_building|remove_building|add_treasury)\s*=')
        self.assertIn('which = dicm_bh_trade_old_cost value = 100', pipeline)

    def test_actual_selector_orders_tiers_before_development(self):
        # Evaluate the exact comparison shape against adversarial score pairs.
        body = dict(blocks((ROOT/'common/scripted_effects/dicm_bh_trade_candidate_effects.txt').read_text()))['dicm_bh_select_best_trade_candidate']
        comparison = dict(blocks(dict(blocks(body))['every_owned_province']))['else_if']
        limit = dict(blocks(comparison))['limit']
        primary, alternatives = list(blocks(limit))
        self.assertEqual(primary[0], 'check_variable')
        self.assertIn('which = dicm_bh_trade_gain which = event_target:dicm_bh_trade_best', primary[1])
        self.assertEqual(alternatives[0], 'OR')
        terms = list(blocks(alternatives[1]))
        self.assertEqual([key for key,_ in terms], ['owner','NOT','check_variable'])
        self.assertIn('dicm_bh_coastal_selected = yes', terms[0][1])
        self.assertIn('is_variable_equal', terms[1][1])
        self.assertIn('which = dicm_bh_coastal_development which = event_target:dicm_bh_trade_best', terms[2][1])
        def replace(candidate, best, coastal=True):
            return candidate[0] >= best[0] and (not coastal or candidate[0] != best[0] or candidate[1] >= best[1])
        # More development never overrides a lower tier; within a tier it does.
        for candidate,best,expected in [((1,999),(2,1),False),((5,1),(4,999),True),((3,20),(3,10),True),((3,10),(3,20),False),((2,10),(2,10),True)]:
            self.assertEqual(replace(candidate,best), expected)
        self.assertTrue(replace((3,10),(3,20),False)) # Preserve other families' equal-score ties.

    def test_minimum_ui_and_raid_upgrade_policy(self):
        script = (ROOT/'common/scripted_effects/dicm_bh_coastal_pipeline_effects.txt').read_text()
        priority = dict(blocks(script))['dicm_bh_calculate_coastal_priority']
        highest = next(b for n,b in blocks(priority) if n == 'if')
        self.assertIn('dicm_bh_coastal_recently_raided = yes', highest)
        self.assertIn('NOT = { OR = { has_building = coastal_defence has_building = naval_battery } }', highest)
        self.assertIn('which = dicm_bh_trade_gain value = 5', highest)
        self.assertNotIn('multiply_variable', priority)
        gui = (ROOT/'common/custom_gui/dicm_bh_ui.txt').read_text()
        for mode in ('build','upgrade'):
            self.assertIn(f'dicm_bh_coastal_{mode}_available = yes', gui)
        ui = (ROOT/'common/scripted_effects/dicm_bh_ui_effects.txt').read_text()
        self.assertEqual(ui.count('category = coastal index = 11 default = 0 small = 1 large = 1'),2)
        self.assertIn('which = dicm_bh_saved_coastal which = dicm_bh_minimum', ui)
        data = (ROOT/'localisation/dicm_bh_l_english.yml').read_bytes()
        self.assertTrue(data.startswith(b'\xef\xbb\xbf'))
        self.assertNotIn(b'\n',data.replace(b'\r\n',b''))

    def test_trade_port_trigger_uses_native_script_syntax(self):
        trigger = dict(blocks((ROOT/'common/scripted_triggers/dicm_bh_coastal_triggers.txt').read_text()))['dicm_bh_coastal_valuable']
        native = Path('D:/SteamLibrary/steamapps/common/Europa Universalis IV/missions/99_EMP_Austrian_Missions.txt').read_text(encoding='utf-8-sig')
        expected = 'province_has_center_of_trade_of_level = 1'
        self.assertIn(expected, native)
        self.assertIn(expected, trigger)
        self.assertNotRegex(trigger, r'\bcenter_of_trade\s*=')

if __name__ == '__main__': unittest.main()
