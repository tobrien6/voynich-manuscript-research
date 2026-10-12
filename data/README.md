# Pinned transliteration sources

The five export files in `raw/` are unmodified downloads from René Zandbergen's
[transliteration catalogue](https://voynich.nu/transcr.html), retrieved on
2026-10-11 in America/New_York (2026-10-12 UTC). Credits, source URLs, declared
versions, byte lengths, and SHA-256 digests are in [transliterations.json](transliterations.json).

The publisher's [licence statement](https://voynich.nu/roadmap.html) makes the
collected transliterations available under CC0. That statement concerns these
text datasets; it does not grant rights to the site's fonts or Yale images.
The original file comments remain source commentary, not findings independently
verified by this project.

See the [selection decision and coverage audit](../research/transliteration/DECISION.md).
The [comparator extension](../research/transliteration/COMPARATORS.md) adds native
v101 and full/basic reference-Eva exports while retaining their separate roles.
Exploratory [token and repetition baselines](../research/transliteration/BASELINES.md)
compare uncertainty policies on paired loci.
Run the audit offline with Python 3.10 or later:

```sh
python3 scripts/audit_transliterations.py --check research/transliteration/coverage_audit.json
python3 -m unittest discover -s tests -v
```

The conventional IVTFF page/locus reader preserves text annotations. It does not
resolve alternatives, turn EVA letters into manuscript glyph counts, identify
language, or translate text.
