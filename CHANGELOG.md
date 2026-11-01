# Changelog

## 3.0.0 — Unreleased

### Breaking changes

- Require Python 3.12 or newer.
- Replace tuple-based steps with typed `Pipeline(source).then(processor)`
  composition.
- Replace `declare.generator(inputs=...)` with `@source`; decorated sources
  bind normal arguments and return a lazy pipeline.
- Change `@processor` to bind normal configuration arguments before attaching
  it to a pipeline.
- Require explicit source iterators and item/batch yields.
- Remove public preparation/runtime state, step-name lookup, and the callable
  sub-pipeline interface.

### Fixes

- Invoke a reached source once per traversal.
- Keep iterator and last-result state local, including empty and failed runs.
- Allow independent traversals and branches from the same pipeline definition.

### Tooling

- Adopt standard package metadata, uv, `uv_build`, and a committed lockfile.
- Add complete public type annotations, strict mypy checks, and `py.typed`.
- Replace Black/Flake8 with Ruff.
- Replace retired GitHub runners with a CPython 3.12–3.15 CI matrix and built-wheel
  validation.
- Replace token-based publishing with a separate GitHub OIDC publisher gated on
  the full CI workflow.

See the [migration guide](docs/migration-v3.md) before upgrading.
