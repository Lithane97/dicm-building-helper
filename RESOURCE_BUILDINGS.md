# Manpower and sailor building integration

Implemented selections: 8 Barracks, 9 Training Fields, 10 Dock, 11 Drydock.
These existing buttons now use the shared Building Helper candidate ordering,
minimum, treasury percentage, independent new/upgrade previews, normal engine
construction, payment verification and report. No new tab or reserve setting.

| Building | Unlock | Base cost | Local bonus | Upgrade from |
|---|---|---:|---:|---|
| Barracks | MIL 6 | 100 | manpower +50% | none |
| Training Fields | MIL 16 | 300 | manpower +100% | Barracks |
| Dock | DIP 6 | 100 | sailors +50% | none |
| Drydock | DIP 19 | 300 | sailors +100% | Dock |

Constants checked against installed vanilla technology order and enabled Europa
Expanded building definitions. New construction excludes both family tiers.
Upgrades require the lower tier, exclude the upper tier, and use the marginal
+50% bonus and (300-100) base cost before the shared build-cost modifier. Selecting
the lower tier never enables Upgrade All. Port requirements use native can_build.

Gain model (basic Paris/Aix cases now confirmed against native tooltips):
- Manpower basis = base_manpower * 250 + exported local_manpower * 1000.
- Sailor basis = exported local_sailors, expected to include the development static
  modifier (60 sailors per total development) and flat local sources.
- Gain = basis * (target building bonus - existing tier bonus) *
  clamp(1 - exported autonomy / 100, 0, 1).
- Additive percentage bonuses cancel in the marginal gain. Flat sources such as
  Soldier's Households and Impressment Offices remain part of the basis.
- Rankings/minima count maximum capacity, not monthly recovery or current pools.
- Conditional completion rewards and special ship availability are excluded from
  rankings. Actual construction uses native add_building_construction so normal
  completion effects remain in force.

Implementation: common/scripted_effects/dicm_bh_resource_math_effects.txt and
resource_pipeline_effects, resource_triggers, live/preview dispatch branches,
GUI availability, and contextual help. The arithmetic effects do not mutate power,
resources, buildings, development or treasury. Gain formulas, particularly the
native local_sailors export, require native tooltip comparison before declaring
parity. Extreme modifier-floor interactions are not established by offline tests.

Validation: tools/test_resource_buildings.py passes 4 checks (dispatch parity,
installed constants/unlocks, new/upgrade gates, gain units/flat-source examples).
Existing tools/test_development_spend.py passes all 10 checks including balanced
registered scripts. These do not execute EU4.

Runtime diagnostic: restart to load events, use an advanced-tech disposable save,
stay paused and run dicm_bh_manpower_sailors_check.txt. It dispatches a hidden
native country event and reports the best supported new/upgrade site for each of
six cases with gain, cost, flat export, basis and autonomy. It restores the chosen
selection, minimum, budget and previous construction report; no construction,
building sampling, power or treasury mutations. Final log checks treasury drift.
Compare named provinces with the native macro builder, then test preview counts,
minimum filtering, budget skips and actual queued payments on a disposable save.

Status: integration complete. Four new-building gain/cost predictions matched native tooltips; normal lower-tier builds and both upgrades passed runtime preview/payment/construction checks. Special flat-bonus and extreme modifier cases have not each been runtime-tested.

First two native diagnostics executed in 1792 France, user first without money then with money. Both outputs identical and treasury drift 0. Barracks: 81 eligible, Paris +875 manpower/cost80; Training Fields new: 81 eligible, Paris +1750/cost240; upgrades0. Dock: 28 eligible, Aix +723.75 sailors/cost80, local_sailors export1500, autonomy3.5; Drydock new: 28 eligible, Aix +1447.5/cost240; upgrades0. These establish stable exported values and treasury-independent arithmetic, not native-tooltip parity. Results saved in tools/validation/resource_buildings_first_runs.json and .log. Next compare four new-building native gains/costs, accounting for display rounding; no construction needed yet.

User confirmed all four new-building native improvement values/costs align with diagnostic predictions (allowing display rounding). Prepared two explicit construction test run files: dicm_bh_test_barracks_build.txt and dicm_bh_test_dock_build.txt. Each selects its type, sets minimum 0 and treasury share 10%, logs cached preview count/cost/cap, invokes normal native Build All, then logs actual counts/cost/failures and measured treasury loss. These files spend gold and queue buildings; use only a disposable baseline. Also prepared but not yet requested for execution: dicm_bh_resource_upgrade_fixture.txt adds completed Barracks in owned Paris (183) and Dock in owned Aix (201), only if neither tier nor construction exists, for later upgrade tests. This fixture deducts no gold and should run only after reloading an unmodified disposable baseline.

New-construction first tests: Barracks preview/actual 81 projects and 6480 ducats, cap10007, zero failures, measured treasury loss6480. Dock immediately afterward correctly previewed/queued zero, cost0, because every owned site already had Barracks construction. Test instructions should have separated runs by reloading the initial baseline; simultaneous site eligibility is intentionally excluded. Barracks construction validated; Dock independent construction remains pending from unmodified baseline. Evidence tools/validation/resource_first_builds.json and resource_barracks_first_build.log/resource_dock_first_build.log.

Independent Dock construction PASSED after baseline reload: preview/actual 28 projects, 2240 ducats, cap10007, zero failures, measured treasury loss2240. Evidence tools/validation/resource_dock_build.json and .log. Next native diagnostic uses the completed lower-tier fixture in Paris/Aix to check marginal upgrade benefit and discounted cost before actual upgrades.

Upgrade fixture verified at runtime: completed Barracks in Paris and Dock in Aix added successfully. Native diagnostic finds exactly one upgrade per chain: Paris Training Fields gain875 cost160; Aix Drydock gain723.75 cost160; each bonus delta0.5, treasury drift0. New-build candidates correctly exclude the existing lower tiers (80 manpower/27 sailor provinces remain). Evidence tools/validation/resource_upgrade_fixture_check.json and .log. Prepared explicit normal-construction upgrade scripts for Training Fields/Drydock, each minimum0 and cap10%, matching their upgrade preview and measuring treasury loss. Independent sites permit consecutive tests without baseline reload between these two upgrade scripts.

Both upgrade construction tests PASSED: Training Fields in Paris preview/actual one project, cost160, measured loss160, zero failures; Drydock in Aix preview/actual one project, cost160, measured loss160, zero failures. Saved native construction queues confirmed in province183 and201 at cost160 each. Evidence tools/validation/resource_upgrades.json plus resource_training_fields_upgrade.log/resource_drydock_upgrade.log. Combined validation: native new-building gains/costs confirmed by user; Barracks81/cost6480 and Dock28/cost2240; both upgrades1/cost160; busy-site exclusion verified; treasury-independent diagnostics and drift0 verified. Existing 14 offline checks passed at implementation. Building Helper manpower/sailor category wiring milestone is complete.
