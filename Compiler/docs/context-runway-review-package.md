# Contextual runway compiler review package

- Repository: `Anazeez/Anazeez-permanence-tools`
- Branch: `codex/permanence-contextual-continuity`
- Audited compiler baseline: `df49a9f2c2023d5b37e3527012937c26dc4d9781`
- Implementation commit: `e33208f7c0cf48ac133e32121da8b32fa423197f`
- Deployment/release performed: no

The standard-library compiler implements canonical JSON, portable Markdown,
SHA-256, source manifests, validation, field diffing, and exact lineage checks.
It does not decide authority, capability, publication, or activation.

Six unit tests, Python compileall, and the existing deterministic compiler
pipeline pass. Its fixture produces byte-identical canonical JSON and the same
manifest hash as Mnemosyne-Worker commit
`97207a630485c499738a3c15451e841705045f87`.

The branch includes the three audited compiler-foundation commits above remote
main because the new compiler reuses that deterministic core. Their grouped
scope is compiler IR/canonicalization, local binary ignore rules, and Python
pipeline compatibility; no runtime deployment or secret-bearing state is
included.

Rollback: revert only
`e33208f7c0cf48ac133e32121da8b32fa423197f`, then run
`python3 -m unittest discover -s Compiler/tests -v` and
`bash Compiler/bootstrap/pipeline.sh`. No Worker Runway record is altered by a
tooling rollback.

Unresolved: repository review of the compiler-foundation ancestry, release tag,
package/install contract, and downstream adoption.
