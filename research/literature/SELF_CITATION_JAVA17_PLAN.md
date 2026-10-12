# Self-citation source replay plan

## Question and fixed scope

Can the source revision pinned by the [implementation audit](COPYING_MECHANISM.md)
produce identical output in two fresh processes here, and does that output
equal the release's supplied artifact? This is a software replay, not a test
that copying explains the manuscript, a paper replication or a decipherment.

Source: `TorstenTimm/SelfCitationTextgenerator`, release tag `v1.0.1`, commit
`9e98c9122a0f490905e8b66f3911fc7ce095fd26`. Use all 35 Java sources and the
unchanged shipped `executable/conf.properties`. Its seed is 19 and total row
count 1,200. Compare against the pinned
`executable/generate/vms_generated.txt`; keep source/configuration/output
identities distinct. Do not select another seed or modify generation rules to
improve agreement.

## Build and run protocol

1. Preserve the repository tree and SHA-256/length manifest of every downloaded
   source, resource, configuration and supplied text. Require each Git blob
   identity to match the exact commit's tree and all overlapping accepted
   fingerprints to match. Source code was inspected before this plan; no
   generated run was executed and no new output statistics were seen.
2. Build the unchanged Java sources with installed Zulu OpenJDK/javac
   `17.0.16`, UTF-8 source encoding and `--release 8`, matching the POM's Java
   1.8 language target. The inspected source imports only project, Java and
   `javax.naming` classes. Do not run Maven plugins or the packaged JAR; the
   unused POM logging dependency is outside this direct source build.
3. Use two separate fresh working directories and JVM processes. Copy the
   exact executable configuration into each as `conf.properties`; create
   `generate/` in advance. Give the JVM an explicit UTF-8 file encoding,
   fixed locale/timezone and a minimal environment excluding optional JVM
   injection variables. Capture exit status, timeout, output paths and logs
   locally. Cap each process at 60 seconds and a 256 MiB Java heap. A failed
   or timed-out attempt remains recorded; do not silently replace it.
4. The filename includes wall-clock time. Preserve its role in provenance but
   compare file **contents** separately from filename. Record whole-file byte
   hashes and lengths without deleting header lines or normalizing bytes.
5. Separately parse ASCII output into physical file-line metadata, comment
   headers and nonblank data rows. Split data rows on literal spaces; preserve
   malformed/empty slots as a failure rather than silently collapsing them.
   Report total rows, group occurrences, and input/generated-row separation.
   The first data row is the supplied manuscript-derived initial line. Exclude
   it from newly generated-row counts; preserve its input identity. These group
   strings are neither verified manuscript glyphs nor native IVTFF P0 loci.
6. Compare the two whole byte streams and data-row sequences. Compare each
   with the supplied release artifact. If unequal, report the first differing
   data-row ordinal and hashes of both row strings, plus lengths/counts, without
   searching seeds or editing the implementation. Do not redistribute source,
   binaries, logs, configuration text or generated/supplied text.

## Outcomes and limits

- Identical process outputs establish replay only for this recorded source,
  build, configuration and runtime. They do not prove cross-runtime portability.
- Equality with the supplied artifact establishes a byte match to that release
  file; it cannot establish which input, binary or sample the paper analyzed.
- Inequality remains an approximate reproduction of that release artifact;
  report it even if the broad counts agree. No matching statistic is a mechanism
  goodness-of-fit score. This plan specifies identity/count diagnostics only;
  no post hoc manuscript comparison or significance claim is authorized by it.

The initial line and manuscript corpus have already been exposed in project
work; neither becomes held-out evidence here. A subsequent mechanism experiment
needs a separately frozen measurement bridge, full candidate settings, seeds,
comparisons and ablations under the [evaluation protocol](../DECIPHERMENT_PROTOCOL.md).

Role: contributor under the user's continuing Voynich contribution goal, with
verified `tobrien6`, matching upstream owner and repository permissions. The
separate maintainer retains merge ownership. Submit original replay evidence
through a focused PR; no upstream merge or self-approval is part of this work.
