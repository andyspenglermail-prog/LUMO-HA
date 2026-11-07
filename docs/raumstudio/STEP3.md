# Auftrag03 · Design & Display (0.14.1)

## Bounded 0.14.1 room-photo correction

Single visible view: no redundant output navigation; its heading remains. Two or more visible views retain switching. When saved RoomPlan views are all hidden, Step3 explains how to reactivate them in Raum; no data is made visible or deduplicated automatically.

`design.roomImages` is an **optional** map of stable saved `view.id` → existing owner-scoped `imageId`, each exactly 32 lowercase hex characters, maximum 256 bindings. Empty map and legacy design without the member are valid; null values, empty/malformed keys, unknown/foreign views and missing/foreign images are rejected. No new database table, RoomPlan field, native field or global settings field exists. The existing design POST retains exact `{revision,design}`, owner/CAS/CSRF checks and transaction; invalid input leaves document/revision unchanged. Maintenance validates the same reference closure before reopen/backup/restore.

Renaming, ordering and hiding views retain bindings by ID. Explicitly confirmed view deletion prunes only the deleted IDs from this separate map atomically with the plan save. A new or duplicated room view has a new ID and no implicit photo; dashboard duplication copies the map into an independent document while immutable owner image bytes remain shared. Removing a photo assignment never deletes library bytes. No startup migration rewrites legacy documents.

Step3 selects/uploads/removes a photo using the existing `GET/POST api/images` and `GET api/images/<id>` routes and decoder. PNG/JPEG/WebP limits, metadata removal, owner isolation and library quotas are unchanged. Upload confirms the image library by GET, stages only the captured view binding, and requires **Design speichern** for persistence. Busy locking, identity/generation guards, dirty confirmation and uncertain-outcome retry blocking apply. Step1 background bytes are never changed by these controls.

The output renders a bounded, responsive image with an opaque theme-token caption; text never depends on the photograph's contrast. Loading/error are explicit; an unsuccessful image request never exposes a successful photo state. Without a binding, the old heading presentation remains. All three profiles and the neutral editor remain distinct. `design-native` explicitly lists room photos as `preview-only`: no native layout/photo generator, no changed original export or HA write.

Selectors: `#design-view`, `#design-room-image`, `#design-room-file`, `#design-room-remove`, `#design-room-target`, `#design-room-hero[data-photo-state]` (`none`, `loading`, `ready`, `error`), `#design-room-photo img`, `#design-room-photo-state`, existing `#design-save` / `#design-dirty`. Global background controls remain in Step1 only.

The two pre-existing version assertions now expect 0.14.1; all existing test identities and other expectations remain. Additional test files: `test_room_photos.py` and `test_room_photos_browser.py`. RED/GREEN source archives and supplementary direct-GREEN checks are separate evidence, not inflated test counts. Final suite manifests bind the actual code. RF08 independent review, images, private reads/snapshot replay and publication belong to the parent; physical touch and Andy's acceptance remain separate.

## Original 0.14.0 integration (historical description)

## Boundaries and minimal integration

New files: `design.py`, `design_native.py`, `design-catalog.json`, `design.js`, `design.css`. The original `store.py`, `room.js`, `room_store.py`, `native.py`, imported configuration grammar and legacy exporters remain unchanged. There is no separate app, service, HA writer, Step4 authoring, action dispatch, analytics or AI.

The existing `app.js` step coordinator now opens Step3, stops its polling on leave, invokes its dirty guard and restores its busy lock after writes. Step2's existing `room-next` already calls that coordinator; no second room model was introduced. `index.html` adds Step3 and updates the Step4 handoff wording only. Step3-specific shell CSS is gated by visible Step3; selected themes never target body/editor. `maintenance.py` validates the new optional overlay without rewriting pre-existing rows. Docker's existing COPY receives the new files. Two existing navigation tests replace obsolete handoff assertions with actual Step3 assertions; two version assertions become 0.14.0. All prior method identities remain.

## Model and transport

Optional document member `design`: schemaVersion=1; category; active profile (`noir`, `ivory`, `smart`); individual overrides; selected targets; active target; display records; functional options. Closed fields/enums, finite bounded numbers (booleans are not numbers), CSS width320–3840/height240–2160, DPR0.5–4, optional physical/hardware dimensions. Text/card contrast is >=4.5. Colors are six-digit hex only; no URLs, custom CSS or code fields.

GET `api/dashboards/<id>/design` returns dashboardId, revision, design, saved room plan and bounded inert native sources. POST same path accepts exactly `{revision,design}` and updates only the overlay/revision/timestamp inside `BEGIN IMMEDIATE` and the existing owner/CAS contract. No write occurs on GET/startup. UI captures identity/revision, compares POST output with exact confirmation GET, blocks uncertain retries, refreshes the native report, then updates list. Old documents remain byte-identical on reopen. Duplicates and cold backups naturally include the overlay. A downgrade needs a full pre-update backup (0.13.0 does not understand the new optional member).

GET `api/dashboards/<id>/design-native` returns a **saved-only sidecar**, not dashboard configuration. `themes` contains an HA theme namespace (JSON/YAML-compatible), plus capabilities, selected tokens, exact document revision, source pin and explicit install=false/export-unmodified flags. Use `themeName` to identify the namespace; copying the entire wrapper as dashboard config is wrong. No automatic installation, theme assignment, resource fetch or publication exists.

## Truthful rendering

Saved roomPlan refs resolve by stable registry identity against actual runtime inventory. Missing/disabled/unavailable/unknown/null/stale are explicit. Native safe known card refs are inert data projection, not custom element execution; unknown cards remain protected labelled elements. Projection is bounded (2000 cards per native view, nesting8). Native layout/order/source data are never rewritten, but this safe function preview does not claim exact imported layout rendering.

View override > native view background > native dashboard background > Step1 global background; theme only supplies a fallback. Hex native backgrounds are safe. External/complex CSS and imported theme assignments remain protected and labelled; no external URLs execute. Step1 remains the sole global background editor; 0.14.1 adds only the independent room-photo surface described above. Local image position/size/opacity and fixed-to-preview background are retained.

The preview root has actual requested CSS dimensions, with container-query reflow into5/3/2/1 columns at >1100/>700/>450/<=450px. Optional fitting is a separate, disclosed transform. Unscaled editor view selection remains usable when fitted controls shrink. 1:1 inspection provides bounded scrolling and tests genuine44px-or-larger target controls. Target DPR/client/kiosk/diagonal are explicit intent, not claimed measurements or hardware emulation. System font stacks require no downloads and may resolve differently by OS.

## Native capability matrix

Original official HA frontend source pin `a67b691a451e0b3fc469679b07158f963a61842c`, offline asset build `DEMO-20261028.4`. `test_design_native_runtime` mounts the **original registered ha-card** and independently inspects its computed background/material/text/border/radius/shadow/header font/size for all three saved sidecars; this is not a div with arbitrary variables. Existing `test_native_runtime` also mounts original hui-root/view-background for legacy inheritance, mode, position, baked image opacity and attachment. Neither test certifies Andy's installed HA version.

| Capability | Contract |
|---|---|
| Card background, gradient material, border/radius/shadow/text | Computed original ha-card proof at pinned build; internal variables may change |
| Card header system family/size | Original card-header computed styles; OS font fallback not fixed |
| Global background | Separate lovelace-background theme fallback; existing view/dashboard overrides win; local PNG embedded |
| Primary/accent/secondary palette | Theme variables exported; individual HA control consumption not exhaustively verified |
| Body typography/weight, navigation shapes, icon/status surfaces, spacing/density | LUMO preview only; no blanket native parity claim |
| Responsive target layout, touch geometry, device profiles | LUMO preview verified; no Step4 native layout generator |
| Diagram palette/transition tokens | Future consumption only, no analytics generated |
| Custom cards/external themes/installed newer HA | Not executed / unverified |

## Reproduction

Use a fresh evidence directory for every run, never historical output paths:

```sh
PYTHONDONTWRITEBYTECODE=1 \
PYTHONPATH=/workspace/jarvis-voice-prototype/.test-deps \
PLAYWRIGHT_BROWSERS_PATH=/opt/playwright \
RAUMSTUDIO_EVIDENCE=/path/to/fresh/evidence/browser \
python3 -B tests/raumstudio/run.py
```

The runner records exact unique qualified test IDs, before/after source manifests, failures/errors/skips and engine fixtures. Native assets default to `/workspace/lumo-core-usability-evidence/native-feasibility`; override with `HA_NATIVE_CACHE` for an equivalent hash-pinned cache. Migration tests use an isolated `git archive` of the actual prior Store, always `-B`. No real HA or private credentials are needed. Synthetic peer fixtures are tests only, never production fallback.

Release gates outside this implementation: parent live runtime reads against actual selected references, independent reviews, images for both declared architectures, nonforce existing-repository publication and anonymous source readback. Installation, physical devices and Andy's personal acceptance remain separate.
