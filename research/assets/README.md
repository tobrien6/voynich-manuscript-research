# Fetch the recorded local viewer assets

The accepted viewers require exact image/service files from their inspection
records. The [receipt downloader](../../scripts/fetch_recorded_viewer_assets.py)
retrieves those fixed successful resources into a local directory outside Git
checkouts. It checks recorded byte counts when present and always checks the
SHA-256 before installing a file. A byte-identical existing cache is reused.

The [source registry](recorded-viewer-sources.json) binds each record to its
accepted Git commit and digest. Later live edits to a record do not silently
change the download list. The cited Git objects must be available locally.

| Study choice | Recorded files | Existing consumer |
| --- | ---: | --- |
| `f76r` | 4 JPEG windows and 1 service JSON | [f76r review/verifier](../pilot/F76R_ANCHORS.md) |
| `y-lookup` | 12 JPEG windows, 1 GIF reference and 4 service JSONs | [local lookup viewer](../hypotheses/y-lookup-image-v1/viewer/README.md) |
| `immediate-repeat` | 10 JPEG windows and 3 service JSONs | [repeat-image packet](../transliteration/IMMEDIATE_REPEAT_IMAGES.md) |

Only recorded successful resources are requested. Earlier failed requests stay
in the original records and are not substituted with a new image or endpoint.
The repeat packet retains both f1r detail attempts, including `wide_detail`.

From the repository root, with Python 3.10+, Git and an internet connection:

```sh
python3 scripts/fetch_recorded_viewer_assets.py --study y-lookup --directory /tmp/lookup-image-inputs
python3 scripts/build_y_lookup_viewer.py --image-directory /tmp/lookup-image-inputs --output /tmp/lookup-viewer
```

Use `--study f76r` or `--study immediate-repeat` for the other records. To fetch
one exact recorded filename, repeat `--only` as needed:

```sh
python3 scripts/fetch_recorded_viewer_assets.py --study f76r --directory /tmp/f76r-image-inputs --only f76r-info.json
```

A subset is labeled separately from the complete inventory in the retrieval
receipt. The local receipt records the source commit/digest, requested URLs,
expected hashes/sizes and each resource's outcome. It uses a fresh filename on
every run, so earlier failures remain available. There is one initial retrieval attempt
per missing resource, with a 20-second default network I/O timeout (maximum 30).
Same-provider redirects are validated. Total elapsed time can exceed the I/O
timeout. Rerun the
command to retry explicitly; verified files are reused, while existing mismatches
or linked files are refused and preserved. No automatic hash refresh occurs.

Public HTTPS requests carry no authorization or cookie headers. URLs are limited
to the recorded Yale IIIF services and the exact publisher GIF endpoint; redirects
cannot change provider. Network failures, truncated responses and hash mismatches
are distinct from verified files. Failed response bytes are not installed as
assets. Fully verified bytes are staged privately and installed without replacing
an existing path; existing/symbolic/hardlink aliases and late collisions are
refused. Unrelated files in a cache remain untouched. The helper adds no package
dependencies and does not inspect pixels, adjudicate glyphs or change sources.

Keep the cache, generated packets and retrieval receipts local. Yale access and
recorded hashes do not establish an image redistribution license. These files
are inputs to the accepted local viewers, not a hosted website or an untouched
manuscript evaluation set.

## Checks

```sh
python3 -m unittest tests.test_recorded_viewer_assets -v
```

Twelve focused tests cover all 35 actual recorded entries, archived-record drift,
provider/address restrictions, exact downloads and cache reuse, partial/mismatched
responses, interrupted chunked HTTP bodies, read timeouts, malformed redirect
addresses, HTTP error-response cleanup, mixed outcomes, existing/late aliases, output isolation and preservation
of unrelated files. Validation includes one live recorded service-JSON download,
verified f76r cache reuse accepted by its existing image verifier, and all 17
lookup inputs reused to produce/check the existing complete local viewer packet.
All 13 immediate-repeat assets were reused from their accepted local cache and
passed the existing verifier with all three cases retained.
The four f76r JPEGs used for this compatibility check came from their earlier
verified local cache; no new visual observation was made. Complete fresh network
retrieval of all 35 resources is not claimed.
