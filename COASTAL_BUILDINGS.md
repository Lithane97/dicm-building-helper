# Coastal Defence and Naval Battery

Implemented. Native new-construction and upgrade tests passed for 1792 France,
with costs, treasury and queues verified below. Strategic priority groups 4/5
have not been exercised in-game; recent-raid detection remains unvalidated.

Selections 23/24 use DIP technology 5/12 and base costs 100/200, checked against
the installed game and Europa Expanded. New construction requires neither family
member. Only Naval Battery can upgrade, from Coastal Defence, with the lower
building's 100 base cost deducted before applying the shared cost factor.

Preview and live actions share collection, minimum filtering and ordering.
The shared construction pipeline handles native construction, actual payments,
budget skips, failures and cost mismatch stops.

Priority (descending), with development breaking ties within each group:

5. Valuable, recently raided coast with neither family building.
4. Coastal capitals, and fortified islands or isolated strongholds.
3. Other coastal forts.
2. Valuable ports: development >=20, centre of trade, or river estuary.
1. Other eligible coast.

Recent raid evidence uses the native `slaves_raided` province modifier. This is
a deliberately limited exposure signal: it does not predict prospective raider
range, ability, religion restrictions, or diplomacy. Previously unraided exposed
coasts therefore rely on their other strategic attributes. The tooltip states
this limitation. A native test of the static modifier still remains necessary.

Islands use native `is_island`; isolated strongholds have no ROOT-owned land
neighbor. Both require an actual land-fort building. A multi-province island
with friendly land neighbors is not automatically classified as isolated.
Capital status does not require a constructed land fort.

Upgrades never receive group 5 merely for raid immunity: Coastal Defence already
provides that effect. No adjacency or sea-zone spacing restriction is imposed.
Tier and development are compared separately to prevent development from
overriding a higher tier or overflowing a packed score. Other building families
retain their existing equal-score behavior, including fort border ordering.

The independent coastal minimum defaults to 0 (all groups). Both +/- controls
change it by 1. Values above 5 exclude all candidates. Naval Battery upgrades can
reach at most group 4 with the current policy.

## Validation

`python -m unittest discover -s "DICM Building Helper/tools" -p "test_*buildings.py"`
checks installed costs/unlocks, dispatch consistency, eligibility, preview
mutation restrictions, priority comparison edge cases, UI and localisation.
The development suite also checks all registered script files for balanced
blocks and guards the existing development behavior.

Restart EU4 to register the new scripts and run:

`run dicm_bh_coastal_check.txt`

This diagnostic logs up to ten candidates in processing order for Coastal
Defence new, Naval Battery new and Naval Battery upgrade. It temporarily sets
the minimum to zero, preserves selection/settings/report and logs treasury
drift. It does not construct buildings or spend ducats. It modifies only helper
scratch variables/candidate flags. An empty upgrade pool is expected when no
Coastal Defence exists.

Next runtime checks: inspect the ordering and reasons against province state,
confirm static raid evidence on a raided province, compare native costs, then
validate a budgeted new build and an upgrade against queues and treasury.

### First runtime diagnostic, 1792 France

28 new sites for each tier; no upgrade sites; zero treasury drift. Aix led
the priority-3 fort group at 20 development, followed by Picardie at 15.
Nine fort sites preceded Bordeaux (priority 2, development 21), confirming
the group comparison outranked development. Predicted new costs were 80/160.

The error log exposed an invalid `center_of_trade` trigger in the valuable-port
test. Replaced it with `province_has_center_of_trade_of_level = 1`, as used in
native missions. Initial trade-port classification is not considered validated;
repeat the diagnostic after restarting. Evidence is in
`tools/validation/coastal_first_run.log` and `coastal_first_run_errors.log`.

### Corrected runtime diagnostic, 1792 France

Both new-building pools still contain 28 provinces and preserve descending
(priority, development) ordering. Predicted costs remain 80/160; upgrades have
no candidates. Treasury drift is zero. The invalid centre-of-trade trigger
errors are absent after restart. Hidden-event metadata warnings remain; these
are unrelated to ranking. This run does not exercise priority groups 4/5 or
actual construction payments. Evidence is in
`tools/validation/coastal_corrected_run.log` and `.json`.

Next: build Coastal Defence at minimum 0 and budget 1%, save as
`coastal_defence_new.eu4` while paused, then inspect actual cost and queues.

### Coastal Defence new-build test, 1792 France

Passed: 12 native construction queues at 80 each, total 960, from 28 eligible
provinces. Budget 1000.700; 16 budget skips; zero failures. Treasury fell from
100070.070 to 99110.070, exactly 960. All queued buildings have saved index 7.
Among all 28 evaluated provinces, no unqueued province outranks the lowest
queued (priority, development) pair. Equal-score ties are allowed.
Evidence: `tools/validation/coastal_defence_new.json` and `.log`; source save
`coastal_defence_new.eu4`. Naval Battery new and upgrade remain to be tested.

### Naval Battery new-build test, 1792 France

Passed: six queues at 160 each, total 960, out of 28 eligible provinces.
Budget 1000.700; 22 budget skips; zero failures. Treasury fell from 100070.070
to 99110.070, exactly 960. No unqueued province outranks the lowest selected
(priority, development) pair; equal-score ties are permitted.
Evidence: `tools/validation/coastal_battery_new.json` and `.log`; source save
`coastal_battery_new.eu4`.

Next: reload the original baseline; run `dicm_bh_coastal_upgrade_fixture.txt`
to add a completed Coastal Defence in Aix; select Naval Battery, minimum 0,
budget 1%, Upgrade, and save as `coastal_battery_upgrade.eu4` while paused.
Expected: one upgrade in Aix at 80 ducats. The fixture costs no gold and is
intended for a disposable test save. No restart is required for this run file.

### Naval Battery upgrade test, 1792 France

Passed: one Naval Battery upgrade queued in Aix (201), costing 80 ducats.
The save retains completed Coastal Defence and queues building index 12.
Priority is 3 (coastal fort). Eligible 1, successful 1, failures 0, skips 0.
Treasury fell from 100070.070 to 99990.070, exactly 80.
The actual action used a 100070 budget (100%), rather than the requested 1%;
this validates upgrade eligibility and payment, not the intended upgrade budget
limit. New-construction runs already exercised the shared budget at 1%.
Evidence: `tools/validation/coastal_battery_upgrade.json` and `.log`; source
save `coastal_battery_upgrade.eu4`.

Coastal Defence new, Naval Battery new, and Naval Battery upgrades are now
validated for this baseline. No further implementation change was needed.
Prospective raid exposure is deliberately not modeled, and groups 4/5 require
further runtime coverage before claiming every strategic category validated.

User subsequently verified construction on islands while playing Spain. Coastal priority refinements are deferred at the user's request.
