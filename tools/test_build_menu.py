"""Selector unlocks and post-construction preview lifecycle regression checks."""
from pathlib import Path
import re
import unittest
from sync_development_hooks import blocks

ROOT = Path(__file__).resolve().parents[1]
GAME = Path('D:/SteamLibrary/steamapps/common/Europa Universalis IV')

class BuildMenuChecks(unittest.TestCase):
    def test_every_selector_requires_its_native_technology(self):
        unlocks = {}
        for category in ('adm', 'dip', 'mil'):
            levels = [body for name, body in blocks(
                (GAME/f'common/technologies/{category}.txt').read_text(encoding='utf-8-sig'))
                if name == 'technology']
            for level, body in enumerate(levels):
                for name in re.findall(r'(?m)^\s*(\w+)\s*=\s*yes\s*(?:#.*)?$', body):
                    unlocks.setdefault(name, []).append((category, level))
        selectors = {}
        for _, body in blocks((ROOT/'common/custom_gui/dicm_bh_ui.txt').read_text()):
            name = re.search(r'\bname\s*=\s*dicm_bh_select_(\w+)\b', body)
            if not name:
                continue
            category, level = unlocks[name[1]][0]
            self.assertEqual(len(unlocks[name[1]]), 1)
            trigger = dict(blocks(body))['trigger']
            self.assertRegex(trigger, rf'\b{category}_tech\s*=\s*{level}\b')
            selectors[name[1]] = (category, level)
        self.assertEqual(len(selectors), 36)
        self.assertEqual(selectors['temple'], ('adm', 4))
        self.assertEqual(selectors['cathedral'], ('adm', 19))

    def test_build_and_upgrade_refresh_after_construction_without_popup(self):
        events = {}
        for kind, body in blocks((ROOT/'events/dicm_bh_trade.txt').read_text()):
            if kind == 'country_event':
                identifier = re.match(r'\s*id\s*=\s*(\S+)', body)[1]
                events[identifier] = body
        for identifier in ('dicm_bh_trade.4', 'dicm_bh_trade.5'):
            self.assertIn('id = dicm_bh_trade.6', events[identifier])
        worker = dict(blocks(events['dicm_bh_trade.6']))['immediate']
        last_construction = max(m.start() for m in re.finditer(
            'dicm_bh_construct_trade_candidates', worker))
        self.assertLess(last_construction, worker.index('id = dicm_bh_estimate.1'))
        self.assertNotIn('dicm_bh_trade.2', events)
        self.assertNotIn('id = dicm_bh_trade.2', worker)
        for identifier, body in events.items():
            self.assertRegex(body, r'\bhidden\s*=\s*yes\b', identifier)
        refresh = next(body for name, body in blocks(
            (ROOT/'events/dicm_bh_estimate.txt').read_text()) if name == 'country_event')
        self.assertLess(refresh.index('dicm_bh_save_trade_report'),
                        refresh.index('dicm_bh_estimate_selected_trade_building = yes'))
        self.assertEqual(refresh.count('dicm_bh_estimate_selected_trade_building = yes'), 2)
        self.assertLess(refresh.index('dicm_bh_estimate_selected_trade_building = yes'),
                        refresh.index('dicm_bh_restore_trade_report'))
        # Churches and all other families share the construction-conflict gate.
        free = dict(blocks((ROOT/'common/scripted_triggers/dicm_bh_trade_triggers.txt').read_text()))['dicm_bh_trade_province_free']
        self.assertIn('has_construction = building', free)

if __name__ == '__main__': unittest.main()
