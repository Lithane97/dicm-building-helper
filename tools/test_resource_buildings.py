"""Resource-building pipeline checks; native tooltip/payment comparison is separate."""
from pathlib import Path
import re
import unittest
from decimal import Decimal as D
from sync_development_hooks import blocks
ROOT = Path(__file__).resolve().parents[1]
CONFIG = [(8, 'barracks', 'barracks', 'training_fields', 'manpower', '0.5', 100, 'mil', 6),
          (9, 'training_fields', 'barracks', 'training_fields', 'manpower', '1', 300, 'mil', 16),
          (10, 'dock', 'dock', 'drydock', 'sailors', '0.5', 100, 'dip', 6),
          (11, 'drydock', 'dock', 'drydock', 'sailors', '1', 300, 'dip', 19)]
class ResourceBuildingChecks(unittest.TestCase):
    def test_preview_and_live_branches_match_installed_buildings(self):
        native = dict(blocks(Path('D:/SteamLibrary/steamapps/workshop/content/236850/2164202838/common/buildings/00_buildings.txt').read_text(encoding='utf-8-sig')))
        for file, process in [('events/dicm_bh_trade.txt', 'construct'), ('common/scripted_effects/dicm_bh_estimate_effects.txt', 'estimate')]:
            script = (ROOT / file).read_text()
            for idx, building, lower, upper, resource, bonus, cost, tech, level in CONFIG:
                call = f'dicm_bh_collect_resource_candidates = {{ BUILDING = {building} LOWER = {lower} UPPER = {upper} RESOURCE = {resource} BONUS = {bonus if bonus == "0.5" else "1"} BASE_COST = {cost} }}'
                self.assertEqual(script.count(call), 1)
                start = script.index(call)
                self.assertIn(f'which = dicm_bh_selection value = {idx}', script[start-300:start])
                self.assertIn(f'{tech}_tech = {level}', script[start-200:start])
                self.assertIn(f'dicm_bh_{process}_trade_candidates = {{ BUILDING = {building} }}', script[start:start+450])
                body = native[building]
                self.assertEqual(int(re.search(r'\bcost\s*=\s*(\d+)', body)[1]), cost)
                modifier = dict(blocks(body))['modifier']
                self.assertEqual(D(re.search(r'local_'+resource+r'_modifier\s*=\s*([\d.]+)', modifier)[1]), D(bonus))
                if building == upper:
                    self.assertIn('make_obsolete = '+lower, body)
    def test_upgrade_and_new_sites_are_disjoint(self):
        pipeline = (ROOT / 'common/scripted_effects/dicm_bh_resource_pipeline_effects.txt').read_text()
        self.assertIn('can_build = $BUILDING$', pipeline)
        self.assertIn('NOT = { has_building = $BUILDING$ }', pipeline)
        self.assertIn('owner = { has_country_flag = dicm_bh_trade_upgrade_mode }', pipeline)
        self.assertIn('has_building = $LOWER$', pipeline)
        self.assertIn('NOT = { OR = { has_building = $LOWER$ has_building = $UPPER$ } }', pipeline)
        self.assertIn('which = dicm_bh_trade_old_cost value = 100', pipeline)
        self.assertLess(pipeline.index('dicm_bh_calculate_resource_gain'), pipeline.index('dicm_bh_mark_trade_candidate'))
        triggers = dict(blocks((ROOT / 'common/scripted_triggers/dicm_bh_resource_triggers.txt').read_text()))
        for idx in (8, 10):
            self.assertNotIn(f'which = dicm_bh_selection value = {idx}', triggers['dicm_bh_resource_upgrade_available'])
        for mode in ('build', 'upgrade'):
            self.assertIn(f'dicm_bh_resource_{mode}_available = yes', (ROOT / 'common/custom_gui/dicm_bh_ui.txt').read_text())
    def test_gain_math_and_flat_resource_units(self):
        script = (ROOT / 'common/scripted_effects/dicm_bh_resource_math_effects.txt').read_text()
        self.assertNotRegex(script, r'\b(?:add_building|remove_building|add_treasury|add_manpower|add_sailors|add_base_\w+)\s*=')
        readers = dict(blocks(script))
        self.assertIn('value = modifier:local_manpower', readers['dicm_bh_read_manpower_basis'])
        self.assertIn('value = 1000', readers['dicm_bh_read_manpower_basis'])
        self.assertIn('value = 250', readers['dicm_bh_read_manpower_basis'])
        self.assertIn('value = modifier:local_sailors', readers['dicm_bh_read_sailors_basis'])
        for base, flat, bonus, old, autonomy, expected in [(4, 0, '.5', 0, 0, 500), (4, '.75', 1, '.5', 20, 700), (4, 0, '.5', '.5', 0, 0), (4, 0, 1, 0, 100, 0)]:
            gain = (D(base)*250+D(str(flat))*1000)*max(D(0),D(str(bonus))-D(str(old)))*max(D(0),min(D(1),1-D(autonomy)/100))
            self.assertEqual(gain,D(expected))
        # 10 development plus 500 flat sailors: new dock vs upgrade at 25% autonomy.
        basis = D(10)*60+500
        self.assertEqual(basis*D('.5')*D('.75'),D('412.5'))
        self.assertEqual(basis*(D(1)-D('.5'))*D('.75'),D('412.5'))
    def test_tech_unlocks_match_native_technology_order(self):
        for kind in ('mil', 'dip'):
            path = Path('D:/SteamLibrary/steamapps/common/Europa Universalis IV/common/technologies') / (kind+'.txt')
            technologies = [body for name, body in blocks(path.read_text(encoding='utf-8-sig')) if name == 'technology']
            for _, building, _, _, _, _, _, tech, level in CONFIG:
                if tech == kind:
                    self.assertRegex(technologies[level], r'\b'+building+r'\s*=\s*yes')
if __name__ == '__main__':
    unittest.main()
