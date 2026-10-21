# Shared development evaluation

Status: initial evaluator and University integration validation passed in the tested French Revolution setup. University preview and construction use the shared evaluator. No automatic point spender is connected.

## Public entry points

- `dicm_bh_evaluate_development = yes`: province scope with the acting country as ROOT. Refreshes one owned, controlled, completed province.
- `dicm_bh_evaluate_country_development = yes`: country scope with country ROOT. Refreshes owned provinces and selects separate recommendations for each power type. Stops evaluating further provinces if the existing treasury-mismatch flag is raised.

No monarch power is spent, development is not changed, and no buildings are queued. Production income uses the existing synchronous native sample/refund helper; the net treasury must stay unchanged. Other benefit and cost calculations use exported modifiers. Only evaluation/sampler scratch state is written.

## Province outputs

| Variable prefix `dicm_bh_dev_` | Meaning |
| --- | --- |
| `cost`, `uni_cost`, `uni_saved` | Estimated next-click cost, hypothetical cost with University, and points saved per click |
| `adm_benefit`, `dip_benefit` | Estimated extra **annual** province tax/production ducats from one base-development point |
| `mil_benefit` | Estimated extra **maximum manpower**, not monthly recovery |
| `extra_goods` | Extra goods produced; not assumed to be collected trade income |
| `extra_governing` | Extra governing capacity used by one development point |
| `adm_score`, `dip_score`, `mil_score` | Respective benefit per 100 monarch points |
| `adm_uni_score`, `dip_uni_score`, `mil_uni_score` | Same benefit-per-power measure using the hypothetical University cost |
| `adm_uni_gain`, `dip_uni_gain`, `mil_uni_gain` | Improvement in the corresponding benefit-per-power score |

ADM/DIP scores measure annual ducats per 100 power. MIL measures maximum manpower per 100 power. **Do not add or compare scores across power types.** Governing cost is reported separately; no arbitrary conversion of governing capacity into ducats or manpower is imposed.

Flags `dicm_bh_dev_evaluated`, `dicm_bh_dev_adm_candidate`, `dicm_bh_dev_dip_candidate`, `dicm_bh_dev_mil_candidate`, and `dicm_bh_dev_production_supported` distinguish evaluated and supported results. Ineligible provinces have their public scores and benefits reset to zero. Basic category-balance gates reject a category whose base development already exceeds the other two combined. These are advisory gates, not a verified substitute for all native development legality rules.

## Cost model awaiting validation

`effective_base = 50 * max(.01, 1 + exported_national_development_cost_modifier - technology_reduction + local_development_cost_modifier)`

`discount_factor = max(.10, 1 + local_development_cost + national_development_cost + all_power_cost - capital_discount)`

`cost = max(1, floor(effective_base * discount_factor))`

Technology reduction uses native ADM levels 17/23/27, each granting .10. Europa Expanded inherits this technology file. Mods replacing these technology grants require updating this small table; no general technology-value export has been validated. Capital discount is `min(.50, total_country_development / 100 * .05)`, applied only to the capital. The country-development export was verified at 1041. Paris native cost is 83; the corrected calculation predicts 83 (76 with a hypothetical University), confirmed by the same-session read-only preview (83, University 76, efficiency -.30); the University prediction was subsequently verified against vanilla at 76.

The local export is expected to include terrain, existing University, development scaling and dynamic province effects. There is no duplicate hand-built terrain/development table. In-game diagnostics must verify this expectation and the placement of all-power modifiers. The hypothetical University subtracts .20 before the discount floor, only when a University is absent. All power types currently share this estimated cost; category-specific or exceptional native pricing is not presumed supported.

## Benefit model awaiting validation

- ADM: `(exported local tax modifier + country global tax modifier) * autonomy_factor`, annually for one base-tax point. The local export already includes the base/core contribution. Paris local 1 + national .35 gives 1.35 annually, or .1125 monthly, matching the native tooltip showing +.11. Other modifier combinations remain to be checked.
- DIP: `.20 * native annual production income / exported flat goods`. Paris estimated 1.331 annually matches native +.11 monthly. This preserves current price, goods modifiers, buildings and applied production autonomy. It assumes production income scales with flat goods; independent flat trade-value additions could require adjustment. Gold, trade companies or unavailable income samples have no DIP recommendation.
- MIL: `250 * (exported local manpower modifier + country global manpower modifier) * autonomy_factor`. The local export already includes the base/core contribution. Paris local 1 + national .25 gives 312.5, matching the native tooltip displaying +312. Other modifier combinations remain to be checked.
- Extra goods: `.20 * (1 + exported local goods modifier + country goods modifier)`.
- Governing cost: recompute the existing validated governing-cost formula at development +1, retaining percentage and flat floors.

Conditional effects on development/building completion, future building slots, institution progress, gold depletion and captured node-trade income are not monetized. University comparisons model the discount only; recalculate after an actual University or development change. Production follows the engine's applied autonomy cache, as established by the building tests.

## Country recommendations

`event_target:dicm_bh_dev_best_adm`, `_dip`, `_mil` hold the highest supported benefit-per-power candidates. Flags `dicm_bh_dev_best_adm_set`, `_dip_set`, `_mil_set` guard existence. Equal scores prefer the lower cost; exact ties preserve scan order.

`event_target:dicm_bh_dev_uni_adm`, `_dip`, `_mil` hold separately ranked legal University sites by improvement in that type's score. Flags `dicm_bh_dev_uni_adm_set`, `_dip_set`, `_mil_set` guard existence. No cross-power weighting, future click count or construction budget is silently assumed.

## Manual validation

Restart once to load these effects/events. Use native events, because trade-good conditions in console `run` files were demonstrated to return incorrect results in this installation.

1. `event dicm_bh_development_check.1`: evaluates the capital, displays its estimates and logs raw modifier inputs, scores and treasury drift. First compare the three native development-button costs and their benefit tooltips. Do not develop it before recording that baseline.
2. After the province model is validated, `event dicm_bh_development_check.2` scans and logs separate country recommendations. This also spends no points and reports treasury drift.

Do not connect this model to automatic spending or University construction until native checks pass. The future spender must re-evaluate after every successful click and verify native legality and actual point cost.

## Native validation record â€” Paris, 1792

After restart, the integrated event returned cost 83, hypothetical University cost 76, annual tax 1.35, annual production 1.331, maximum manpower 312.5 and treasury drift zero. These match the recorded vanilla cost 83, monthly tax +.11, monthly production +.11 and manpower +312. This validates this province case, not every modifier combination or country ranking. The extra-goods output has not been independently validated by the tooltip's base-goods line.

Next isolated test: `run dicm_bh_dev_university_test.txt` adds a University to the capital if absent and opens the native evaluation event. Compare the actual development-button cost with 76. It logs development before/after to detect any building-triggered development effects. `run dicm_bh_dev_university_cleanup.txt` removes only the marked test University and reruns the evaluator. Existing Universities are preserved. Both use startup-loaded native events for the evaluation.

University test confirmed: native cost dropped 83 -> 76; integrated evaluator returned cost 76, hypothetical cost 76 and further University saving zero. Development stayed 41, all estimated benefits stayed unchanged and treasury drift remained zero. Cleanup verified: University absent, vanilla and evaluator both returned to 83, benefits unchanged and treasury drift zero. Non-capital/country-ranking checks remain pending.

Country scan repeated twice: 81 provinces, zero treasury drift, identical targets (ADM/MIL Lille, DIP Metz; University ADM/MIL Lille, DIP Caux). Each invocation also produced one wrong-scope owned_by warning and one wrong-scope has_province_flag warning. Do not mark country ranking fully validated until these are isolated. A direct-scan probe bypassing the event window is prepared; its console context is for scope diagnosis only, not validating trade-good-dependent output.

Direct country-scan execution produced 81 evaluated provinces, zero drift and no additional scope warnings. This isolates the warnings to the visible native event path rather than the directly invoked scan. The .2 diagnostic now dispatches hidden worker .3 to execute and log the scan, leaving the visible event to show results. Restart and repeat .2 to verify this event-path change.

Hidden-worker verification passed after restart: event .2 evaluated 81 provinces, retained all six recommendations and treasury drift zero, with neither scope warning in the fresh error log. Next validation is Lille (4769), the ADM/MIL recommendation; the read-only Lille check logs cached inputs/results from the native scan for comparison with its native development tooltips.

Lille (4769) non-capital cost verified: native and cached evaluator both 30, development 11, autonomy 3.5%, local cost -.09, national cost -.05 and efficiency -.30. Hypothetical University cost 23 remains untested here. Native benefit comparison confirmed: annual tax 1.302 displays +.10 monthly, annual production 1.034 displays +.08 monthly and maximum manpower 301.562 displays +301. Thus the non-capital case and these benefit calculations at 3.5% autonomy match vanilla.

Initial shared-evaluator validation is complete for the tested French Revolution setup: Paris and Lille costs/benefits, Paris University discount and cleanup, stable country rankings, zero treasury drift and clean hidden-worker event execution. This supports proceeding to University integration and the separate development spender. It does not establish universal compatibility: technology efficiency uses the native 17/23/27 table; unsupported gold/trade-company production and special conditional building/development effects remain documented exclusions.


## University building integration

Selection 18 now supports Build All and cached budget previews at ADM tech 17.
Eligible, idle University sites with at least one estimated point saved are freshly evaluated.
For each power type, find the maximum positive `*_uni_gain` among these sites.
Each site's aggregate is `adm_gain/max_adm + dip_gain/max_dip + mil_gain/max_mil`.
A category with no positive maximum contributes zero. This gives equal weight to
all three categories, without adding raw ducat and manpower scores. The comparison
set is fixed before minimum/budget filtering, so a score of 3 means the site is best
in every supported category. Rankings are relative to the current eligible sites.
Unsupported DIP cases contribute zero; they do not invalidate ADM/MIL benefits.

The University minimum has a separate saved setting (default 0, steps 0.1/1).
The normal shared cost calculation uses base cost 300 and engine construction;
the treasury percentage cap, actual-payment tracking and mismatch stop are reused.
University upgrade preview remains zero and Upgrade All remains disabled.
No development or monarch power is spent. Conditional completion bonuses are excluded.

Verification after restarting EU4: select University, refresh estimates twice and
compare counts/costs; inspect `DICM BH UNIVERSITY CANDIDATE` lines in game.log and
check error.log. Set minimum above 3 to confirm zero projects, then restore it.
At a small treasury percentage, compare the preview to Build All on a disposable
save: queued count and actual spending should match, stay within cap, and never
queue at an occupied, already-building or existing-University site. Confirm upgrade
preview is zero. Re-run the development diagnostic to confirm no treasury drift
from previewing. Integration has received static checks only until this game test.

University integration first in-game preview: user reports treasury 5070, minimum 0, budget 10%; preview 2 buildings / 480 ducats, unchanged across repeated refreshes (within the 507 cap). Construction and minimum-filter tests remain pending. Candidate diagnostic fields were blank in game.log; logging now copies values to country scope and uses a named province target, following the established development diagnostic pattern. Restart required to verify corrected diagnostic output.

Minimum-filter verification passed: user confirmed minimum 4 yields zero projects/cost; restoring 0 returns 2 projects / 480 ducats; Upgrade All disabled. After restart, inline candidate logging still produced blank substitutions, so its scope-copy change is not a verified fix. Inline logger removed from source. Use `run dicm_bh_university_preview_check.txt` after a University preview to log cached site scores, costs, category gains and maxima directly, without recalculating trade-good-dependent benefits or changing treasury/construction. Ranking verification remains pending this probe.

Direct cached-score probe passed: 81 legal sites logged with valid names, costs and scores. Normalization maxima ADM 1.320, DIP 1.315, MIL 305.933 equal the maxima independently found among the logged sites. All 81 aggregate scores agree with independently recomputed normalized sums within 0.002423 (engine fixed-point/display precision). Leading sites: Lille 2.797, Avignon 2.631, Rennais 2.594, Caux 2.503, Auxerrois 2.134. Lille and Avignon each cost 240, predicting 2 projects / 480 at the tested 507 spending cap. Actual construction targets/payments remain to be verified on a test save.

Live University construction report confirmed by user and native BUILD RESULT log: eligible 81, projects 2, spending cap 507, actual spending 480, budget skips 79, failures 0. Matches preview exactly. Province-level queued log substitutions are blank in the pre-existing shared construction helper, so Lille/Avignon target confirmation remains pending direct inspection; totals alone do not prove the target provinces.

University construction target verification passed: user directly confirmed Universities under construction in Lille and Avignon. This completes the initial University integration validation for this setup: stable previews, independent aggregate-score checks across 81 sites, minimum filter, disabled upgrades, actual construction matching the 2-project / 480-ducat preview within the 507 cap, correct target provinces, and zero failed requests. Inline scripted-effect diagnostic substitutions remain unreliable; the direct cached-score probe works. This is validation of the tested setup, not universal compatibility or the separate automatic development spender.


## Development Helper menu

A new second vertical tab sits below Building Helper; EE's tab is third in all
three custom macrobuilder windows. The Development tab uses the native development
tab sprite. Tab switching excludes the other panels; closing/reopening through
the main macrobuilder button returns to Building Helper. Returning to EE refreshes
its cost predictions.

The menu has separate ADM/DIP/MIL previews and persistent point reserves (initially
500 each, steps of 50, floor zero). Opening the tab or clicking Refresh invokes
hidden native event `dicm_bh_dev_menu.1`, which scans with the shared evaluator and
copies best-next-click cost/benefit/score into independent menu cache variables.
Existing building report/settings are saved and restored around that scan. Treasury
drift is logged by the native event, outside scripted-effect log substitution.
Unavailable categories and sampler failures have explicit preview states.

Develop buttons are deliberately disabled in this menu-only implementation; no
monarch power or development is changed. Reserve settings are ready for the future
spender and do not filter the displayed benefit-per-power recommendation yet.

Static verification passed: balanced scripts, custom helper references, unique
localisation keys and UTF-8 BOM, scripted GUI bindings, tab order in all three
panels, measured sprite widths and preview worker native-effect exclusions.
In-game layout and runtime verification remain pending. Restart, switch through
Building Helper -> Development -> EE and back, check that only one panel appears,
that each +/-50 reserve is independent and retained, and that refresh updates the
three previews without changing treasury or monarch power. Check game.log for
`DICM BH DEVELOPMENT MENU REFRESH: treasury_drift=0` and error.log for new issues.

Development menu in-game UI verification passed: user confirmed tab switching, reserve increment controls and disabled Develop buttons. Default reserves changed to 500 ADM/DIP/MIL; the existing initialization guard preserves reserves already saved in a country. Existing saves can adjust each reserve with the menu controls. Preview-runtime/treasury-drift verification remains separate from these UI checks.

Native spender requirement confirmed: preserve full native development-click behavior. Investigation found no verified callable native action in the installed script/custom-GUI interfaces. Develop buttons remain disabled; no raw-development/point-deduction substitute added. See NATIVE_DEVELOPMENT_INTEGRATION.md for installed-interface evidence, remaining uncertainty and companion/native-UI versus manual architecture choices.

First scripted reproduction implemented after user authorization: single-step ADM/DIP/MIL events, reserve/payment/base-change checks, institution/devastation/crownland reproduction, and generated native/EE hook replay. GUI spending and bulk loops remain disabled pending native A/B parity checks. Read-only baseline `.90` and delta observer `.91` are prepared. See NATIVE_DEVELOPMENT_INTEGRATION.md for commands, guardrails, source synchronization and unresolved engine behavior. Four offline structural/arithmetic/source checks passed; no new in-game execution has been performed.

First reproduction baseline invocation (.90): no supported affordable ADM site above reserve; no step performed. Menu refresh logged zero treasury drift. Error log contains province-scope and undefined sp_target warnings on this path; eligibility/power cause not established. Direct read-only run probe dicm_bh_development_step_check.txt prepared to log power/reserve and cached evaluated/category/supported/affordable counts, protected-estate exclusions, then dispatch hidden baseline via country_event instead of a direct console event window.

After user added monarch power, baseline .90 selected Lille at estimated ADM cost 30. Baseline pools 999 each; tax/production/manpower 4/5/2, crownland 100, devastation 0, recorded counters 0. This establishes affordability with added points, not the full cause of the earlier rejection. Institution game-value exports failed (logged zeros invalid). Observer source corrected to numeric institution-state triggers: 100 complete, -1 partial, 0 absent; no claim to exact partial progress. Immediate-load direct console baseline/after scripts embed the corrected observer to avoid another restart and bypass direct-console-event preview warnings. Source changes to the native event observer take effect at next restart.

Native ADM A/B reference recorded for Lille from saved baseline: ADM -30, tax +1; DIP/MIL and production/manpower unchanged; native num_of_times_developed +1, EE num_of_adm_clicks +1, from_counter unchanged (0). Crownland remains capped at 100; devastation remains 0; all institutions complete and unchanged, so those active side effects are not validated by this case. Corrected direct observer reported all eight institutions complete (100). Native reference and raw log excerpt saved under tools/validation/native_lille_adm.json and .log before reload. Next: reload saved baseline, run dicm_bh_step_adm_once.txt then dicm_bh_step_after.txt, compare all recorded fields including from_counter.

First scripted Lille ADM step executed: status 1, observed cost 30, development gain 1, preview treasury drift 0. All direct-observer deltas match the saved native reference except country num_of_times_developed_var: native +0, scripted +1. Vanilla num_of_times_developed and EE num_of_adm_clicks both correctly +1. This is NOT full parity. Suspected event FROM scope mismatch; read-only dicm_bh_step_scope_check.txt prepared to inspect the watched province counter after a native click. Scripted delta and mismatch recorded in tools/validation/scripted_lille_adm_first.json. No scope correction applied until native province-counter evidence is collected.

Native scope probe observed Lille num_of_times_developed_var 0 -> 1 after native ADM development, confirming the missing province-local counter change. Hook replay moved to nested province events .21/.22/.23 so ROOT and FROM are both province scopes; payment-worker country FROM ownership checks remain unchanged. Pending province flags and active-owner flag guard callbacks, and flags clear before replay. Observers now log both counter locations. Correction awaits restart and repeat scripted comparison; bulk/menu spending still disabled.

Corrected Lille ADM comparison PASSED after restart: baseline exactly matches saved native baseline; all 20 observed deltas equal the native reference. Cost 30 ADM, tax +1, vanilla country counter +1, EE ADM counter +1, province-local FROM counter +1, owner-local FROM counter unchanged. Step status 1 and preview treasury drift 0. Evidence saved in tools/validation/scripted_lille_adm_corrected.json and .log. This validates the scope fix and this single-step case only: crownland is capped, devastation zero, institutions complete. Reserve refusal, DIP/MIL, active side effects and repeated spending remain unvalidated; menu/bulk controls stay disabled.

ADM reserve-refusal test PASSED: current ADM 969, user-set reserve 1000; status 0, spending 0, gain 0, all 20 observed deltas zero, menu refresh treasury drift 0. Evidence recorded in tools/validation/adm_reserve_refusal.json. Prepared immediate-load DIP/MIL baseline selectors and one-step dispatch files; benefits refresh via native menu event before cached console selection, preserving the known trade-good condition boundary. No restart needed for these new run files.

DIP baseline prepared: Metz, predicted cost 53 DIP, available DIP 999, tax/production/manpower 8/8/5, crownland 100, devastation 0, all institutions complete. Native development country counter currently 1, EE ADM counter 1, owner FROM counter 0, Metz province FROM counter 0. Native single-click DIP comparison remains pending. Baseline preserved in tools/validation/dip_metz_baseline.json.

Native Metz DIP reference recorded: DIP -53, production +1, native country development counter +1, province FROM counter +1, owner FROM counter unchanged; ADM/MIL, tax/manpower and EE ADM counter unchanged. Reference preserved in tools/validation/native_metz_dip.json and .log. Next reload saved DIP baseline and execute dicm_bh_step_dip_once.txt plus shared after observer.

Metz DIP single-step comparison PASSED: all 20 observed deltas match the saved native reference. Script status 1, 53 DIP paid, production +1, native and province counters +1, EE ADM counter unchanged, other power pools unchanged, preview treasury drift 0. Evidence stored in tools/validation/scripted_metz_dip.json and .log. This is the second category validated for basic point/development/hook behavior; active institution progress, crownland gains, devastation reduction, conditional EE bonuses, MIL and bulk execution remain unvalidated.

MIL comparison baseline prepared: Rennais, predicted cost 31 MIL, available MIL 999, tax/production/manpower 4/4/4, native country counter 2, EE ADM counter 1, province FROM counter 0. Baseline preserved in tools/validation/mil_rennais_baseline.json. Native click remains pending.

Native Rennais MIL reference recorded: MIL -31, base manpower +1, native country counter +1 and province FROM counter +1; other power pools, base categories, EE ADM and owner FROM counters unchanged. Evidence preserved in tools/validation/native_rennais_mil.json and .log. Scripted MIL comparison remains pending.

Rennais MIL comparison PASSED: all 20 observed deltas equal native reference; status 1, MIL -31, base manpower +1, native/province counters +1, all other observed deltas unchanged. Evidence preserved in tools/validation/scripted_rennais_mil.json and .log. Basic single-step point/development/hook parity now passed for ADM (Lille), DIP (Metz) and MIL (Rennais), plus ADM reserve refusal. Active crownland gain, nonzero devastation reduction, partial institution progress and conditional EE reward cases remain unvalidated before menu/bulk enablement.

Active devastation fixture baseline captured at Rennais: devastation 30, tax/production/manpower 4/4/5, MIL 968, refreshed estimated cost 34 (versus prior 31 without devastation), native country counter 3 and province FROM counter 1. Preserved tools/validation/devastation_rennais_baseline.json. Native reduction test pending; no reduction formula validated yet.

Native active-devastation reference recorded: Rennais MIL -34, base manpower +1, devastation delta -11.65; native/province development counters +1. Reference preserved in tools/validation/native_rennais_devastation.json and .log. Scripted fixed-site comparison remains pending.

Active devastation comparison FAILED fractional parity: native Rennais reduction 11.65 versus scripted 11, with all other observed deltas matching (34 MIL, manpower +1, correct hook counters). CWTools EU4 effect schema declares add_devastation as int, consistent with fractional literal pieces being discarded. Earlier proposed fixed-point fractional helper is not validated and does not overcome this effect limitation. Evidence saved as tools/validation/scripted_rennais_devastation_first.json and .log. User asked whether to exclude devastated provinces for exactness or allow rounded reduction. No policy change or menu/bulk enablement made pending that choice.

User authorized rounded devastation reduction. Implementation now rounds the estimated reduction once to the nearest integer (ties upward), caps at 100, then applies only integer native-effect denominations. Unsupported fractional-piece dispatch was removed. The preview tooltip states this approximation. For Rennais resulting development 14, expected rounded reduction is 12 (30 -> 18), intentionally different from native 11.65 (30 -> 18.35). Nearest-rounding and all integer dispatch totals 0..100 are checked offline; runtime rounded-policy test remains pending restart and repetition from the saved devastation baseline. Other native side-effect parity limitations remain unchanged.

Rounded devastation runtime test PASSED under the user-authorized approximation: Rennais status 1, 34 MIL spent, manpower +1, devastation -12 (30 -> 18), versus native -11.65. All other 19 observed deltas match the saved native reference; preview treasury drift 0. Evidence preserved in tools/validation/scripted_rennais_devastation_rounded.json and .log. Active crownland gain and partial institution progress still need comparison; menu/bulk controls remain disabled.

Active crownland baseline captured: 1444.11.11 France, Saintonge, crownland 30, power pools 999 each, tax/production/manpower 4/4/2, predicted MIL cost 51, counters zero. User saved baseline. Evidence in tools/validation/crownland_saintonge_baseline.json and .log. Native click comparison pending; institution state classes do not establish exact progress.

Native Saintonge crownland reference recorded: 51 MIL spent, manpower +1, crownland +0.198 percentage points (30 -> 30.198), native/province development counters +1; other observed deltas unchanged. Evidence saved in tools/validation/native_saintonge_crownland.json and .log. Scripted comparison from saved baseline remains pending.

Active crownland scripted comparison differs: native Saintonge +0.198 versus script +0.200; all other 19 observed deltas match, status 1, 51 MIL spent, manpower +1, preview treasury drift 0. Evidence saved in tools/validation/scripted_saintonge_crownland_first.json and .log. Installed ESTATE_CROWNLAND_FROM_DEV is 0.2. Per-estate native allocation/rounding needs inspection before changing the implementation; a universal 0.198 substitution is not established.

Three save files inspected directly: baseline estate shares church/nobles/burghers 12.500/53.750/3.750; native 12.454/53.631/3.717; scripted 12.463/53.597/3.740. Native losses 0.046/0.119/0.033 differ from scripted 0.037/0.153/0.010. Thus the aggregate 0.002 discrepancy is not merely a total-rounding issue. Evidence in tools/validation/crownland_estate_shares.json. Read-only dicm_bh_estate_influence_probe.txt prepared to test variable-valued estate_influence thresholds and inspect influence without world-state mutations; production behavior unchanged pending evidence.

Literal estate influence checks in direct console-run scope returned 255 for all three estates, an invalid result, consistent with earlier evaluator console-context limitations. No production correction made from these readings. Probe moved to hidden native country event dicm_bh_estate_probe.1 with a 0/1000 sanity check; same console wrapper now dispatches that event. Native-scope probe requires restart before use.

Native fractional influence probe: all 27 thresholds (integer floor + 0.000 through +0.999 for church/nobles/burghers) returned true, while integer floor+1 had returned false. This provides no usable sub-integer resolution. Variable thresholds already failed parsing. Whole-number influence proposal would deduct church/nobles/burghers 0.047/0.120/0.032, total crownland +0.199, versus native 0.046/0.119/0.033, total +0.198. Evidence saved in tools/validation/estate_influence_fraction_probe.json and .log. No production approximation enabled; user has approved rounding devastation only so far. Further exact reproduction would require another way to obtain or reconstruct full influence, not more fractional threshold probes.

User authorized whole-number influence weighting. Production side-effect helper now calls generated dicm_bh_sp_apply_estate_land in owner scope. It first snapshots every installed active estate weight with literal 0..255 integer thresholds in native event scope, then apportions 200 thousandths by weight, floors each estate deduction to a thousandth, and applies literal per-estate denominations. Zero total weight performs no land mutation. Negative influence and influence >=256 are excluded by the generated eligibility guard, alongside existing protected privileges. Estate definitions are resolved from enabled sources, hashed in the source manifest, and covered by generator synchronization. No direct console evaluation is used in production. Saintonge expected losses church/nobles/burghers: 0.047/0.120/0.032, total +0.199 crownland (native +0.198). Seven offline checks pass, including all 256 weight-tree leaves, all deduction totals 0..200 thousandths, snapshot-before-mutation ordering, source hashes and Saintonge arithmetic. Tooltip discloses the approximation. Runtime repetition requires restart; save weighted result for per-estate comparison. Bulk/menu controls remain disabled while institution progress and other side effects are still being validated.

Weighted crownland runtime test PASSED under accepted approximation: Saintonge status 1, 51 MIL spent, manpower +1, crownland +0.199. Saved estate shares church/nobles/burghers 12.453/53.630/3.718 confirm deductions 0.047/0.120/0.032 exactly match the proposal. Other 19 observed deltas match native; native crownland +0.198 remains intentionally different. Evidence preserved in tools/validation/scripted_saintonge_crownland_weighted.json and .log. Next validation: active institution progress on a post-1450 save where Renaissance is spawned and not complete in the selected province; compare exact save progress rather than the coarse institution-state observer.

Institution baseline attempt at 1453.05.29 is unsuitable: saved France country institution array and Saintonge province progress already show all ten installed current institutions embraced/complete. No active progress can be measured there. Also found a diagnostic regression: newly added estate numeric guards were invoked in direct-console DIP/MIL target selection and rejected every site. Replaced those diagnostic selectors with native hidden country events .92 DIP/.93 MIL (cloned read-only ADM .90), retaining the existing direct observation body. Production selection already executes natively and is unchanged by this fix. A fresh early-date start and restart to load these diagnostic events are required.

CORRECTION to earlier institution-save interpretation: saved institution arrays contain legacy slots before the active EE institution slots; ten leading completed values do NOT mean ten current institutions are complete. In this installation the observed active feudalism/Renaissance positions are 8/9 (zero-based), with earlier slots not to be treated as current institutions. EE 00_ME_Override.txt Renaissance history explicitly grants it throughout Europe from 1450, explaining French complete Renaissance in a fresh 1453 start. Earlier claim of later-date contamination and need for a fresh restart was unsupported. Latest 1453 save has Morocco not embracing Renaissance, Tangiers at 2.044 province progress; switch to MOR in the same paused disposable save to obtain an active native institution test. Native MIL baseline selector .93 is loaded and works (selected Alencon for France); diagnostic console selector regression is resolved. Next: tag MOR, powerpoints, native MIL baseline, save institution_baseline; inspect exact progress before comparison.

Native Tangiers institution reference captured: Renaissance 2.044 -> 3.374, gain 1.33 percentage points; MIL delta -40.0, manpower delta 1.0, crownland delta 0.192. Exact progress read from saved province institution slot 9, rather than coarse observer class. Evidence in tools/validation/native_tangiers_institution.json and .log. Scripted comparison from institution_baseline pending.

First active institution comparison FAILED exact progress: Tangiers native Renaissance gain 1.330 (2.044 -> 3.374), scripted 1.500 (2.044 -> 3.544); all 20 coarse observed deltas match, including 40 MIL, manpower +1, crownland +0.192 and counters. Precise save comparison exposes the difference that institution classes miss. Evidence preserved in tools/validation/scripted_tangiers_institution_first.json and .log. Scaled effect executed after +1 appears to count an additional next point. Corrected helper runs only after payment/base +1 verification, temporarily removes that same base point, verifies pre-click development, calls the engine scaled institution effect once, then restores the point and verifies final development. This retains no-institution-mutation behavior for an initially failed base +1. Helper uses literal base effects, whose lack of native hook dispatch was already observed; hooks replay only once after restoration. Unexpected sampling/restoration reports status 3 and suppresses remaining manual side effects/replay. All nine offline checks pass. Runtime repeat from institution_baseline after restart is pending; expected Renaissance 3.374, not yet established.

Corrected Tangiers institution runtime comparison PASSED: Renaissance 2.044 -> 3.374, gain 1.330 exactly equals native, full saved institution vector matches, status 1, all 20 observed deltas match (40 MIL spent, manpower +1, crownland +0.192, native/province counters +1). Evidence preserved in tools/validation/scripted_tangiers_institution_corrected.json and .log. Single-step basic ADM/DIP/MIL, reserve refusal, accepted rounded devastation/weighted estates, and this active institution case are now covered. Prepared immediate-load dicm_bh_step_mil_three.txt: three existing native .3 event attempts, each reranks and rechecks reserves; no new bulk loop/menu enablement yet. Next runtime uses institution_baseline and saves development_three_steps for full province/base/counter/institution inspection.

Three successive native MIL worker calls PASSED in Morocco: Tangiers selected each time, 40 MIL per click, 120 total spent, 999 -> 879 MIL, manpower 1 -> 4, native development counter +3, ADM/DIP unchanged, reserve 500 retained. Full-save province comparison found only Tangiers manpower changed. Evidence tools/validation/morocco_three_steps.json and .log.

Menu batch implementation now wired: native country events dicm_bh_development_batch.1/.2/.3 call shared country batch helper with matching single-step .1/.2/.3. Each attempt re-evaluates/reranks natively and rechecks payment/reserve via the verified worker; no affordable supported target finishes normally, any unexpected worker status/zero payment/wrong delta stops immediately, and 1,000 attempts is a hard bound. Running flag prevents reentry. Final spending is measured from actual power pools rather than summing possibly refunded deductions. Redundant per-step menu refresh is skipped during a batch, then one final native refresh restores recommendations. Three Develop buttons now dispatch these events; footer shows type/increases/points spent/remaining/reserve, with stop reason on hover. Existing reserves and default 500 retained. Accepted devastation and estate approximations appear in the spending tooltip. Ten offline checks pass; full reserve-exhaustion loop and actual menu activation still need runtime verification after restart. Next: reload institution_baseline as Morocco, Develop MIL once, save development_batch_mil, verify pool stays >=500 and no further affordable supported click.

Full MIL menu batch PASSED in Morocco: 11 verified increases, 483 MIL spent, remaining 516 against reserve 500, stop code 1. Saved province changes are exclusively base manpower, summing +11; country native development counter +11, ADM/DIP unchanged. Cheapest remaining evaluated MIL candidate costs more than the remaining 16 spendable points. Evidence tools/validation/morocco_mil_batch.json and .log. User reported footer unlocalized: dynamic footer instantTextBox lacked scripted = yes, unlike working preview/reserve text boxes. Added that flag; localization key/custom text registration already present. Runtime footer check can load development_batch_mil after restart, without spending again.

User verified footer fix in game by reloading the window and topbar.gui; dynamic footer localized successfully without restarting EU4. Development menu wiring is complete: ADM/DIP/MIL buttons dispatch the shared reserve-aware batch flow, MIL full batch passed runtime (11 increases, 483 spent, 516 remaining vs 500 reserve), all three single-step category workers previously matched observed native baselines, and accepted devastation/estate approximations are disclosed. Ten offline checks passed at batch implementation. No claim of universal native parity: conditional EE reward branches, unusual estate configurations and institution completion boundaries have not each been runtime-tested. No further user action required for this wiring milestone.
