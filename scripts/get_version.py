#!/usr/bin/env python3
"""Print the C++ project version and export release metadata to GITHUB_OUTPUT.

Usage: python3 scripts/get_version.py [--cpp-root DIR]

Outputs: version, tag, tag_prefix, title, package_name, port_name, cpp_root,
multi_language.
"""

from __future__ import annotations

import argparse
import sys

import cpp_project as cp


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    cp.add_cpp_root_argument(parser)
    args = parser.parse_args(argv)

    layout = cp.detect_layout(cpp_root=args.cpp_root)
    name = cp.read_project_name(layout.cmake_file)
    version = cp.read_project_version(layout.cmake_file)
    port_name = cp.read_vcpkg_name(layout.vcpkg_manifest) or name.replace("_", "-").lower()

    cp.set_output("version", version)
    cp.set_output("tag", cp.build_release_tag(version, layout.multi_language))
    cp.set_output("tag_prefix", cp.get_tag_prefix(layout.multi_language))
    cp.set_output("title", cp.build_release_title(version, name, layout.multi_language))
    cp.set_output("package_name", name)
    cp.set_output("port_name", port_name)
    cp.set_output("cpp_root", layout.relative(layout.root) or ".")
    cp.set_output("multi_language", layout.multi_language)
    return 0


if __name__ == "__main__":
    sys.exit(main())
