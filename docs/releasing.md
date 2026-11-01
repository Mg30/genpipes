# Releasing genpipes

The package version is defined once in `pyproject.toml`. The release workflow
runs only for pushed `v*` tags, and rejects a tag that does not exactly match
`v` followed by the built package version.

Merging a PR does not publish a package.

## One-time Trusted Publisher setup

Before pushing a release tag, configure the GitHub environment `pypi` and
verify the following Trusted Publisher on the existing PyPI project:

| PyPI setting | Value |
| --- | --- |
| Project | `genpipes` |
| Owner | `Mg30` |
| Repository | `genpipes` |
| Workflow filename | `release.yml` |
| Environment | `pypi` |

These settings must match exactly. The workflow alone cannot create the PyPI
trust binding. Select the intended release-tag restrictions and approvals for
the GitHub environment before enabling publication.

The publish job receives `id-token: write` and uses PyPI Trusted Publishing.
It has no checkout or build step and does not use `PYPITOKEN`. Remove the old
stored credential through the account's normal credential-management process
once the OIDC setup is established.

References: [PyPI setup](https://docs.pypi.org/trusted-publishers/adding-a-publisher/),
[OIDC workflow](https://docs.pypi.org/trusted-publishers/using-a-publisher/),
[security guidance](https://docs.pypi.org/trusted-publishers/security-model/).

## Release procedure

1. Set the intended version in `pyproject.toml`, run `uv lock`, update the
   changelog, and refresh any pending-publication wording in the README.
2. Review and merge the versioned changes into `develop` with CI passing.
3. Confirm that the PyPI Trusted Publisher and GitHub `pypi` environment are
   configured. Tag the reviewed commit using `v<version>` and push that tag
   only when publication is intended.
4. The release workflow calls the same CI workflow used by PRs. It runs lint,
   formatting, strict typing, the Python matrix, and distribution checks on the
   tagged commit. The package job builds a source distribution and a wheel,
   validates their metadata, installs the wheel, and tests it outside the
   checkout.
5. Only after every validation job succeeds does the publisher download those
   exact distribution artifacts and upload them to PyPI through OIDC.
6. Verify the published version and artifacts on PyPI.

Never reuse a published version. A failed publish should be investigated before
rerunning it; the workflow does not silently skip already-published files.
