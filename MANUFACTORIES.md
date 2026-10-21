# Remaining manufactory families

Implemented. All 11 remaining families pass native construction and budget
checks for 1792 France. Representative goods/manpower/sailor benefit estimates
match native tooltips. The 28 offline checks pass. Furnace national benefit
parity and conditional completion rewards have not been separately validated.

The seven goods manufactories, Furnace, Soldier's Households, Impressment
Offices and Ramparts feed the existing construction/budget/report pipeline.
State Houses were implemented earlier. Selections 25-29 and 31-32 retain their
IDs; new selections 33-36 add Naval Equipment (wharf), Plantations, Mills and
Ramparts. Their unlocks and inherited base cost 500 are checked against the
installed game/Europa Expanded definitions in the tests.

Goods manufactories occupy the bottom menu row. Furnace moves beside Workshop
and Counting House. Ramparts sits between land forts and coastal defences.
Other layout and coastal priorities remain as before.

All are new construction only. Native `can_build` selects valid trade goods and
enforces DLC/other legality. A separate `has_manufactory_trigger` gate prevents
replacement of existing goods/resource manufactories, State Houses, Ramparts or
Furnaces. Existing construction also blocks candidates. No helper upgrades or
automatic replacement are enabled for these families.

## Ranking

- Goods manufactories: additional monthly production income, using the existing
  balanced engine income sample divided by the exported flat goods and 12.
  The inherited bonus is one flat goods unit. Existing price, efficiency,
  goods bonuses and applied autonomy are retained in the income measurement.
  Strictly requires a valid engine sample; there is no reconstructed-price
  fallback for the displayed manufactory gain.
- Furnace: sum of supported provinces' monthly production contributions from
  +0.05 national goods modifier. Divide each sampled income by its current
  goods multiplier before multiplying by .05. Every legal Furnace site has
  the same estimated national benefit in one pass. Exact ties retain existing
  iteration behavior. National income excludes unsupported provinces; this is
  a partial estimate where trade companies or other unsampled cases exist.
- Soldier's Households: 750 flat manpower, or 1500 for grain, fish, livestock,
  wine, multiplied by current local + national manpower modifiers and autonomy.
- Impressment Offices: 250 flat sailors, or 500 for salt, fish, naval supplies,
  tropical wood, multiplied by current local + national sailor modifiers and
  autonomy. Recruitment speed and ship-cost benefits are not ranked.
- Ramparts: completed land forts only. Score is 2/4/6/8 for the four fort tiers,
  plus 1 for a land border. This is a defensive heuristic, not an income score.

Resource modifier exports already include the land/coastal and core base
contributions; do not add a second base multiplier of 1. Resource minima reuse
their existing units. Goods/Furnace minima use monthly ducats. Ramparts has its
own saved minimum, default 0, increment 1.

Trade income, commodity trading bonuses, institutions, conditional EE completion
development/rewards and downstream gains are not included in the benefit
estimates. Gold and trade-company production are unsupported by the engine
sampler. Preview does not add/remove buildings or development. The sampler
temporarily pays production income and reverses it synchronously, as in the
existing production/development evaluators. Native construction applies normal
EE `on_built` effects on completion; the helper does not manually replay them.

## Runtime diagnostic

Restart EU4 to load the scripts/menu, then run on the paused test baseline:

`run dicm_bh_manufactory_check.txt`

Logs the best three candidates, benefit and cost for each unlocked family,
eligible counts, locked technologies and final treasury drift. Settings and
the previous report are restored. No construction, development or net spending.
The initial diagnostic does not refresh cached UI estimates or change selection.

Next validation: inspect script errors and zero drift, compare native predicted
benefits/costs in representative provinces, then test actual queues and budgets.
Some families may have no eligible sites on a given country/save. Furnace
requires a suitable coal province and Rule Britannia.

### First runtime diagnostic, 1792 France

All 11 families produced eligible candidates; no helper-specific script errors
were found and treasury drift was zero. All logged candidate costs were 400.
Top-three order was descending by benefit for every family. This establishes
execution and balance, not native parity of benefit estimates.

User confirmed native tooltip matches: Troyes Weapons 0.480 monthly production,
Calais Soldier's Households 1875 manpower, Calais Impressment Offices 625 sailors,
and 400-ducat costs for all three. Furnace predicts 1.327 monthly national
supported production gain in Metz; this needs a separate national comparison.

Eligible pools: Weapons 5, Textile 18, Farm Estate 29, Trade Station 4, Naval
Equipment 11, Plantations 6, Mills 5, Impressment Offices 28, Soldier's Households
81, Furnace 1, Ramparts 22. Evidence:
`tools/validation/manufactory_first_run.log` and `.json`.

### Construction batch prepared

On the same paused 1792 France baseline, set budget 1% and minimum 0 for each
selected family, then Build once in this order: Weapons, Textile, Farm Estate,
Trade Station, Naval Equipment, Plantations, Mills, Impressment Offices, Soldier's
Households, Furnace, Ramparts. Do not unpause or reload between families. Save
`manufactory_builds.eu4`. Expected at this treasury/cost: two queues per action
except Furnace (one legal coal site), totaling 21 queues and 8400 ducats.
This also exercises conflict exclusion when resource/Ramparts candidates overlap
previously queued goods manufactories. Actual counts and payments remain pending.

### Construction batch results, excluding Ramparts

Passed: all ten attempted families queued successfully; nine created two
buildings and Furnace created one. Each cost 400, totaling 19 distinct province
queues and 7600 ducats. Treasury is 92470.070, matching 100070.070 minus 7600.
All ten live reports show zero failures and spending within the 1% budget.
The user built Soldier's Households before Impressment Offices; both still
created two valid queues. No province received overlapping construction.
Evidence: `tools/validation/manufactory_builds.json` and `.log`; source save
`manufactory_builds.eu4`. Benefit parity for Furnace remains unverified.

Ramparts was not visible because the runtime remapped shared `GFX_ramparts` to
a missing `gfx/interface/buildings/iv_weapons_1.tga` texture. Added helper-owned
`GFX_dicm_bh_ramparts`, pointing directly at the existing native
`gfx/interface/buildings/latin_march.tga`, and updated the button. The tests
verify the sprite registration and asset path. This bypasses the culture remap
for this helper button; it does not change the shared vanilla sprite. Evidence:
`tools/validation/ramparts_missing_icon.log`. Visual confirmation is pending.

Next: restart EU4, load `manufactory_builds.eu4`, select Ramparts between the
land-fort icons and Coastal Defence, minimum 0/budget 1%, Build once, save as
`manufactory_ramparts.eu4`. Expected: two queues costing 800 combined.

### Ramparts construction and icon test

Passed after the icon fix: two Ramparts queues, in Roussillon (197) and
Verdun (4766), each 400 ducats. Eligible 17, budget 924.700, 15 budget skips,
zero failures. Treasury fell from 92470.070 to 91670.070, exactly 800.
All 19 earlier queues were preserved; total 21 queues and 8400 spent across
all 11 families. Saved building index 33 identifies the new Ramparts queues.
The helper-owned sprite produced no matching texture errors in this session.

The user overwrote `manufactory_builds.eu4`; the baseline is now its
`manufactory_builds_Backup.eu4`. Evidence is in
`tools/validation/manufactory_ramparts.json` and `.log`. A later unsaved action
in the same session queued the remaining 15 Ramparts for 6000 with zero
failures, as recorded in the log; this extra action is not included in the
21-queue saved-state verification.

All manufactory construction paths are now tested. Furnace's national income
estimate, other commodity-by-commodity benefit parity, and conditional EE
completion outcomes remain outside the verified scope.

### Province-interface Ramparts compatibility fix

The earlier icon fix covered the helper-owned sprite only. User screenshot
showed the native province construction slot still had a missing icon and the
name "Centre of Weapons Production". Confirmed source: active mod The Idea
Variation Lite Version (1680127708), `interface/idea_variation.gfx` overrides
`GFX_ramparts` with a missing `gfx/interface/buildings/iv_weapons_1.tga` and
`localisation/replace/zIdea_Variation_replace_l_english.yml` renames
`building_ramparts`. This is a direct sprite override, rather than the previously
inferred culture remap. EE's effective building remains defensive, including
+1 hostile attrition, +15% defensiveness and +1 defender dice roll bonus.

Supplied the missing texture path inside Building Helper using an exact copy
of native `latin_march.tga`. The shared province sprite now has a valid asset
without requiring another GFX definition to win load order. Added late English
replacement localisation restoring `building_ramparts` to "Ramparts". Original
workshop files were not edited. Existing helper icon continues to use its own
reference. EE specifies `onmap = no`; this fix does not add a 3D map model.
Asset equality was checked with SHA-256 and localisation has a UTF-8 BOM/CRLF.
Visual confirmation after restart remains pending; no save or construction
needs to be redone.
