# Open the accepted f76r comparison with local image copies

The accepted [live-image viewer](../viewer/README.md) loads its windows from
Yale. This companion [packet builder](../../../scripts/build_f76r_offline_packet.py)
uses the same accepted page with five verified cache files. The three displayed
windows load locally; the recorded whole-page overview and service JSON are
available as local links. Native text, zoom, neighbor context, original notes
and provisional row associations are preserved.

Collect the four JPEGs and service JSON named in the
[original accepted review](../f76r-anchor-review.json), using its exact URLs and
`local_filename` values: `f76r-overview.jpg`, `f76r-first.jpg`,
`f76r-median.jpg`, `f76r-last.jpg` and `f76r-info.json`. Keep this image directory
outside Git checkouts. The builder downloads nothing. An earlier verified cache
can be reused; unrelated cache files and retrieval receipts are ignored and
never copied into the packet.

From the repository root, with Python 3.10+, Git and the cited history, replace
the capitalized paths with a cache and a separate fresh local packet directory:

```sh
python3 scripts/build_f76r_offline_packet.py \
  --image-directory LOCAL_IMAGE_DIRECTORY --output FRESH_LOCAL_PACKET_DIRECTORY
python3 scripts/build_f76r_offline_packet.py \
  --image-directory LOCAL_IMAGE_DIRECTORY --check FRESH_LOCAL_PACKET_DIRECTORY
```

Open the packet's `index.html` directly in a browser. All text and three image
windows work offline; opening an official image or source-file link requires
internet. Alternatively, serve only that packet on loopback:

```sh
python3 -m http.server 8765 --bind 127.0.0.1 \
  --directory FRESH_LOCAL_PACKET_DIRECTORY
```

Open `http://127.0.0.1:8765/index.html` while the server runs. The viewer saves no
notes and makes no requests to external image services. With scripts disabled,
all three anchors and their native context remain available.

## Identity and checks

The [declaration](inputs.json) binds five actual Git blobs to accepted viewer
merge `dc01f9b27847d5ffd5aefb1e2a74f69799b11c3c`. The builder reads the archived
HTML and evidence, verifies their original source bindings, all fourteen native
fields, source-line links and three image associations, then changes only the
displayed image `src` values and local-packet explanation/provenance. The current
live viewer, its producer and its template are unchanged. No unmerged downloader
code is imported.

Every copied asset must match its recorded SHA-256 and its byte count when
present. Service identity and native dimensions are checked from its JSON.
The packet contains only `index.html`, `packet.json` and five files in `assets`.
Its manifest records archived inputs, builder identity and every payload's
byte count/hash. `--check` compares all seven files and the complete directory
inventory; missing, changed, extra or aliased members fail. Cache and output
must be separate and outside Git. Output creation is exclusive: existing paths
and late collisions are preserved. A write failure can leave an incomplete new
packet; use a different fresh directory rather than overwrite it.

```sh
python3 -m unittest tests.test_f76r_offline_packet -v
```

Eight focused tests preserve the fourteen literal fields, notes and all original
hrefs; verify exact asset copies and manifest replay; reject archived/conversion
drift, missing/truncated/wrong bytes, wrong service identity, cache/packet links,
Git locations, unrelated/extra members and existing/late output collisions.
Copy/failure fixtures are synthetic; the actual five-file earlier cache also
passed complete build/check without downloads or new scientific observations.
Browser checks cover all three local windows at their recorded dimensions,
native keyboard selection and zoom, and desktop/390-pixel layouts. Sixfold zoom
scrolls inside the image window while page width remains 390 pixels. A script-
blocked QA copy retains all three sections and fourteen fields; a missing-image
copy reports the local failure while preserving native text and the official link.

Build-time byte verification establishes copied-file identity. The browser
reports loaded dimensions and does not recheck byte hashes. Both checks remain
separate from glyph accuracy and physical-row alignment. Original PR #60 notes
and PR #99's later nonblind check keep their attribution and limits. No source
correction, glyph adjudication, new image selection, language or translation is
added. These previously exposed images remain local; no pixel files, generated
packets, retrieval receipts or hosting configuration belong in the PR.
