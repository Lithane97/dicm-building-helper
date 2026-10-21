# DICM Building Helper

A building and development helper for **Europa Universalis IV 1.37.5**, designed
for **Europa Expanded**. It adds Building Helper and Development Helper tabs to
the macro builder, alongside EE's existing tab.

## Features

- Build or upgrade supported buildings across qualifying provinces, with a
  configurable treasury percentage and minimum benefit.
- Preview project counts and costs before committing. Native construction
  handles payment, queues and completion effects; reports show actual spending,
  budget skips and failures.
- Rank tax, production, trade, manpower, sailors, army/navy force limits,
  governing-cost buildings and manufactories by their estimated additional
  benefit. Universities use an aggregate of ADM, DIP and MIL development benefits.
- Place land forts using border, neighbour and spacing rules. Coastal defences
  use strategic groups and development tie-breakers. Ramparts target existing
  land forts.
- Develop provinces with separate ADM/DIP/MIL reserves, defaulting to 500 points
  each. The helper reranks after every successful increase and reproduces the
  tested development effects in script, including institution progress and EE
  development hooks.

The building menu includes Church/Cathedral, Workshop/Counting House,
Marketplace/Trade Depot/Stock Exchange, Barracks/Training Fields, Dock/Drydock,
Regimental Camp/Conscription Center, Shipyard/Grand Shipyard, Courthouse/Town Hall,
State House, University, four land-fort tiers, Coastal Defence/Naval Battery,
all seven goods manufactories, Soldier's Households, Impressment Offices,
Furnace and Ramparts. Manufactories use new construction only; the helper does
not replace an existing manufactory with a different type.

## Requirements and installation

- Europa Universalis IV 1.37.5.
- [Europa Expanded](https://steamcommunity.com/sharedfiles/filedetails/?id=2164202838),
  enabled before this mod. This is an EE integration, not a standalone vanilla
  interface replacement. DLC-specific buildings still use the game's eligibility
  checks.

1. Download the repository and put its contents in a folder named
   `DICM Building Helper` inside your EU4 user directory's `mod` folder. On
   Windows, that directory is usually `Documents/Paradox Interactive/Europa
   Universalis IV/mod` (or its OneDrive equivalent).
2. Copy `packaging/DICM Building Helper.mod` into the **parent `mod` folder**,
   alongside the `DICM Building Helper` directory.
3. Enable Europa Expanded and DICM Building Helper in the launcher, keeping the
   helper after EE, then restart EU4.

The resulting layout should be:

```text
mod/
  DICM Building Helper.mod
  DICM Building Helper/
    descriptor.mod
    common/
    events/
    interface/
    localisation/
    ...
```

If cloning directly from the `mod` folder:

```sh
git clone https://github.com/Lithane97/dicm-building-helper.git "DICM Building Helper"
```

The repository does not publish to Steam Workshop or install Europa Expanded
for you. Mods replacing the same macro-builder/topbar interface may need a
compatibility merge. The helper includes an icon/name compatibility fix for
Ramparts when Idea Variation Lite is enabled.

## Use

Open the macro builder and select the Building Helper tab. Choose a building,
set its minimum benefit and the percentage of current treasury to spend, and
inspect the Build/Upgrade preview. Click the appropriate action to queue native
construction. Each action takes its own budget from the current treasury.

The minimum uses the selected family's unit: monthly ducats, manpower, sailors,
force-limit capacity, governing capacity saved or a strategic score. Tooltips
explain the unit and placement rules. A minimum of zero allows all supported
positive-benefit candidates; building eligibility and placement rules still apply.

The Development Helper tab has separate point reserves and Develop buttons for
ADM, DIP and MIL. The footer reports increases, points spent and the stop reason.

## Validation and limits

All 28 offline checks pass on the development installation. Native game tests
verified construction, costs, budgets and queues for each supported building
family. Representative production, manpower and sailor manufactory estimates
matched native tooltips. Development tests covered all three individual point
types and a full reserve-aware MIL batch, including an active institution case.

These results are scoped to the tested saves and installed mod versions:

- Production estimates exclude gold and trade-company production. Workshop
  estimates have a documented approximate fallback; goods-manufactory estimates
  require a valid native income sample.
- Goods estimates cover direct production income, not the owner's eventual
  share of downstream trade income. Conditional EE building completion rewards
  are applied by native construction but excluded from estimated benefits.
- Furnace estimates sum supported national production benefits; the national
  income estimate has not been independently compared with native results.
- Coastal raid priority uses recent raids as evidence, not predicted raider
  range or diplomacy. Coastal priorities may be refined later.
- Scripted development rounds devastation reduction and uses whole-number
  estate influence weights. It is not a callable native development click;
  unusual estate setups, conditional EE rewards and all institution boundaries
  have not each been tested.
- Development-hook replays depend on the installed game and EE scripts. Game
  or mod updates require checking/regenerating those integrations.

## Development and diagnostics

Python 3 is sufficient for the offline tests; EU4 and the referenced EE files
must also be installed. Tests currently use the development machine's Steam
paths on `D:`; adapt those paths and the source manifest for another installation.
They are integration checks, not a self-contained CI suite.

Run from this repository's root:

```sh
python -m unittest discover -s tools -p "test_*buildings.py"
python -m unittest discover -s tools -p "test_development_spend.py"
```

The `dicm_bh_*.txt` files at the root are developer console scripts. Some are
diagnostics; others deliberately change buildings, development or resources in
a test save. They are not required for normal play. Their comments describe
their purpose.

Design notes and test history:

- [Manufactories](MANUFACTORIES.md)
- [Coastal defences](COASTAL_BUILDINGS.md)
- [Force-limit buildings](FORCE_LIMIT_BUILDINGS.md)
- [Manpower and sailor buildings](RESOURCE_BUILDINGS.md)
- [Development evaluation](DEVELOPMENT_EVALUATION.md)
- [Development integration](NATIVE_DEVELOPMENT_INTEGRATION.md)

These notes include historical implementation stages. Local save files and
raw validation captures referenced by the notes are omitted from the public
repository. Current status and limitations are summarized above.

## Credits

Europa Universalis IV and its original scripts, interface definitions and art
are by Paradox Development Studio / Paradox Interactive. Europa Expanded
integration and adapted hook content come from the Europa Expanded project.
See [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md) for the reused components.
