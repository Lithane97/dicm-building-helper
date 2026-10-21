# Native development integration investigation

User requirement: preserve normal development-click behavior, including institution
progress, native cost/legality enforcement, and Europa Expanded development hooks.
The user subsequently authorized reproducing the action in scripts, including side effects; raw development plus point deductions alone is insufficient.

## Verified installed interfaces

- The installed common/custom_gui/example.txt documents custom_button with potential,
  trigger, effect, tooltip and frame. It documents no native action/command binding.
- interface/provinceview.gui binds native handlers through tax_base_increase_button,
  prod_base_increase_button and mp_base_increase_button in the native province view.
- interface/macrobuildinterface_override.gui has native tax_button,
  production_button and manpower_button in development entries.
- These native controls are not scripted custom buttons. Copying a control name
  into our topbar window is not a verified way to acquire its native controller.
- Native common/scripted_functions/00_scripted_functions.txt defines can_improve_tax,
  can_improve_production and can_improve_manpower as scripted-function hook points.
  These are not evidence of callable development effects or general script triggers.
- EE common/scripted_functions/zzz_me_scripted_functions.txt adds development
  restrictions for ME_tim_deny_developing_arabian_provinces in arabia_region.
- EE common/on_actions/missions_expanded_on_actions.txt has substantial
  on_adm_development, on_dip_development and on_mil_development behavior, including
  mission counters, culture effects and conditional extra development. Merely
  increasing a base-development value cannot be assumed to perform the whole action.
- No supported callable native development-click effect was found in the installed
  scripts or documented custom GUI interface. This is an investigation result,
  not proof that no undocumented engine capability exists.

## Investigation state before reproduction

The Development menu, reserves (default 500), evaluator and previews remain intact.
Develop buttons remain disabled. No monarch points or development were changed
by this investigation. No raw-development spender has been introduced.

The read-only dicm_bh_development_spend_preflight.txt diagnostic is prepared but has
not been run in game. Its power export and variable affordability syntax remain
unverified and must not be treated as validated production logic.

## Architecture decision (resolved by user)

A mod-only automatic native-click spender is not currently implementable through a
verified exposed action. Full native behavior would require either discovering a
supported native command or a separate companion that operates the real game UI.
A companion is a new component, with window/scale handling, current point and native
cost verification before every click, reserve enforcement, stop-on-mismatch behavior,
and re-ranking after each observed successful click. Its feasibility has not been
verified; it is not part of the existing mod.

A mod-only alternative is to keep recommendations and let the user perform native
clicks. This preserves actual native behavior but does not provide bulk spending.
Do not present either route as completed native automation.


## First scripted reproduction â€” implemented, not yet validated in EU4

The user authorized a scripted reproduction after reviewing the Auto Dev example.
Three country events now perform at most ONE affordable supported increase:
`dicm_bh_development_spend.1` (ADM), `.2` (DIP), `.3` (MIL).
Menu Develop buttons and repeated spending remain disabled during this first test.

Selection evaluates current provinces and chooses the best benefit-per-power score
among supported, affordable sites. Reserve plus current estimated cost must fit the
current point pool; exact equality is allowed. Initial scope is owned, controlled,
completed core provinces, no siege/construction conflicts, non-primitive countries,
and no protected-estate development privileges. The installed EE Arabian development
restriction is respected. The category-balance gates from the evaluator still apply.
This is a conservative supported subset, not a universal native-legality query.

A country event selects the site and calls a hidden province event so hook ROOT is
the province and FROM is the actor. The worker rechecks ownership, site eligibility,
reserve and exact observed payment. Literal binary point deductions support costs
1..2047; no variable-valued native point effect is assumed. Payment failures refund
the observed deduction without adding development. A failed base increase also
refunds points before applying any reproduced side effects. Unexpected automatic
native hooks or development deltas suppress manual hook replay and report status 3.

For a verified base +1, the implementation applies:
- `add_next_institution_embracement_scaled = 5` after the base increase;
- devastation reduction `resulting development * 5 / 6`, up to 100, rounded to the nearest whole point, using literal
  integer pieces (user-authorized approximation);
- individual estate land deductions weighted by snapshotted whole-number influence
  in owner scope (user-authorized approximation);
- the installed vanilla and enabled-mod development hooks, once.

Institution timing, fractional devastation behavior, estate distribution, point
expenditure statistics and other hidden native changes are NOT established as
identical. This implementation is for A/B comparison, not a claim of full parity.
No native process was patched and no external helper was added.

### Hook maintenance

`tools/sync_development_hooks.py` resolves same-named files using the enabled mod
list and generates replay effects without overriding engine on_actions. Existing
vanilla/EE helper effects remain runtime calls rather than copied implementations.
`tools/development_hook_sources.json` records input hashes and protected privileges.
Two hook bodies per type were found in this installation (vanilla + EE).
Generator assumptions about load order/additive hooks must be checked through the
native comparison. Regenerate after relevant mod or game updates; run
`python tools/test_development_spend.py` from the mod directory. The tests check
source hashes and replay identity, script structure, every supported literal point
cost, single-step execution and disabled bulk/menu controls. They do not run EU4.

### First manual comparison

Use a disposable non-Ironman save and stay paused. Restart to load new events.
1. `event dicm_bh_development_spend.90`: read-only baseline. Logs the best supported
   affordable ADM site, predicted cost, pools, crownland, devastation, institutions
   and native/EE counters. If no site qualifies, no mutation occurs.
2. Save AFTER the baseline so the watched province and baseline values persist.
3. In that province, click native ADM development once, then run
   `event dicm_bh_development_spend.91`. Preserve game.log for comparison.
4. Reload the baseline save, run `event dicm_bh_development_spend.1`, then `.91`.
   Compare cost, reserve, base gain, counters and all recorded side effects.
5. Status 1 means the scripted path executed, not that parity has been validated;
   0 means no supported/affordable target or rejected scope; 2 payment mismatch;
   3 unexpected native hooks/base delta; 4 failed base increase with refund.

The current 1792 setup likely has every institution complete and no devastation.
A second test save with partial institution progress, nonzero devastation and
ordinary land-holding estates is required before those mechanics can be validated.
Random EE bonuses may legitimately differ between runs; verify trigger coverage and
distribution separately from deterministic base changes. DIP/MIL need their own tests.

Observer correction: institution IDs are not supported province export game values. They are now observed using numeric triggers as state classes (100 complete, -1 partial, 0 absent), not exact progress. Partial institution progress must be compared in the province UI separately. For the currently watched Lille, use `run dicm_bh_step_baseline.txt`, save, perform one native ADM click, then `run dicm_bh_step_after.txt`. Preserve native log output; reload that baseline save before running `run dicm_bh_step_adm_once.txt` followed by the same after script. Direct run observers load immediately, so this correction does not require restarting the running test.


### Native FROM scope correction

The first scripted comparison matched every recorded delta except the owner-local
num_of_times_developed_var. A separate native scope probe observed that same
variable on Lille itself changing from 0 to 1. This provides evidence that native
hook FROM is the province. The payment worker still uses province ROOT/country FROM
for ownership checks; it now dispatches a second province event (.21/.22/.23) only
for hook replay, giving province ROOT/province FROM. A province pending flag plus
the owner's active-step flag gates each replay; the pending flag clears before
replay to prevent duplicate dispatch. This correction is implemented, but must be
loaded by restarting and compared again. Both province-local and country-local
counters are now included in the direct observer. Earlier references describing
hook replay with country FROM are superseded by this observed scope correction.

Corrected Lille ADM comparison PASSED after restart: baseline exactly matches saved native baseline; all 20 observed deltas equal the native reference. Cost 30 ADM, tax +1, vanilla country counter +1, EE ADM counter +1, province-local FROM counter +1, owner-local FROM counter unchanged. Step status 1 and preview treasury drift 0. Evidence saved in tools/validation/scripted_lille_adm_corrected.json and .log. This validates the scope fix and this single-step case only: crownland is capped, devastation zero, institutions complete. Reserve refusal, DIP/MIL, active side effects and repeated spending remain unvalidated; menu/bulk controls stay disabled.

ADM reserve refusal validated at 969 points versus reserve 1000: all observed deltas zero. DIP/MIL tests can now use `run dicm_bh_step_dip_baseline.txt` / `run dicm_bh_step_mil_baseline.txt`, save after the selected baseline, native-click the matching category once and run the shared after observer, then reload and use the matching `_once.txt` script. Each baseline replaces the watched province/observations; complete one category comparison before starting another. The console selectors read cached native evaluations rather than recalculating production in run-file context.

Metz DIP single-step comparison PASSED: all 20 observed deltas match the saved native reference. Script status 1, 53 DIP paid, production +1, native and province counters +1, EE ADM counter unchanged, other power pools unchanged, preview treasury drift 0. Evidence stored in tools/validation/scripted_metz_dip.json and .log. This is the second category validated for basic point/development/hook behavior; active institution progress, crownland gains, devastation reduction, conditional EE bonuses, MIL and bulk execution remain unvalidated.

Rennais MIL comparison PASSED: all 20 observed deltas equal native reference; status 1, MIL -31, base manpower +1, native/province counters +1, all other observed deltas unchanged. Evidence preserved in tools/validation/scripted_rennais_mil.json and .log. Basic single-step point/development/hook parity now passed for ADM (Lille), DIP (Metz) and MIL (Rennais), plus ADM reserve refusal. Active crownland gain, nonzero devastation reduction, partial institution progress and conditional EE reward cases remain unvalidated before menu/bulk enablement.

Active devastation comparison fixture prepared: `run dicm_bh_step_devastation_setup.txt` adds 30 devastation once to the currently watched owned province, refreshes native evaluation and records a fresh direct baseline. Save after setup, native MIL click once, shared after observer; reload that save and use `run dicm_bh_step_mil_watched_once.txt` plus after observer. The test dispatcher pins the watched province because changing devastation can change country rankings; it retains core worker payment/reserve/eligibility checks. Production ranking code remains unchanged. Current watched province is Rennais; use only a disposable test save. No restart required for these immediate-load run scripts.

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
