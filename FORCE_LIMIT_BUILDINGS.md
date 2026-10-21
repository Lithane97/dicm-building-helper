# Army and navy force-limit buildings

Implementation is wired into Building Helper selections 12â€“15, shared candidate
ordering, absolute minimum, treasury percentage, new/upgrade previews, normal
construction payment checks, and existing result reporting.

| Building | Unlock | Flat contribution | Base cost | Upgrade from |
|---|---|---:|---:|---|
| Regimental Camp | MIL 8 | land +1 | 200 | none |
| Conscription Center | MIL 22 | land +2 | 400 | Regimental Camp |
| Shipyard | DIP 8 | naval +2 | 100 | none |
| Grand Shipyard | DIP 24 | naval +4 | 300 | Shipyard |

Constants verified against installed enabled Europa Expanded building definitions
and vanilla technology order. Upgrade gain is only the difference from the lower
tier; upgrade base costs subtract 200 for Regimental Camp or 100 for Shipyard.
New construction excludes either existing family tier; native can_build enforces
port and other legality requirements. Lower-tier selections do not enable upgrades.

Gain model, pending runtime validation:
1. Provincial contribution = (target flat bonus - existing tier bonus) *
   clamp(1 - native exported autonomy / 100, 0, 1).
2. Additional national capacity = provincial contribution *
   max(0, 1 + owner's land_forcelimit_modifier/naval_forcelimit_modifier).
3. Minimum/ranking use additional national capacity, retaining fractions.
   Diagnostic separately logs provincial contribution so a province-level native
   tooltip can be distinguished from national capacity. National percentage
   modifiers are uniform across owned provinces, so within-category order follows
   the autonomy-adjusted marginal flat contribution.

Arithmetic does not sample buildings or mutate development, resources or treasury.
Ship construction speed, repair bonuses, special ship availability and conditional
on-built rewards do not affect ranking. Normal queued construction still applies
native completion behavior. Fractional display/engine rounding and unusual
province-status interactions require native comparison rather than inference from
these offline checks.

New files: force_math_effects, force_pipeline_effects, force_triggers and native
force_check event. Existing live/preview dispatch, GUI availability, contextual
building notes and force-limit unit help updated. Previously validated manpower,
sailor and development formulas unchanged.

Offline checks: 4 force building checks, 4 resource building checks, and 10 existing
development/shared-script checks all pass. They cover installed costs/bonuses and
unlocks, consistent live/preview parameters, new/upgrade gates, fractional autonomy
and national multipliers, upgrade cost differences, and registered script balance.
They do not run EU4.

Runtime entry: restart EU4, load original advanced-tech disposable France baseline
without construction, stay paused, run dicm_bh_force_limit_check.txt. This hidden
native event reports six new/upgrade cases, restores UI settings/report, and logs
treasury drift. It neither queues buildings nor spends gold. Compare native costs
and provincial/national gains before testing construction and upgrade fixtures.

Status: integration complete. Initial gain/cost predictions confirmed by user; both lower-tier construction runs and upper-tier upgrades passed preview, budget, actual payment and saved-queue checks. Unusual province-status interactions have not each been runtime-tested.

First native force diagnostic: treasury drift0. Regimental Camp:81 sites, best zero-autonomy Mamaceqtaw, provincial+1/national+1.15/cost160. Conscription Center new:81 sites, provincial+2/national+2.3/cost320. Shipyard:28 sites, best zero-autonomy Ile Bourbon, provincial+2/national+2.3/cost80. Grand Shipyard new:28 sites, provincial+4/national+4.6/cost240. Land and naval national modifiers exported0.15, factor1.15. Both upgrade cases0 because no lower tiers exist. Evidence tools/validation/force_buildings_first_run.json and .log. Need native tooltip comparison, distinguishing provincial contribution from final national multiplier, then construction/upgrades.

User confirmed the initial force-limit predictions look correct, including provincial vs national values and costs. Prepared explicit test wrappers for Regimental Camp/Shipyard new construction and Conscription Center/Grand Shipyard upgrades, each using minimum0 and 1% treasury cap to exercise budget skips with fewer queued buildings. They log cached preview, actual count/payment/failures and measured treasury loss. New construction tests must reload the clean baseline between army/navy runs to prevent busy-site interference; this requirement follows the earlier resource test. Later upgrade fixture adds completed Camp in Paris183 and Shipyard in Aix201, only on owned empty/free family sites, without deducting gold. No production formulas changed this turn.

New construction tests PASSED independently from clean baseline. Regimental Camp: preview/actual6 projects,960 ducats, cap1000.7,75 budget skips,0 failures. Shipyard: preview/actual12 projects,960 ducats, cap1000.7,16 skips,0 failures. Saved queues verified: six at160 and twelve at80; each save totals960. Measured treasury losses equal estimates. Remaining cap40.7 cannot afford another project. Evidence tools/validation/force_new_builds.json and force_regimental_camp_build.log/force_shipyard_build.log. Next: reload clean baseline, add lower-tier upgrade fixtures in Paris/Aix and run force diagnostic.

Force upgrade fixtures verified: Paris completed Regimental Camp, Aix completed Shipyard. Exactly one upgrade each; new-build counts exclude those sites (army80/navy27). Paris Conscription Center: provincial+1, national+1.15, cost160. Aix Grand Shipyard: provincial+1.93 at autonomy3.5, national+2.219 (fixed-point truncation of2.2195), cost160. Treasury drift0. Evidence tools/validation/force_upgrade_fixture_check.json and .log. Next run both prepared upgrade construction tests on the independent Paris/Aix sites and save force_buildings_upgraded.

Both force upgrade construction tests PASSED: Conscription Center in Paris and Grand Shipyard in Aix each previewed/queued1 project, cost160, measured treasury loss160, zero failures. Saved queues verified in provinces183/201 at160 each. Evidence tools/validation/force_upgrades.json and force_conscription_center_upgrade.log/force_grand_shipyard_upgrade.log. This completes the army/navy force-limit building wiring milestone, including shared ranking/minimum/budget/previews and native construction/upgrades. All18 offline checks passed at implementation; no formula changes after runtime validation.
