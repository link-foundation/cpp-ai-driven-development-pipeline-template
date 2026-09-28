# Changelog Fragments

This directory contains changelog fragments that will be collected into `CHANGELOG.md` during releases.

## How to Add a Changelog Fragment

When making changes that should be documented in the changelog, create a fragment file:

```bash
# Create a new fragment (recommended - generates the file name from the date and description)
python3 scripts/create_changelog_fragment.py --bump-type patch --description "Fix overflow in add()"

# Or manually create a file matching the pattern: YYYYMMDD_HHMMSS_description.md
```

## Fragment Format

Each fragment starts with front matter that declares the semantic version bump
(`major`, `minor` or `patch`; `patch` when omitted), followed by the relevant
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/) sections:

```markdown
---
bump: minor
---

### Added
- Description of new feature

### Changed
- Description of change to existing functionality

### Fixed
- Description of bug fix

### Removed
- Description of removed feature

### Deprecated
- Description of deprecated feature

### Security
- Description of security fix
```

The highest bump among all pending fragments decides the next version.

## Why Fragments?

Using changelog fragments (similar to [Changesets](https://github.com/changesets/changesets) in JavaScript and [Scriv](https://scriv.readthedocs.io/) in Python):

1. **No merge conflicts**: Multiple PRs can add fragments without conflicts
2. **Per-PR documentation**: Each PR documents its own changes
3. **Automated collection**: Fragments are automatically collected during release
4. **Version from intent**: The bump type comes from the fragments, not from a manual edit

## During Release

On every push to `main` with pending fragments, the release workflow runs:

```bash
python3 scripts/get_bump_type.py          # highest bump of all fragments
python3 scripts/version_and_commit.py --bump-type <bump>
```

which bumps the version in `CMakeLists.txt` and `vcpkg.json`, collects the
fragments into `CHANGELOG.md` (`scripts/collect_changelog.py`), deletes them,
commits, tags and pushes. The **Changelog Fragment Check** requires a fragment
in every pull request that changes code.
