# Choose a local research tool

Use this table to find a selected accepted review aid, then follow its canonical
guide for commands, pinned inputs and output guards. The seven entries were
checked against accepted main
[`d2450f5`](https://github.com/tobrien6/voynich-manuscript-research/commit/d2450f565d9e68a363465d6a9f8c11f80686d730).
This chooser links the existing workflows; the guides retain their detailed
recipes and verification records.

| What to inspect | Canonical guide | Local execution and inputs | Network requirement | Evidence limits |
| --- | --- | --- | --- | --- |
| Three provisional f76r anchors beside literal ZL/IT context | [Live-image f76r comparison](pilot/viewer/README.md) | Open the committed `f76r.html` locally. Rebuilding uses Python 3.10+, Git and the cited history. | Native text is local; displayed Yale windows and public source links need internet. | Row/glyph associations remain provisional. Loaded dimensions do not verify live image byte hashes. |
| The same f76r comparison with cached windows and a local overview | [Offline f76r packet](pilot/offline-packet/README.md) | Build with Python 3.10+, Git/history and exactly four recorded JPEGs plus service JSON. Open the seven-file packet or use the guide's loopback server. | The helper retrieves missing assets. The constructed comparison works offline; public evidence links need internet. | Build-time hashes identify copied files. The browser checks dimensions; glyph accuracy and physical rows remain unresolved. |
| Two fixed y-lookup target/reference pairs and their native neighbors | [Lookup-pair reviewer](hypotheses/y-lookup-image-v1/viewer/README.md) | Build with Python/Git and 17 recorded files; use the tested loopback workflow. Browser Web Crypto provides the additional displayed-image hash check. | Exact cached assets support offline viewing. Source/provider links need internet when opened. | Lookup matches and related-edition agreement do not adjudicate glyph function or word boundaries. Associations stay provisional. |
| Three encoded repeat cases across editions and uncertainty policies | [Immediate-repeat reviewer](transliteration/repeat-viewer/README.md) | Build with Python 3.10+, Git/history and 13 recorded files. Use loopback HTTP for browser byte checks; the guide also describes direct-file display. | Retrieve missing files with the helper; constructed packets use local assets. Public links need internet. | Literal equality and slot highlighting identify encoded events, not verified manuscript words or glyph boxes. |
| Stored-array/EXIF orientation and pixel coordinates on 1r and 116v | [Multispectral comparison](image-index/msi-viewer/README.md) | Python 3.10+/Git builds from eight exact image files, the Read Me and manifest. JavaScript and a local HTTP server are required for this viewer. | Cache acquisition follows the intake guide. The constructed comparison is offline; provider links open on demand. | Eight files concern two surfaces. Viewports do not register captures, calibrate intensities, adjudicate glyphs or verify a legacy folio alias. |
| Exact conditional interior orders in a known IID wrapping model | [Conditional-orbit guide](line-wrap/interior/viewer/README.md) | Open committed `orbit.html` locally, with no image cache. Rebuilding requires Python 3.10+, Git and cited history. | The display works offline; clicked source links need internet. | Synthetic calibration only. Constant zero, short unscored and impossible undefined remain distinct; it establishes no manuscript geometry or reading. |
| Exact recorded inputs for the f76r, lookup and repeat packets | [Recorded asset helper](assets/README.md) | Python 3.10+, Git/history and a cache outside Git. Profiles contain 5, 17 and 13 files respectively; verified files are reused. | Missing files require public HTTPS access. Existing verified cache files need no retrieval. | Receipts/hashes establish recorded byte identity, not glyph accuracy or redistribution permission. These three profiles do not retrieve MSI inputs. |

The image/source tools present previously exposed evidence for traceable
comparison. Their software checks establish the documented workflow and file
identity; independent row/glyph adjudication remains a research task under the
[decipherment protocol](DECIPHERMENT_PROTOCOL.md). Synthetic displays describe
their stated models. Neither kind supplies a validated decipherment,
translation or untouched evaluation material.

Keep image caches, image packets and retrieval receipts local and outside Git,
using the separation/fresh-output rules in each guide. The accepted HTML pages
store no observations or source corrections. The 99 Tokens renderer presents
Markdown and folio raster plates; GitHub HTML links show source. Open the local
artifact or use the canonical guide's loopback workflow to interact with it.
