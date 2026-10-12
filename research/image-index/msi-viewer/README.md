# Local multispectral image comparison

This local packet makes the [selected source intake](../MULTISPECTRAL_INTAKE.md)
easier to inspect at useful zoom, with explicit stored-array and EXIF display
coordinates. It copies exactly eight original image files: six provider JPEGs
and two Yale references. All sources concern **two manuscript surfaces**, 1r and
116v; duplicate/processed views provide no independent manuscript samples.

This contribution is initially a **draft dependent on PR #163**. The
[settings](inputs.json) pin that parent's exact commit
`ee961733dffbeb98893407114634ed82816a81bc`, seven input hashes and corresponding
Git blobs. The pending typed-offset correction belongs to the parent's assigned
reviewer. Refresh the dependency explicitly after parent acceptance, proving
that source/image records remain unchanged; do not treat these pins as an
accepted-source claim or silently update them.

## Build and open locally

Python 3.10 or later and Git; standard library only for packet construction.
Use the source cache described in the [intake note](../MULTISPECTRAL_INTAKE.md).
It must contain the eight exact image files, Read Me and manifest. Then:

```sh
python3 scripts/build_msi_viewer.py --cache /tmp/voynich-msi-cache --output /tmp/voynich-msi-viewer
python3 scripts/build_msi_viewer.py --cache /tmp/voynich-msi-cache --check /tmp/voynich-msi-viewer
python3 -m http.server 8765 --bind 127.0.0.1 --directory /tmp/voynich-msi-viewer
```

Open `http://127.0.0.1:8765/index.html` in a browser on that computer. The local
server is needed for browser fetch/hash checks; directly opening `index.html`
as a file is not supported. Stop the server when finished. No external hosting,
deployment, account, upload or network image retrieval is added. Provider links
open only when clicked. The comparison itself works offline after construction.

The output must be a fresh empty directory outside the checkout, its ancestors
and the source cache. The builder verifies pinned inputs and source bytes before
construction, then repeats its output guard after all serialization and before
writing. It uses exclusive file creation. `--check` reconstructs all eleven
packet files, rejects missing/extra/changed/linked files and writes nothing.
The packet manifest binds templates, script, settings, generator, inputs and
every original asset. Generated image packets stay outside Git.

## Views and coordinate conventions

Choose any pinned image independently in either panel. File names, source
folders, dimensions, EXIF values, source links and hashes remain visible. The
two PSC copies have distinct menu labels even though their native filenames
coincide. Each panel supports fitted view, zoom up to 12x, pointer dragging,
numeric center coordinates and keyboard panning. Arrow keys move ten pixels;
Shift plus arrow moves 100. Zoom is relative to fitted display size.

The initial pair illustrates the known orientation seam. In **EXIF display**,
the processed-folder PSC (orientation 3) and RGB-folder PSC (orientation 1) face
opposite ways. In **Stored array**, both show the same stored orientation.
Every pointer position reports zero-based displayed and stored pixel indices;
positions outside the image are identified rather than clamped into a glyph.

The browser checks the original asset's SHA-256 first. It removes the EXIF
segment only from an **in-memory decoding copy**, verifies that copy against
the parent's non-EXIF digest and explicitly renders the requested orientation.
JPEG coding/scan data and ICC profiles are retained; all original source files
are unchanged. The browser may manage colors and resample the screen display.
This interface does not compare calibrated pixel intensities.

For orientation 3, displayed `(x,y)` maps to stored
`(width-1-x,height-1-y)`; orientation 1 or absent EXIF leaves indices unchanged.
The conversion is exact for the documented pixel convention, not a physical
glyph mask or a mapping between captures. Changing orientation resets the
viewport so an old center is not silently assigned another convention. Separate
captures have independent viewports; no automatic registration is offered.

A missing or changed image stays blank with an explicit error. Previous image
content and stale coordinate controls are cleared; image-dependent controls
are disabled until verification succeeds. Recorded source details/links remain
available. No observations, masks, annotations or notes are saved or uploaded.

## Verification and limits

```sh
python3 -m unittest tests.test_msi_viewer tests.test_msi_intake -v
node tests/test_msi_viewer_geometry.cjs /tmp/voynich-msi-cache
```

All **14 focused Python tests** pass on the pinned parent: six packet tests and
eight intake tests. They cover exact parent blobs/pins, preserved original
bytes, exclusion of unrelated cache files, literal/escaped model text, changed
inputs, fresh output/cache protection, an alias created during serialization,
exclusive packet writing and complete read-only packet replay.

The separate JavaScript test uses independently arranged labeled grids to check
432 orientation mappings and round trips, 972 fitted/zoomed viewport projections,
invalid/outside coordinates and malformed containers. It verifies the EXIF
removal digest against the independent Python parent's recorded value on all
eight real JPEGs while proving the original buffers are unchanged.

Actual browser inspection exercised all eight choices with both file and
in-memory digest checks, EXIF/stored modes, keyboard zoom/pan and pointer index
conversion. The PSC stored-mode displays appear alike; no exact browser pixel
array equality is claimed. A disposable wrong-hash page demonstrated that a
failed selection clears previous content, retains source links and leaves the
other valid panel usable. At 390- and 320-pixel widths the panels stack without
horizontal page overflow. Temporary viewport overrides were reset. Complete
original-cache packet replay passes.

The page requires JavaScript; its scriptless notice points to original packet
files and hashes. Source credits and interpretation limits stay visible. The
intake's nonblind observations and prior exposure are not adjudicated by this
interface. Opening it creates no unseen or independent evidence, source
correction, accepted glyph reading, legacy 117v alias or translation. It prepares
traceable views for later qualified review under the decipherment protocol.
