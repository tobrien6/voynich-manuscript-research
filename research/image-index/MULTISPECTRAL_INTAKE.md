# Supplementary multispectral views with original file identities

The public release provides supplementary views of the first and last written
folio sides. It also contains a concrete provenance trap: two `116v_PSC.jpg`
copies have **identical stored RGB pixels but different EXIF orientation tags**.
Their file hashes differ even though they are one image. Folder placement,
filename suffix or RGB format alone does not establish an independent capture
or an unprocessed image.

## Source and fixed selection

Lisa Fagin Davis's [release notice](https://manuscriptroadtrip.wordpress.com/2024/09/08/multispectral-imaging-and-the-voynich-manuscript/)
links the [public collection](https://drive.google.com/drive/folders/1mNQGKQDSCR4M_c2M2JrsU5soghvYwMig).
Its [Read Me](https://drive.google.com/file/d/1nzKNlV2BqCEz3VvheAFZ_4IULFwLExng/view)
reports capture at Beinecke in 2014 and describes separate true-color,
processed and raw-band folders. The article is dated 2024-09-08; the Read Me
prints 2024-09-09. Preserve both dates. The rendered, visually checked PDF has
one page, 58,338 bytes and SHA-256
`02183484db3d238325d87b46f8c48676efeac53bce7a03b4af40f141fa2af157`.

The [plan](MULTISPECTRAL_INTAKE_PLAN.md) was remotely published and verified at
`f9d87ab1ca339a746a3ae5c86889d331d5f52b3c` before selected pixel inspection.
The article, ordinary Yale endpoint images, file names and Read Me were already
exposed. Select every visible JPEG in the processed `Voynich_001r` and
`Voynich_116v` subfolders, plus the separate RGB 116v copy. These are **six
provider files for two surfaces**, with another Yale reference view per surface.
No new transcription or translation is proposed.

The [record](multispectral-intake.json) preserves exact public IDs and names,
including signed component/rotation/ROI wording:

| Finite observed scope | Entries | Pixel inspection |
| --- | ---: | --- |
| Top-level folders | 4 | None as folders |
| Processed-folio folders | 10 | Only 001r and 116v |
| RGB JPEG files | 6 | Only 116v |
| Files in the two selected processed folders | 10 | All 5 JPEGs; 5 TIFFs unviewed |
| Selected provider JPEGs, including separate RGB copy | 6 | All six |
| Ordinary Yale references | 2 | 1r and 116v |

Other folder labels include `070v1` and `102v1`; they are not automatically
joined to whole Yale canvases or stripped to generic folio numbers. Other
processed subfolders, the Lab TIFF collection and raw bands were not
inventoried. This is not a complete release inventory.

## Direct observations

All six selected provider JPEGs have stored dimensions **6,132 x 8,176**. They
were fully decoded as RGB and viewed as full-frame displays reduced to
1,368 x 1,824. ROI wording does not mean the three 1r output JPEGs are spatial
crops: all show the mounted page and chart/ruler context. No enhancement,
color tuning, image registration or glyph mask was made. Known article
descriptions informed this single assistant's inspection.

For **1r**, all three palettes show the same broad writing blocks and mounting.
Dark leaf-shaped forms overlap the main writing. Lower-margin writing and
right-margin marks are more conspicuous than in the separately framed Yale
view. This full-frame comparison does not adjudicate their letters, exact
column alignment or purpose. The author's interpretations and proposed
historical attributions remain source claims, not new findings here.

For **116v**, the processed JPEG makes dense, faint reversed-looking body
writing more conspicuous. Much of it remains faint in the true-color views.
The upper writing and left-edge figures remain visible: a separate short upper
row and three longer rows. More conspicuous marks need not be writing on this
surface; show-through and processing effects require review. No words or glyphs
were newly read, and there is no calibrated legibility score or preferred
transcription.

The ordinary Yale references retain exact index/live-manifest identity: 1r
image **1006076**, 2,972 x 3,766; 116v image **1006277**, 2,686 x 3,697. The
live manifest retains accepted SHA-256
`317d58fd9ea90392a83d9858a91eada3d0b41416a3c835857dc0154bd123a309`.
Capture scale, framing and mounting differ. A shared folio label does not
provide a pixel-coordinate transform.

## The 116v orientation seam

| Copy | Public file ID | EXIF Orientation | Display when honored |
| --- | --- | ---: | --- |
| Processed folder PSC | `1UBQfNp3pm8KfGjGCcAOCV1QXF_qQdjyE` | 3 | Upper writing at top |
| RGB folder PSC | `17hqCyh3kaBU_7Twa0N2VKRZjqfmddFVL` | 1 | Same writing upside down |

Both files are 2,474,519 bytes. Direct comparison finds **one different byte at
zero-based offset 126**, within the orientation field. All non-EXIF JPEG bytes
match, including coding and scan data. Full decoding without EXIF rotation
gives the same stored RGB-array SHA-256:
`28127f7b86f70cb04930c0760bcc2e0e919659b1310410a7e9b0d6cd3daa95ff`.
Both original file hashes, ICC-profile identity and a digest excluding EXIF
segments are retained. Original files are never rewritten.

[CIPA's definitions](https://cipa.jp/std/documents/e/DC-X010-2017.pdf) place the
stored first row/column at display bottom/right for value 3, compared with
top/left for value 1. This gives a 180-degree display difference, also implemented
in [Pillow's EXIF transpose](https://pillow.readthedocs.io/en/stable/_modules/PIL/ImageOps.html).
The inspection tool honored the metadata and showed opposite displays. A later
annotation must declare stored-array versus oriented-display coordinates;
dimensions alone could transfer a mask to the opposite corner.

These are two file identities for one stored image. The separately processed
116v JPEG is another dependent view of that surface; an RGB container does not
certify true color. Preserve processing/capture dependencies when combining
observations.

## Reproduce and verify

Standard-library schema/source/header checks:

```sh
python3 -m unittest tests.test_msi_intake tests.test_folio_aliases tests.test_yale_image_index -v
python3 scripts/check_msi_intake.py
```

All **26 focused tests** pass: nine intake, eleven alias and six Yale index
tests. Synthetic headers cover both TIFF byte orders, the one-byte orientation
change, ICC chunk ordering, original hashes and malformed/truncated headers.
Tests reject changed listing identities, labels/URLs, hashes, exposure claims,
unknown fields, Boolean/decimal substitutions, duplicate JSON keys and
nonfinite values. The checker is read-only, including failure paths.

Maintainer review reproduced a decimal offset `126.0` passing an ordinary
comparison with integer `126`. The checker now compares typed canonical JSON
for that field, with a real-CLI regression covering five invalid offset forms
and preservation of the input record. The scientific record and image facts
are unchanged.

Retrieve the six exact `download_url`/`local_filename` pairs in the record to a
local directory. The two Yale `index_row` objects supply `full_image_url` and
their local names. Also keep the public Read Me as `README.pdf` and the Yale
manifest as `live-manifest.json`. Retrieval uses no cookies or account tokens.
Then run:

```sh
python3 scripts/check_msi_intake.py --cache /tmp/voynich-msi-cache
python3 scripts/check_msi_intake.py --cache /tmp/voynich-msi-cache --decode
```

`--cache` checks original file hashes, JPEG headers/orientation, ICC identities,
non-EXIF data, Read Me bytes, manifest/canvas identity and the PSC byte change.
`--decode` additionally requires Pillow and verifies every complete stored RGB
array, decoded format/mode/dimensions and pixel digest. The decoder version is
recorded; another version is accepted only if facts and bytes agree. All eight
actual images pass full decoding and cache replay. Earlier Pillow extraction
independently matched the standard-library dimensions, orientations and ICC
hashes. PDF page count was checked separately by rendering.

A pass binds the finite manually extracted listing and reported file identity.
It does not establish authority, complete release coverage, visual truth,
processing reconstruction, registration, glyph equivalence or chronology.
Default output states whether local bytes and pixels were checked. Qualified
paleographic review remains pending.

## Rights, exposure and next use

The release states permission for public viewing/free download; the Read Me
requests project/institution credit and a manuscript/folio citation. Exact
credit is retained in the record. No Creative Commons license is inferred.
Images, PDF, full responses and renders remain local. Only links, selected
metadata and original observations are published. Browser-account details,
frontend configuration, contacts and unrelated image metadata are excluded.

The [legacy 117v alias](../folio-aliases/README.md) remains unresolved: this
release's `116v` cannot establish what the older catalog meant. Registry hash
and blocked lookup are unchanged. Multiple processed views create no new
unseen folios or independent manuscript samples.

A later glyph review should choose explicit windows from pinned originals,
declare stored/oriented coordinates and processing dependencies, compare all
relevant views and retain ambiguous strokes. Qualified adjudication must
precede use of a new reading in a frozen decipherment candidate.

The [local comparison viewer](msi-viewer/README.md) provides hash-checked zoom,
independent viewports and explicit stored/EXIF pixel coordinates for these
selected originals. Its packet remains local and records the accepted source
version; it adds no glyph adjudication.
