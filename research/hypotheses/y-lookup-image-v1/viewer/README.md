# Local reviewer for the two accepted lookup image pairs

This viewer displays the accepted `f17r.2 → f18r.6` and `f19v.4 → f35v.15`
packet from [PR #115](https://github.com/tobrien6/voynich-manuscript-research/pull/115),
with preserved native source contexts, whole-page/row/group windows, original
slots and provisional status. It adds no selection, image measurement, reading,
correction, saved annotation or deployment. Original nonblind AI observations
are separately collapsible; hiding them does not create a blind experiment.

The interface follows the accepted [f76r viewer](../../../pilot/viewer/README.md),
extended to a target/development pair and locally verified assets. Generation
requires the 17 recorded image/service files listed in
[image-review.json](../image-review.json), named exactly as its resources.
Retrieve those official public URLs to a local image directory, retaining the
recorded bytes; the builder performs no download or external request. Source
images remain local and are never included in the contribution files.

The builder checks accepted Git blobs and all image/service fingerprints,
dimensions, URLs and bounds before writing a fresh output folder outside the
checkout. It copies only the 17 declared files, renders `index.html`, and writes
a packet identity manifest. It refuses existing nonempty outputs and protected
or linked paths. The `--check` mode verifies every generated file and refuses
unexpected additions. A viewer packet contains source images and must stay local;
do not commit or upload the generated folder.

Run from the repository root:

```sh
python3 scripts/build_y_lookup_viewer.py --image-directory /path/to/recorded/files --output /tmp/lookup-pair-review
python3 scripts/build_y_lookup_viewer.py --image-directory /path/to/recorded/files --check /tmp/lookup-pair-review
```

Serve the packet over loopback HTTP, the tested browser workflow:

```sh
python3 -m http.server 8765 --bind 127.0.0.1 --directory /tmp/lookup-pair-review
```

Open `http://127.0.0.1:8765/`, then stop that temporary server afterward. Direct
`file:` opening was not tested because the in-app browser blocks that protocol.
The HTML uses only local assets, system fonts and inline controls. External Yale,
publisher and GitHub links open only when selected. Native disclosures and all
pair/window sections remain accessible without JavaScript; image errors retain
source text and official links. Zoom stays inside each image viewport. On a
local HTTP server with Web Crypto, each displayed image is additionally checked
against its recorded SHA-256. Unsupported contexts retain the builder's
byte-check provenance rather than claiming browser verification.

The packet aids human review of the same already exposed evidence. Exact local
image bytes do not certify row placement, glyph identities or token boundaries.
Both editions are related; their agreement is not independent ground truth.
Source-file links target the exact accepted commit. All native case, dots,
commas and tags are retained literally, including the unresolved ZL/IT ch/sh
disagreement. Original observations remain attributed to PR #115 and separate
from the viewer's functionality. Independent human adjudication remains pending.

This is a local research aid. The 99 Tokens Markdown/folio renderer does not
execute this HTML/JavaScript, and GitHub HTML links show source. No live site,
hosted URL or publication of pixel assets is added.

## Validation

All 24 focused tests pass, including seven builder/packet tests. The accepted
four Git blobs, all 24 literal native fields and exact source-line links,
escaping, fixed pair roles/slots, image identities, omitted/mutated packet
files, extra input-file exclusion, pin drift and output/link protections are
checked. All 19 generated files (HTML, manifest, 17 recorded assets) replay
byte for byte. The accepted scientific plan, selection and image-review records
remain unchanged.

Browser QA covers both pairs, keyboard selection and sixfold keyboard zoom,
1280/390/320 layouts with horizontal scrolling confined to image windows,
all 13 runtime image hashes, a scriptless copy with both pairs and all 24 native
fields, missing-image fallback, and a deliberately incorrect checksum declaration.
The temporary copies are removed and the viewport reset after QA. File-protocol
testing is explicitly unavailable under the in-app browser's URL policy; the
documented loopback workflow is tested. These checks assess the interface and
byte identity, not glyph accuracy or independent human adjudication.
