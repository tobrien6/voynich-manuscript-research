# Inspect the accepted conditional wrapping orbit

The [standalone local viewer](orbit.html) displays the accepted
[proof and exact certificates](../RESULTS.md) without recalculating scores.
Download or open `orbit.html` from a local clone in a browser. Its geometry,
tables and controls work offline; opening a cited source link requires internet.
The HTML is a synthetic illustration, with no manuscript images or source text.

For the repeated interior bag, the complete accepted values are:

| Interior order | Full centered | Half centered | Conditional order probability | Raw event weight, given first |
| --- | ---: | ---: | ---: | ---: |
| `[2, 2, 3]` | 1/4 | 0 | 1/3 | 4/3125 |
| `[2, 3, 2]` | -1/2 | -3/8 | 1/3 | 4/3125 |
| `[3, 2, 2]` | 1/4 | 3/8 | 1/3 | 4/3125 |

These nonzero realizations have zero full and half conditional means. Raw
event weights and normalized probabilities condition on different information.
The viewer keeps all eight conditions, all 173 retained row orders (172 scored),
every recorded incoming-width event, all 25 half-bag classes and the nine-stream
fixture. It distinguishes constant zero, short unscored and impossible undefined.
The exactly full final tail is unclosed and excluded; next tokens causing
overflow are carried unchanged. Early/late colors show fixed position blocks,
not glyph categories, and the half score includes the crossing pair.

The [input declaration](inputs.json) pins four actual Git blobs to accepted
merge `0245b4ed6d77a098837798ad683213aea1835278`, including certificate SHA-256
`3b2450af7a70fa5fcdddaa093f76a5c952ebedad5ada6f4f00952fcb133f8a00`.
The [builder](../../../../scripts/build_wrap_interior_viewer.py) reads those
archived blobs, so later documentary edits do not silently alter the display.
The cited Git history must be available in the clone. From the repository root:

Maintainer review restored the pinned proof's requirement that capacity be at
least the largest supported incoming width. The certificate blobs, all displayed
numbers and diagrams are unchanged. The original display at
`2f40263062bb1cac09c50738e0e3558fc4b08870` has SHA-256
`87ecb53d9402e2e3afd4a273c7818ef5fb848dd14306ba6f901b80c3aebdf47b`;
the corrected HTML has SHA-256
`9286e48111f1cfa88ac711dfb7b486b817955eb7beeb2a78a93fefe44feed04e`.
Only the model-assumption sentence differs. An existing test now checks that
restriction explicitly; the five focused tests still pass.

```sh
python3 -m unittest tests.test_wrap_interior_viewer -v
python3 scripts/build_wrap_interior_viewer.py --check research/line-wrap/interior/viewer/orbit.html
python3 scripts/build_wrap_interior_viewer.py --output /tmp/new-wrapping-orbit.html
```

Output requires a new unlinked file; existing paths and late collisions are
preserved. The browser saves no selections or observations and makes no network
requests. Keyboard selection and overview links reveal each condition. With
scripts disabled all cases, tables and expandable diagrams remain available.

This is a presentation of previously accepted mathematical calibration evidence.
It adds no simulation, fit, manuscript comparison, image inspection, source
correction, hosted interface, glyph interpretation, language or translation.
