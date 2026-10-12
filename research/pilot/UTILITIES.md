# Verify and export the accepted pilot inventory

The canonical [inventory](inventory.json) retains all ten accepted records and
their inspection fingerprints. With a local Yale manifest, the existing
metadata verifier can also check the recorded inspection JPEGs:

```sh
python3 scripts/verify_pilot.py --manifest LOCAL_MANIFEST --images LOCAL_IMAGE_DIRECTORY
```

Name each image `IMAGE_ID.jpg`, using the inventory's `image_id`. These must be
the recorded inspection derivatives, not differently sized or newly processed
images. Missing or different bytes fail verification. The command downloads
nothing, writes nothing and does not certify the visual observations.

Add `--csv` to stream all canonical records to standard output after successful
verification. Status messages go to standard error. Every inventory field is
retained; lists and objects use JSON within their CSV cells. This avoids a
second manually maintained inventory or provenance ledger. Without `--images`,
the command retains its metadata-only behavior and explicitly says image bytes
were not checked.

This preserves the useful CSV representation and optional local checksum check
from [superseded PR #14](https://github.com/tobrien6/voynich-manuscript-research/pull/14),
whose original contribution is commit `41979ac298483be56100a04c08c6cfda6fdb4e18`.
The accepted observations from PR #5 remain authoritative. The obsolete CSV,
duplicate provenance ledger and duplicate selection implementation are omitted;
no observation, image, source, sampling rule or scientific result is changed.

Three CLI tests cover all ten synthetic image files, complete CSV round-tripping
including nested uncertainty/source fields, failure before CSV emission for
missing or changed images, preserved input bytes and the metadata-only mode.
These are software checks, not new manuscript-image inspection.
