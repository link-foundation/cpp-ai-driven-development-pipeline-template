#!/usr/bin/env python3
"""Build all C++ entry points under CodeQL's manual compiler tracing on Linux.

The release preset supplies C++20, real dependency headers, tests, examples
and benchmarks. The existing consumer checker covers each distribution path;
Conan's standalone package test is compiled and run separately.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import cpp_project as cp


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    cp.add_cpp_root_argument(parser)
    args = parser.parse_args(argv)
    root = cp.detect_layout(cpp_root=args.cpp_root).root.resolve()
    package_test = root / "build" / "codeql-test-package"
    commands = [
        ["cmake", "--workflow", "--preset", "release"],
        [sys.executable, str(Path(__file__).with_name("check_consumers.py")),
         "--cpp-root", str(root)],
        ["c++", "-std=c++20", "-I", str(root / "include"),
         str(root / "test_package" / "test_package.cpp"), "-o", str(package_test)],
        [str(package_test)],
    ]
    try:
        for command in commands:
            print("+ " + " ".join(command), flush=True)
            cp.run(command, cwd=root, capture=False)
    except (OSError, RuntimeError) as exc:
        cp.error(str(exc), title="CodeQL build")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
