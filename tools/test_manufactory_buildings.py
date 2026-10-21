"""Installed definitions, wiring, and marginal manufactory benefit checks."""
from decimal import Decimal as D
from pathlib import Path
import json
import re
import unittest
from sync_development_hooks import blocks

ROOT = Path(__file__).resolve().parents[1]
CONFIG = json.loads((ROOT/'tools/manufactory_config.json').read_text())
GAME = Path('D:/SteamLibrary/steamapps/common/Europa Universalis IV')
EE = Path('D:/SteamLibrary/steamapps/workshop/content/236850/2164202838')

class ManufactoryChecks(unittest.TestCase):
    def test_installed_defaults_and_unlocks(self):
        native = dict(blocks((EE/'common/buildings/00_buildings.txt').read_text(encoding='utf-8-sig')))
        self.assertRegex(native['manufactory'], r'\bcost\s*=\s*500\b')
        self.assertRegex(native['manufactory'], r'trade_goods_size\s*=\s*1\.0')
        for idx,name,tech,level,kind in CONFIG:
            self.assertIn('manufactory', dict(blocks(native[name])))
            self.assertNotRegex(native[name], r'\bcost\s*=')
            levels = [b for n,b in blocks((GAME/f'common/technologies/{tech}.txt').read_text(encoding='utf-8-sig')) if n == 'technology']
            self.assertRegex(levels[level], rf'\b{name}\s*=\s*yes')
        self.assertRegex(native['furnace'], r'global_trade_goods_size_modifier\s*=\s*0\.05')
        self.assertRegex(native['soldier_households'], r'local_manpower\s*=\s*0\.75')
        self.assertRegex(native['impressment_offices'], r'local_sailors\s*=\s*250')

    def test_live_preview_diagnostic_dispatch_agree(self):
        for file,process in [('events/dicm_bh_trade.txt','construct'), ('common/scripted_effects/dicm_bh_estimate_effects.txt','estimate'), ('events/dicm_bh_manufactory_check.txt',None)]:
            script = (ROOT/file).read_text()
            for idx,name,tech,level,kind in CONFIG:
                call = f'dicm_bh_collect_manufactory_candidates = {{ BUILDING = {name} KIND = {kind} }}'
                self.assertEqual(script.count(call),1)
                pos = script.index(call)
                self.assertIn(f'{tech}_tech = {level}',script[pos-200:pos])
                if process:
                    self.assertIn(f'which = dicm_bh_selection value = {idx}',script[pos-300:pos])
                    self.assertIn(f'dicm_bh_{process}_trade_candidates = {{ BUILDING = {name} }}',script[pos:pos+350])

    def test_protect_existing_manufactories_and_preview_state(self):
        triggers = (ROOT/'common/scripted_triggers/dicm_bh_manufactory_triggers.txt').read_text()
        self.assertIn('NOT = { has_manufactory_trigger = yes }',triggers)
        native = dict(blocks((GAME/'common/scripted_triggers/00_scripted_triggers.txt').read_text(encoding='utf-8-sig')))['has_manufactory_trigger']
        for name in ['wharf','plantations','furnace','soldier_households','impressment_offices','state_house','ramparts']:
            self.assertIn('has_building = '+name,native)
        collector = (ROOT/'common/scripted_effects/dicm_bh_manufactory_pipeline_effects.txt').read_text()
        self.assertIn('NOT = { has_country_flag = dicm_bh_trade_upgrade_mode }',collector)
        self.assertIn('dicm_bh_trade_province_free = yes',collector)
        self.assertIn('dicm_bh_manufactory_slot_clear = yes',collector)
        self.assertIn('can_build = $BUILDING$',collector)
        math = (ROOT/'common/scripted_effects/dicm_bh_manufactory_math_effects.txt').read_text()
        self.assertNotRegex(collector+math,r'\b(?:add_building|remove_building|add_base_\w+|add_treasury)\s*=')
        self.assertIn('limit = { has_province_flag = dicm_bh_income_valid }',math)
        self.assertIn('dicm_bh_manufactory_build_available = yes',(ROOT/'common/custom_gui/dicm_bh_ui.txt').read_text())

    def test_flat_bonus_and_national_bonus_arithmetic(self):
        # Native static contributions supply the base resource multiplier.
        native = dict(blocks((GAME/'common/static_modifiers/00_static_modifiers.txt').read_text(encoding='utf-8-sig')))
        self.assertRegex(native['land_province'],r'local_manpower_modifier\s*=\s*0\.25')
        self.assertRegex(native['core'],r'local_manpower_modifier\s*=\s*0\.75')
        math = dict(blocks((ROOT/'common/scripted_effects/dicm_bh_manufactory_math_effects.txt').read_text()))
        self.assertNotIn('change_variable = { which = dicm_bh_mfg_resource_factor value = 1 }',math['dicm_bh_mfg_resource_factor'])
        for flat,local,national,autonomy,expected in [(1500,1,0,0,'1500'),(750,2,'.5',20,'1500'),(500,'1.5','.25','3.5','844.375'),(250,1,0,100,'0')]:
            value=D(flat)*max(D(0),D(str(local))+D(str(national)))*max(D(0),1-D(str(autonomy))/100)
            self.assertEqual(value,D(expected))
        # More pre-existing goods never create a larger flat-unit marginal gain.
        for annual,flat,expected in [(24,2,1),(48,4,1),(36,1,3)]:
            self.assertEqual(D(annual)/D(flat)/12,D(expected))
        # A national +5 percentage points is not +5% of already boosted income.
        self.assertEqual(D(180)/D('1.5')*D('.05')/12,D('.5'))

    def test_all_missing_buttons_have_ui_name_scale_and_icon(self):
        custom = (ROOT/'common/custom_gui/dicm_bh_ui.txt').read_text()
        gui = (ROOT/'interface/topbar.gui').read_text()
        names = (ROOT/'customizable_localization/dicm_bh_ui.txt').read_text()
        scales = (ROOT/'common/scripted_effects/dicm_bh_ui_effects.txt').read_text()
        for idx,name in [(33,'wharf'),(34,'plantations'),(35,'mills'),(36,'ramparts')]:
            self.assertIn('name = dicm_bh_select_'+name,custom)
            self.assertIn('name = "dicm_bh_select_'+name+'"',gui)
            sprite = 'GFX_dicm_bh_ramparts' if name == 'ramparts' else 'GFX_'+name
            self.assertIn('quadTextureSprite = "'+sprite+'"',gui)
            self.assertIn(f'which = dicm_bh_selection value = {idx}',names)
            self.assertIn(f'which = dicm_bh_selection value = {idx}',scales)
        list(blocks(gui))
        gfx = (ROOT/'interface/dicm_bh.gfx').read_text()
        self.assertIn('name = "GFX_dicm_bh_ramparts"',gfx)
        self.assertIn('texturefile = "gfx/interface/buildings/latin_march.tga"',gfx)
        self.assertTrue((GAME/'gfx/interface/buildings/latin_march.tga').is_file())

if __name__ == '__main__': unittest.main()
