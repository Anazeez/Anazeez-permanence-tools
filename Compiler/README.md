# Compiler

Deterministic tooling for Project Permanence.

This directory will contain generators, validators, templates, bootstrap utilities, and future compiler stages.

## Contextual runway compiler

`Compiler.compiler` exposes standard-library-only functions for the
`mnemosyne.context-runway/1.0` contract:

- `compile_context_runway`
- `validate_context_runway`
- `hash_context_runway`
- `diff_context_runways`
- `verify_runway_lineage`

Compilation returns canonical JSON, a portable Markdown representation,
SHA-256 manifest identity, a content-free source manifest, validation results,
and a predecessor diff. It validates deterministic meaning only; it does not
grant capability, authority, canonical standing, publication, or activation.

Run the compiler tests with:

```bash
python3 -m unittest discover -s Compiler/tests -v
```
