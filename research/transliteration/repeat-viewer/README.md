# Local immediate-repeat source/image comparison

Build a private local packet for the three accepted [immediate-repeat cases](../IMMEDIATE_REPEAT_IMAGES.md),
then open its `index.html` in a browser. Both editions, neighboring native
records, all four uncertainty policies and recorded image windows remain
available. Choose a case/policy and zoom a context, overview or detail window.
Image pixels and generated outputs stay outside the research checkout.

This follows the accepted [f76r viewer](../../pilot/viewer/README.md) and
[lookup-pair packet](../../hypotheses/y-lookup-image-v1/viewer/README.md)
patterns, without modifying those viewers or adding hosting/99 Tokens execution.

## Build and open

Python 3.10 or later, Git and the pinned source files are needed to build.
The builder downloads nothing. The [recorded asset helper](../../assets/README.md)
retrieves the **13** files listed in
[the accepted review receipts](../immediate_repeat_image_review.json) into
a local image directory outside Git checkouts, verifying each recorded hash
before installing a file. Existing verified files are reused. Alternatively,
collect them using each recorded `url` and `file_name` verbatim.
They comprise ten JPEG windows and three service-info responses. A changed
response fails verification; keep the accepted record and inspect the change
rather than silently replacing a fingerprint. No image/corpus binaries belong
in the repository.

From the repository root, replace the capitalized paths below with local paths:

```sh
python3 scripts/fetch_recorded_viewer_assets.py \
  --study immediate-repeat --directory LOCAL_IMAGE_DIRECTORY
python3 scripts/build_immediate_repeat_viewer.py \
  --image-directory LOCAL_IMAGE_DIRECTORY --output FRESH_LOCAL_PACKET_DIRECTORY
python3 scripts/build_immediate_repeat_viewer.py \
  --image-directory LOCAL_IMAGE_DIRECTORY --check FRESH_LOCAL_PACKET_DIRECTORY
python3 -m http.server 8765 --bind 127.0.0.1 \
  --directory FRESH_LOCAL_PACKET_DIRECTORY
```

The helper requires an internet connection for missing assets. Its retrieval
receipts stay in the cache; the builder copies only the 13 recorded assets.
Keep the image cache and fresh packet directory separate.

Open `http://127.0.0.1:8765/index.html` while the local server runs. Opening the
HTML file directly also displays the packet; browser byte checks require a
local HTTP server with Web Crypto. Every image has an original Yale link.
Native text and links remain available if an image fails. No Python/Git/backend
is needed merely to open the completed packet.

The output must be outside the checkout and separate from the image inputs,
either absent or an empty unlinked directory. Files are created exclusively;
existing populated packets are not overwritten. Build bytes are complete before
the last directory check. Check mode rejects missing/extra files and linked or
changed page/assets/manifest files. Unrelated files in the input directory are
never copied. These path checks do not provide an atomic filesystem transaction.

## What is preserved

[inputs.json](inputs.json) pins four inputs to accepted merge
`9ff8325887ebf9d0ee9f3e2744e6d30c0ad760d4`. The builder checks current byte
hashes against the actual Git blobs, replays the complete source selection,
checks the review's selection fingerprint and provisional structure, and
verifies every local file's bytes and recorded dimensions. Later changes
require an explicit reviewed input update. `packet.json` records input,
generator, template and settings fingerprints plus hashes of the page and
13 assets. The complete 15-file packet is checked byte-for-byte.

All **18** selected/preceding/following native fields and exact source-file
links are retained, with alphabets, case, punctuation, tags, braces,
apostrophes and extended notation rendered literally. All **24** source-policy
slot arrays remain in the HTML. Highlighting marks original slot indices
participating in the recorded equal-adjacent events, without image glyph boxes:

- `f1r.15`: ZL `chol` at **7–8**, IT at **6–7**. Earlier segmentation differs.
- `f4r.2`: ZL `shol` at **1–2**; IT has no event and retains `chol.shol`.
- `f2r.10`: IT `saiin` at **7–8**; ZL has no event and retains `saiin.e'a'iin`.

Indices are zero-based and source-specific. The four policy vectors within
each selected source happen to be identical here; that does not make the two
editions agree. An event sample is distinct from the globally deduplicated
repeating-type statistic. Without JavaScript, all three cases, policies and
ten windows are displayed, and native disclosures still expose neighbor text.

The original nonblind AI notes from [PR #154](https://github.com/tobrien6/voynich-manuscript-research/pull/154)
are separately collapsible and attributed. All row associations remain
provisional, with source preference unresolved. Neither file identity nor the
UI's literal-equality highlighting adjudicates glyphs, words or physical rows.
No source correction, new selection, image observation, independent human
validation, untouched material, decipherment or translation is introduced.

## Validation and delivery

```sh
python3 -m unittest discover -s tests -p 'test_immediate_repeat*.py'
```

Eight new viewer methods plus the 14 accepted source/image methods give **22**
targeted tests. They verify every literal context and source link, all policy
arrays and event highlights, ten local windows and original notes, escaping,
typed settings/commit/fingerprint drift, exact declared copying, mid-generation
asset drift, early/late directory aliases and complete packet replay.

Browser checks cover all **12** case/policy combinations and **10** window
choices, loaded dimensions and matching browser SHA-256 values, native keyboard
case/policy navigation, keyboard zoom to sixfold, and neighbor disclosures.
At **1280**, **390** and **320** pixels, the page has no horizontal overflow;
the two sources stack at narrow widths, with zoom overflow contained inside
the image window. The viewport override was reset. Temporary HTML-only QA
copies retain all 18 native fields/24 policies/ten windows without script, and
preserve native text plus the correct Yale fallback link with a missing image.
Those QA copies are removed before the canonical packet replay.

The completed viewer is a **local packet**. No public hosting URL, saved notes,
source edits, pixel publication or 99 Tokens renderer change is added. The
source inputs and images were already exposed; viewing them again creates no
untouched evaluation evidence. Independent row/glyph adjudication remains a
later research task.
