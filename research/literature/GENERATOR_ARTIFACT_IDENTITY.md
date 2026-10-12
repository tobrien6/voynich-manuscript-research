# Packaged self-citation generator: static identity follow-up

Question: is the packaged generator interchangeable with a build of the source
at its release tag? This follows the [source-method audit](COPYING_MECHANISM.md)
and checks artifacts before any runtime or manuscript comparison.

**An exact build/JAR identity is not established.** The pinned JAR contains
51 classes; compiling all 35 release Java source files produces 47. The JAR's
embedded configuration does match the release source resource byte for byte.
No generator, publisher build script, or statistical experiment was executed.
Compilation and disassembly were static inspection steps, with annotation
processing disabled. Runtime reproduction is separate work.

## Inputs and artifact observations

All inputs come from author repository commit
`9e98c9122a0f490905e8b66f3911fc7ce095fd26`, the resolved `v1.0.1` tag linked
by [Zenodo record 2531632](https://zenodo.org/records/2531632).
The [machine-readable record](generator-artifact-identity.json) pins the JAR,
every Java source file, class comparisons, selected manifest facts and resource.
The repository stores metadata and original analysis; no source archive,
compiled class, JAR, configuration payload or disassembly is redistributed.

| Artifact | Observation |
| --- | --- |
| `executable/text-generator.jar` | 194,515 bytes; SHA-256 `e9cf22d4ce50a5af6d75a17f613919e0de5d409c0232fbb6b0f7acf784dac582`. Its Git blob identity also matches the release tree. |
| Archive inventory | 68 members including 51 class files. No nested JAR/ZIP or service descriptor was found. Entries were read in memory, without archive extraction. |
| Manifest | Main class `de.voynich.text.SelfCitationTextGenerator`; Maven 3.5.3, build JDK 1.8.0_162 and external class-path entry `lib/log4j-1.2.17.jar` are declared. These are manifest statements, not an authenticated build history or resolved dependency inventory. |
| Embedded `conf.properties` | 5,165 bytes; SHA-256 `e21b977d15f7543c2d14ab91455f1a8543dba3719b4600779933de6fda62380d`; exact byte equality with `source/src/main/resources/conf.properties`. |
| External executable configuration | Differs from the embedded resource by three additional property keys: `save.length.distribution`, `stats.calculate.entropy`, and `stats.calculate.random_walk`. Other parsed key/value pairs agree. Presence of a key does not prove that this binary uses it. |

The four JAR-only class paths are `canfollow/CanFollowHelper.class`,
`canfollow/PercentCanFollow.class`, `canfollow/vms/CalcNode.class` and
`canfollow/vms/GephiNode.class`, all under `de/voynich/text/`. No class was
present only in the source build. Extra classes can be unused or retained from
another build stage; their presence does not prove different default behavior.

## Compiler-only comparison

The source inventory contains 35 `.java` files and 475,966 bytes. Every source
file's Git blob identity was checked against the pinned release tree, then its
SHA-256 recorded. All files were compiled together with `javac` 17.0.16:

```sh
javac --release 8 -g -proc:none -d REBUILT_CLASSES @PINNED_SOURCE_LIST
```

`PINNED_SOURCE_LIST` contains exactly those 35 verified source paths, one per
line. This uses the Java 8 target/API surface with a Java 17 compiler; it is
not a recreation of the manifest's original Java 8 Maven toolchain. No Maven
build, generator main method or annotation processor was run.

None of the 47 shared class files is byte-identical to its packaged counterpart.
Each shared class was disassembled with the same `javap` 17.0.16 command:

```sh
javap -p -c -constants -classpath ARTIFACT_PATH QUALIFIED_CLASS_NAME
```

The fixed comparison normalizes **only the constant-pool reference number on
an indexed instruction with a resolved `//` comment**, plus spacing before that
comment. It keeps the comment, literal strings, offsets, opcodes and other
operands. It does not normalize branch targets, instruction widths, method
order or synthetic members. Complete class attributes and bootstrap metadata
are outside this comparison. The record includes the exact
normalizer and every class's original/rebuilt byte and comparison digests.

Under this narrow normalization, 28 of the 47 shared class disassemblies match
and 19 differ. `SelfCitationTextGenerator` matches; `Config` and
`SlimGroupMorpher` do not match this strict representation. Inspected differences
include shifted branch offsets and instruction widths. Compiler-generated enum
members also differ. **No behavioral difference is inferred from these counts.**
The comparison does not prove complete semantic equivalence, nor classify every
difference's cause. The original compiler, debug metadata and code-generation
choices are not reconstructed here.

## What this resolves and what remains

The JAR and embedded resource now have reproducible byte identities. The source
inventory and shared classes can be compared without silently substituting a
source build for the packaged executable. Keep the two implementation artifacts
separate in later run records, even if their observed outputs agree.

A runtime follow-up should use the exact selected artifact, full effective
configuration, original source initialization, JVM/dependency identities and
complete seed list. It should verify repeatability and compare generated bytes
before claiming reproduction of the supplied text. Static disassembly is not a
generated-output test. Neither source/JAR correspondence nor matching generated
text establishes identity with the paper's analyzed input, or validates a
manuscript production mechanism, glyph reading or translation.

## Validation and limits

Inspected 2026-10-12 (America/New_York). JAR size, Git blob identity and SHA-256,
archive inventory, selected manifest fields, embedded/external property facts,
all 35 source identities, compiler/disassembler versions, class-set differences
and all 47 paired comparison digests were checked. Small synthetic checks ensure
that pool-index normalization preserves literal `#number` strings, numeric
operands, opcodes and branch targets. JSON, local links and outgoing scope pass.

The class hashes identify this Java 17 build and inspection representation;
another compiler can change them. The Zenodo ZIP, declared external dependency,
original build environment and paper sample remain unverified. This follow-up
does not execute the generator or perform a mechanism evaluation.

Tool contracts: [javac](https://docs.oracle.com/en/java/javase/17/docs/specs/man/javac.html)
and [javap](https://docs.oracle.com/en/java/javase/17/docs/specs/man/javap.html).
