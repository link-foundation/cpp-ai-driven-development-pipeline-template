#!/usr/bin/env python3
"""Convert a copy of this template to the multi-language layout and exercise it.

Copies the tracked files into a temporary git repository, moves the C++
project into cpp/ (as docs/multi-language.md describes), adds a stand-in
rust/ project, and runs the layout-sensitive tools against it:

* layout detection, version, tag prefix and release title;
* check-required-docs.sh (the changelog is cpp/CHANGELOG.md);
* the bump type of a fragment in cpp/changelog.d/;
* change detection: a Rust-only change must not run the C++ jobs;
* the release assets: the source archive holds only cpp/;
* the CMake dev workflow, the consumer examples and Doxygen inside cpp/
  (--build).

Usage: python3 experiments/multi_language_layout.py [--build] [--keep]
"""

from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
import tarfile
import tempfile
from pathlib import Path

TEMPLATE = Path(__file__).resolve().parents[1]
# Everything that belongs to the C++ project; .github/, scripts/, README.md,
# CONTRIBUTING.md and LICENSE stay at the repository root.
CPP_ENTRIES = (
    "CMakeLists.txt", "CMakePresets.json", "cmake", "include", "tests", "benchmarks",
    "examples", "conanfile.py", "test_package", "vcpkg.json", "packaging", "Doxyfile",
    "docs/mainpage.md", "gcovr.cfg", ".clang-format", ".clang-tidy", "CHANGELOG.md",
    "changelog.d",
)


def run(cmd, cwd, env=None, check=True, quiet=False):
    if not quiet:
        print(f"$ {' '.join(map(str, cmd))}")
    result = subprocess.run(cmd, cwd=cwd, env={**os.environ, **(env or {})},
                            capture_output=True, text=True)
    if result.stdout.strip() and not quiet:
        print(result.stdout.rstrip())
    if check and result.returncode != 0:
        print(result.stderr, file=sys.stderr)
        raise SystemExit(f"FAILED: {' '.join(map(str, cmd))}")
    return result


def git(repo, *args):
    return run(["git", *args], repo, quiet=True).stdout.strip()


def make_repository(root: Path) -> None:
    for relative in git(TEMPLATE, "ls-files").splitlines():
        source = TEMPLATE / relative
        if source.is_file() and not relative.startswith(("docs/case-studies/", "experiments/")):
            (root / relative).parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, root / relative)
    cpp = root / "cpp"
    for entry in CPP_ENTRIES:
        if (root / entry).exists():
            (cpp / entry).parent.mkdir(parents=True, exist_ok=True)
            shutil.move(str(root / entry), str(cpp / entry))
    # The C++ project is packaged on its own (git archive of cpp/), so it
    # needs its own copy of the license.
    shutil.copy2(root / "LICENSE", cpp / "LICENSE")
    (root / "rust" / "src").mkdir(parents=True)
    (root / "rust" / "src" / "lib.rs").write_text("pub fn answer() -> u32 { 42 }\n")
    git(root, "init", "-q", "-b", "main")
    git(root, "-c", "user.name=t", "-c", "user.email=t@example.com", "add", "-A")
    git(root, "-c", "user.name=t", "-c", "user.email=t@example.com", "commit", "-qm", "multi-language layout")


def expect(condition: bool, message: str) -> None:
    print(("ok   " if condition else "FAIL ") + message)
    if not condition:
        raise SystemExit(1)


def check(root: Path, build: bool) -> None:
    py = sys.executable
    field = lambda name: run([py, "scripts/get_version.py", "--print", name], root).stdout.strip()
    expect(field("cpp_root") == "cpp", "the C++ root is detected as cpp/")
    expect(field("multi_language") == "true", "the layout is multi-language")
    tag = run([py, "-c", "import sys; sys.path.insert(0, 'scripts'); import cpp_project as cp;"
                         "print(cp.build_release_tag('1.2.3', True), cp.build_release_title('1.2.3', 'x', True))"],
              root).stdout.strip()
    expect(tag == "cpp_v1.2.3 [C++] 1.2.3", "tags are cpp_vX.Y.Z and titles [C++] X.Y.Z")

    run(["bash", "scripts/check-required-docs.sh"], root)
    expect(True, "check-required-docs.sh finds cpp/CHANGELOG.md")

    output = root / "bump.out"
    run([py, "scripts/get_bump_type.py"], root, env={"GITHUB_OUTPUT": str(output)})
    expect("bump_type=minor" in output.read_text(), "the fragment in cpp/changelog.d/ decides the bump")

    base = git(root, "rev-parse", "HEAD")
    (root / "rust" / "src" / "lib.rs").write_text("pub fn answer() -> u32 { 43 }\n")
    git(root, "-c", "user.name=t", "-c", "user.email=t@example.com", "commit", "-qam", "rust only")
    output.write_text("")
    run([py, "scripts/detect_code_changes.py"], root, env={
        "GITHUB_OUTPUT": str(output), "GITHUB_EVENT_NAME": "pull_request",
        "GITHUB_BASE_SHA": base, "GITHUB_HEAD_SHA": git(root, "rev-parse", "HEAD")})
    changes = output.read_text()
    expect("any-code-changed=false" in changes and "cpp-changed=false" in changes,
           "a Rust-only change does not run the C++ jobs")

    dist = root / "dist"
    run([py, "scripts/package_release.py", "--out-dir", str(dist), "--nuget",
         "--skip-install-tree", "--repository", "acme/multi"], root)
    archive = next(dist.glob("*[0-9].tar.gz"))
    with tarfile.open(archive) as tar:
        names = tar.getnames()
    expect(any(n.endswith("/CMakeLists.txt") and n.count("/") == 1 for n in names)
           and not any("/rust/" in n or "/scripts/" in n for n in names),
           f"{archive.name} holds only the C++ project, with CMakeLists.txt at its top")

    if build:
        run(["cmake", "--workflow", "--preset", "dev"], root / "cpp")
        expect(True, "cmake --workflow --preset dev passes in cpp/")
        run([py, "scripts/check_consumers.py"], root)
        expect(True, "every consumer example builds against cpp/")
        if shutil.which("doxygen"):
            run(["doxygen", "Doxyfile"], root / "cpp", quiet=True)
            expect((root / "cpp/docs/api/html/index.html").is_file(),
                   "Doxygen builds the reference in cpp/docs/api/")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--build", action="store_true", help="also run CMake (downloads GoogleTest)")
    parser.add_argument("--keep", action="store_true", help="keep the temporary repository")
    args = parser.parse_args()
    root = Path(tempfile.mkdtemp(prefix="cpp-multi-language-"))
    try:
        make_repository(root)
        check(root, args.build)
    finally:
        if args.keep:
            print(f"kept {root}")
        else:
            shutil.rmtree(root, ignore_errors=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
