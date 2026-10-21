"""Offline structural/arithmetic checks. These do not substitute for EU4 parity tests."""
from pathlib import Path
import hashlib
import json
import re
import unittest
from sync_development_hooks import blocks, TOKEN, estate_effects

ROOT = Path(__file__).resolve().parents[1]


def tokens(text):
    return [m.group() for m in TOKEN.finditer(text) if not m.group().startswith('#')]


class DevelopmentSpendChecks(unittest.TestCase):
    def test_registered_scripts_are_balanced(self):
        for folder in ('common', 'events', 'customizable_localization'):
            for path in (ROOT / folder).rglob('*.txt'):
                with self.subTest(path=str(path)):
                    list(blocks(path.read_text(encoding='utf-8-sig')))

    def test_hooks_match_source_and_hashes(self):
        manifest = json.loads((ROOT / 'tools/development_hook_sources.json').read_text())
        expected = {kind: [] for kind in ('adm', 'dip', 'mil')}
        for source in manifest['sources']:
            path = Path(source['path'])
            self.assertEqual(hashlib.sha256(path.read_bytes()).hexdigest(), source['sha256'])
            if path.parent.name == 'on_actions':
                for name, body in blocks(path.read_text(encoding='utf-8-sig')):
                    match = re.fullmatch(r'on_(adm|dip|mil)_development', name)
                    if match:
                        expected[match[1]].extend(tokens(body))
        replay = dict(blocks((ROOT / 'common/scripted_effects/dicm_bh_development_hook_replay.txt').read_text()))
        for kind in expected:
            self.assertEqual(tokens(replay[f'dicm_bh_sp_replay_{kind}_hooks']), expected[kind])

    def test_literal_point_deductions_cover_every_supported_cost(self):
        events = (ROOT / 'events/dicm_bh_development_spend.txt').read_text()
        for idx, kind in ((11, 'adm'), (12, 'dip'), (13, 'mil')):
            worker = next(body for _, body in blocks(events)
                          if re.match(r'\s*id\s*=\s*dicm_bh_development_spend\.'+str(idx)+r'\b', body))
            pieces = [(int(a), int(b)) for a, b in re.findall(
                r'dicm_bh_sp_power_piece = \{ TYPE = '+kind+r' VALUE = (\d+) DELTA = (-\d+) \}', worker)]
            self.assertEqual(len(pieces), 11)
            for cost in range(1, 2048):
                remaining, deduction = cost, 0
                for value, delta in pieces:
                    if remaining >= value:
                        deduction -= delta
                        remaining -= value
                self.assertEqual((remaining, deduction), (0, cost))
            self.assertIn('which = dicm_bh_sp_after which = dicm_bh_dm_'+kind+'_reserve', worker)
            self.assertIn('owned_by = FROM', worker)
            self.assertNotIn(f'dicm_bh_sp_replay_{kind}_hooks = yes', worker)
            self.assertIn(f'province_event = {{ id = dicm_bh_development_spend.{idx+10} }}', worker)
            callback = next(body for _, body in blocks(events)
                            if re.match(r'\s*id\s*=\s*dicm_bh_development_spend\.'+str(idx+10)+r'\b', body))
            self.assertEqual(callback.count(f'dicm_bh_sp_replay_{kind}_hooks = yes'), 1)
            self.assertIn(f'has_province_flag = dicm_bh_sp_{kind}_replay_pending', callback)
            self.assertLess(callback.index('clr_province_flag'), callback.index(f'dicm_bh_sp_replay_{kind}_hooks'))
            self.assertLess(worker.index('add_base_'), worker.index('dicm_bh_sp_apply_institution_progress'))

    def test_institution_calculation_uses_pre_click_development_after_verification(self):
        helpers = dict(blocks((ROOT / 'common/scripted_effects/dicm_bh_development_spend_effects.txt').read_text()))
        effect = helpers['dicm_bh_sp_apply_institution_progress']
        remove = effect.index('add_base_$BASE$ = -1')
        institution = effect.index('add_next_institution_embracement_scaled = 5')
        restore = effect.index('add_base_$BASE$ = 1')
        self.assertLess(remove, institution)
        self.assertLess(institution, restore)
        self.assertEqual(effect.count('add_next_institution_embracement_scaled'), 1)
        self.assertIn('which = dicm_bh_sp_dev_before', effect[:institution])
        self.assertIn('which = dicm_bh_sp_dev_after', effect[restore:])
        events = (ROOT / 'events/dicm_bh_development_spend.txt').read_text()
        for kind, base, idx in (('adm', 'tax', 11), ('dip', 'production', 12), ('mil', 'manpower', 13)):
            worker = next(body for _, body in blocks(events)
                          if re.match(r'\s*id\s*=\s*dicm_bh_development_spend\.'+str(idx)+r'\b', body))
            call = f'dicm_bh_sp_apply_institution_progress = {{ BASE = {base} }}'
            self.assertIn(call, worker)
            self.assertLess(worker.index('which = dicm_bh_sp_raw_delta value = 1'), worker.index(call))
            after = worker[worker.index(call):]
            self.assertLess(after.index('which = dicm_bh_sp_status value = 1'), after.index('dicm_bh_sp_apply_side_effects'))
            self.assertNotIn('add_next_institution_embracement_scaled', worker)

    def test_devastation_rounds_once_and_dispatches_integers(self):
        helpers = dict(blocks((ROOT / 'common/scripted_effects/dicm_bh_development_spend_effects.txt').read_text()))
        effect = helpers['dicm_bh_sp_apply_side_effects']
        rounding = 'change_variable = { which = dicm_bh_sp_devastation_units value = 0.5 }'
        floor = 'round_variable = { which = dicm_bh_sp_devastation_units value = -1 }'
        self.assertLess(effect.index(rounding), effect.index(floor))
        self.assertLess(effect.index(floor), effect.index('dicm_bh_sp_devastation_piece'))
        pieces = [(int(a), int(b)) for a, b in re.findall(
            r'dicm_bh_sp_devastation_piece = \{ UNITS = (\d+) DELTA = (-\d+) \}', effect)]
        self.assertEqual(len(pieces), effect.count('dicm_bh_sp_devastation_piece ='))
        self.assertEqual(len(pieces), 7)
        for expected in range(101):
            remaining, total = expected, 0
            for units, delta in pieces:
                if remaining >= units:
                    remaining -= units
                    total -= delta
            self.assertEqual((remaining, total), (0, expected))
        # Half-up ties, observed Rennais case, and the devastation maximum.
        from fractions import Fraction
        for development, expected in ((3, 3), (13, 11), (14, 12), (120, 100), (121, 100)):
            reduction = min(Fraction(100), Fraction(development * 5, 6))
            self.assertEqual(int(reduction + Fraction(1, 2)), expected)

    def test_direct_observers_match_snapshot_helper(self):
        helpers = dict(blocks((ROOT / 'common/scripted_effects/dicm_bh_development_spend_effects.txt').read_text()))
        snapshot = ' '.join(tokens(helpers['dicm_bh_sp_watch_snapshot']))
        for mode in ('baseline', 'after'):
            script = (ROOT / f'dicm_bh_step_{mode}.txt').read_text()
            # Validate run-file structure as well as the complete embedded snapshot.
            list(blocks(script))
            self.assertIn(snapshot, ' '.join(tokens(script)))
            self.assertIn('province_from_counter', script)

    def test_estate_weight_tree_and_weighted_land_dispatch(self):
        manifest = json.loads((ROOT / 'tools/development_hook_sources.json').read_text())
        estates = manifest['estates']
        source = (ROOT / 'common/scripted_effects/dicm_bh_development_estate_effects.txt').read_text()
        self.assertEqual(source, estate_effects(estates))
        helpers = dict(blocks(source))

        # Interpret the actual generated decision tree, testing every supported floor.
        def read_weight(body, influence):
            if re.match(r'\s*set_variable', body):
                return int(re.search(r'value = (\d+)', body)[1])
            branches = list(blocks(body))
            threshold = int(re.search(r'influence = (\d+)', branches[0][1])[1])
            selected = branches[0][1] if influence >= threshold else branches[1][1]
            selected = re.sub(r'^\s*limit\s*=\s*\{.*?\}\s*\}', '', selected, count=1, flags=re.S)
            return read_weight(selected, influence)

        for influence in range(256):
            self.assertEqual(read_weight(helpers['dicm_bh_sp_read_estate_weight'], influence), influence)
        effect = helpers['dicm_bh_sp_apply_estate_land']
        last_snapshot = max(effect.index(f'which = dicm_bh_sp_weight_{e} which = dicm_bh_sp_estate_weight') for e in estates)
        self.assertLess(last_snapshot, effect.index('dicm_bh_sp_estate_land_piece'))
        from decimal import Decimal
        for estate in estates:
            pieces = [(int(u), Decimal(d)) for u, d in re.findall(
                r'dicm_bh_sp_estate_land_piece = \{ ESTATE = '+estate+r' UNITS = (\d+) DELTA = (-[\d.]+) \}', effect)]
            self.assertEqual(len(pieces), 8)
            for loss in range(201):
                remaining, total = loss, Decimal(0)
                for units, delta in pieces:
                    if remaining >= units:
                        remaining -= units
                        total -= delta
                self.assertEqual((remaining, total), (0, Decimal(loss) / 1000))
        reference = json.loads((ROOT / 'tools/validation/estate_influence_fraction_probe.json').read_text())
        weights = reference['proposed_whole_influence_weights']
        losses = {e: (w * 200 // sum(weights.values())) / 1000 for e, w in weights.items()}
        self.assertEqual(losses, reference['proposed_losses'])
        self.assertEqual(round(sum(losses.values()), 3), 0.199)
        one_estate = [0, 0, 100]
        self.assertEqual(sum(w * 200 // sum(one_estate) for w in one_estate), 200)
        self.assertIn('which = dicm_bh_sp_estate_total value = 1', effect)
        spender = (ROOT / 'common/scripted_effects/dicm_bh_development_spend_effects.txt').read_text()
        self.assertNotIn('estate = all share = -0.2', spender)
        self.assertIn('owner = { dicm_bh_sp_apply_estate_land = yes }', spender)

    def test_menu_batch_dispatch_and_read_only_observers(self):
        events = (ROOT / 'events/dicm_bh_development_spend.txt').read_text()
        self.assertNotRegex(events, r'\bwhile\s*=')
        gui = (ROOT / 'common/custom_gui/dicm_bh_development_ui.txt').read_text()
        for idx, kind in enumerate(('adm', 'dip', 'mil'), 1):
            button = next(body for _, body in blocks(gui)
                          if f'name = dicm_bh_dev_{kind}_spend' in body)
            self.assertNotIn('always = no', button)
            self.assertIn(f'country_event = {{ id = dicm_bh_development_batch.{idx} }}', button)
            self.assertIn('NOT = { has_country_flag = dicm_bh_db_running }', button)
            self.assertIn('NOT = { has_country_flag = dicm_bh_dm_scan_failed }', button)
        for idx in (90, 91):
            observer = next(body for _, body in blocks(events)
                            if re.match(r'\s*id\s*=\s*dicm_bh_development_spend\.'+str(idx)+r'\b', body))
            self.assertNotRegex(observer, r'\b(?:add_base_\w+|add_\w+_power|add_devastation)\s*=')

    def test_batch_reranks_and_stops_on_failure_or_attempt_limit(self):
        batch = (ROOT / 'common/scripted_effects/dicm_bh_development_batch_effects.txt').read_text()
        self.assertEqual(batch.count('while = {'), 1)
        self.assertIn('NOT = { check_variable = { which = dicm_bh_db_attempts value = 1000 } }', batch)
        self.assertLess(batch.index('set_country_flag = dicm_bh_db_running'), batch.index('while ='))
        self.assertLess(batch.index('change_variable = { which = dicm_bh_db_attempts value = 1 }'),
                        batch.index('country_event = { id = dicm_bh_development_spend.$STEP$ }'))
        self.assertIn('is_variable_equal = { which = dicm_bh_sp_dev_delta value = 1 }', batch)
        self.assertIn('check_variable = { which = dicm_bh_sp_spent value = 1 }', batch)
        # Any unsuccessful worker result clears the flag checked by the next loop.
        loop = next(body for name, body in blocks(dict(blocks(batch))['dicm_bh_sp_spend_batch'])
                    if name == 'if')
        self.assertIn('clr_country_flag = dicm_bh_db_continue', loop)
        self.assertIn('which = dicm_bh_db_stop value = 2', loop)
        self.assertIn('which = dicm_bh_db_stop value = 3', loop)
        self.assertIn('which = dicm_bh_db_spent which = dicm_bh_db_power_before', batch)
        self.assertIn('which = dicm_bh_db_spent which = dicm_bh_db_power_after', batch)
        self.assertNotRegex(batch, r'\b(?:add_base_\w+|add_\w+_power|add_devastation)\s*=')
        events = (ROOT / 'events/dicm_bh_development_batch.txt').read_text()
        single_events = (ROOT / 'events/dicm_bh_development_spend.txt').read_text()
        for idx, kind in enumerate(('adm', 'dip', 'mil'), 1):
            self.assertIn(f'dicm_bh_sp_spend_batch = {{ TYPE = {kind} STEP = {idx} }}', events)
            single = next(body for _, body in blocks(single_events)
                          if re.match(r'\s*id\s*=\s*dicm_bh_development_spend\.'+str(idx)+r'\b', body))
            self.assertIn(f'dicm_bh_sp_collect_target = {{ TYPE = {kind} }}', single)
            self.assertIn('NOT = { has_country_flag = dicm_bh_db_running }', single)

    def test_diagnostic_selection_stays_in_native_event_scope(self):
        events = (ROOT / 'events/dicm_bh_development_spend.txt').read_text()
        for kind, idx in (('dip', 92), ('mil', 93)):
            script = (ROOT / f'dicm_bh_step_{kind}_baseline.txt').read_text()
            self.assertIn(f'country_event = {{ id = dicm_bh_development_spend.{idx} }}', script)
            self.assertNotIn('dicm_bh_sp_site_supported', script)
            self.assertNotIn('dicm_bh_sp_collect_target', script)
            self.assertNotIn('estate_influence', script)
            observer = next(body for _, body in blocks(events)
                            if re.match(r'\s*id\s*=\s*dicm_bh_development_spend\.'+str(idx)+r'\b', body))
            self.assertIn(f'dicm_bh_sp_collect_target = {{ TYPE = {kind} }}', observer)
            self.assertIn(f'which = dicm_bh_dm_{kind}_reserve', observer)
            self.assertIn('set_province_flag = dicm_bh_sp_watched', observer)
            self.assertNotRegex(observer, r'\b(?:add_base_\w+|add_\w+_power|add_devastation)\s*=')


if __name__ == '__main__':
    unittest.main()
