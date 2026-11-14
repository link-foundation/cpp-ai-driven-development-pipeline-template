# Dependency maintenance

CI uses Python 3.15.2, CMake 4.5.0, the explicit current GA hosted images,
Doxygen 1.18.0, and the tool versions in `scripts/requirements-*.in`.
The CMake consumer floor is 3.25 (the first version with the workflow presets
and FetchContent SYSTEM support we use); the policy range is tested through
4.5. The library still requires C++20.

## Python resolution

The `.in` files are the direct dependency inputs. Generated `.txt` files
include `constraints.txt`, a complete universal resolution for Python 3.15
on Linux, macOS and Windows. Every pip install of an existing requirements
file therefore uses the same transitive versions. Do not edit the generated
files independently. Install the tools with:

```bash
python3 -m pip install -r scripts/requirements-ci.txt -r scripts/requirements-security.txt -r scripts/requirements-toolchain.txt
```

After changing the direct pins, regenerate with the pinned uv version:

```bash
uv pip compile --upgrade --universal --python-version 3.15 scripts/requirements-ci.in scripts/requirements-security.in scripts/requirements-toolchain.in --no-header --output-file scripts/constraints.txt
for group in ci security toolchain; do
  uv pip compile --no-deps --no-header "scripts/requirements-$group.in" --output-file "scripts/requirements-$group.txt"
  # Insert the shared constraints before the generated pins.
  sed -i '1i-c constraints.txt' "scripts/requirements-$group.txt"
done
```

Run `python3 -m pytest scripts/tests` and audit the committed resolution:

```bash
python3 -m pip_audit --strict -r scripts/requirements-ci.txt -r scripts/requirements-security.txt -r scripts/requirements-toolchain.txt --format=json --output=build/pip-audit.json
python3 scripts/check_python_audit.py build/pip-audit.json
```

## Native dependencies and audits

GoogleTest and Google Benchmark versions and source hashes live in
`cmake/Dependencies.cmake`; the CPM consumer pins its bootstrap script and
hash. `vcpkg.json` pins the registry baseline. Native build tools resolved
through Conan and vcpkg are included in the Security workflow's reports.
CMake is installed from its upstream release because PyPI currently lags
behind the 4.5.0 release. No compatibility policy override is used to make
outdated dependencies build.

Conan's supported audit provider requires a free registered account and the
repository secret `CONAN_AUDIT_PROVIDER_TOKEN_CONANCENTER`, obtained at
https://audit.conan.io/register. Without it, native audits retain resolved
coordinates and report **incomplete**: pull requests warn, while main,
scheduled and manual runs fail with setup instructions. A passing pull
request is not evidence of a completed native vulnerability audit. Unknown
coordinates, findings and provider errors always fail. Do not suppress this
gate to make the default branch green.

## Automated updates

Dependabot covers Actions at `/`, all Python inputs/resolutions in `/scripts`,
pre-commit, npm and the vcpkg manifest at `/`. CMake archive pins, CPM,
Doxygen, Python and the hosted image labels require periodic release review;
Dependabot has no manager that updates these literals. Historical case
studies and saved investigation logs intentionally retain original versions.

See the [issue 30 evidence](../dev/log/issues/30/pulls/31/DEPENDENCIES.md) for
registry-derived before/latest tables, migration decisions and exceptions.

## Credential scanner

Node and npm versions are declared in `.node-version` and `package.json`.
Use `npm ci --ignore-scripts` and `npm test`; the latter checks detection,
formatters and parser migrations before scanning the repository. The npm lock
and tested overrides keep the scanner's transitive packages current while
upstream dependency-range requests are pending. Remove overrides when the
upstream parent ranges support those releases.

The project scanner audit has zero findings. The latest npm CLI 12.2.2 itself
still bundles affected glob/minimatch packages; its separate audit and
[upstream report](https://github.com/npm/cli/issues/10299) remain explicit
limitations. Do not describe a clean project audit as a clean CLI bundle.
