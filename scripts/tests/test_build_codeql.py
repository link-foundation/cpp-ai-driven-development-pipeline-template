"""The manual CodeQL build must cover all translation units in both layouts."""

import importlib
import sys
from pathlib import Path

import pytest


@pytest.mark.parametrize("multi", [False, True])
def test_manual_build_uses_cpp_root_and_includes_consumers_and_conan_test(make_repo, monkeypatch, multi):
    build = importlib.import_module("build_codeql")
    repo = make_repo(multi=multi)
    root = (repo.path / "cpp" if multi else repo.path).resolve()
    calls = []
    monkeypatch.setattr(build.cp, "run", lambda command, **kwargs: calls.append((command, kwargs)))
    assert build.main([]) == 0
    assert calls[0][0] == ["cmake", "--workflow", "--preset", "release"]
    assert all(call[1]["cwd"] == root and call[1]["capture"] is False for call in calls)
    assert calls[1][0] == [sys.executable, str(Path(build.__file__).with_name("check_consumers.py")),
                           "--cpp-root", str(root)]
    assert calls[2][0] == ["c++", "-std=c++20", "-I", str(root / "include"),
                           str(root / "test_package/test_package.cpp"), "-o",
                           str(root / "build/codeql-test-package")]
    assert calls[3][0] == [str(root / "build/codeql-test-package")]


def test_failed_manual_build_does_not_continue_with_partial_extraction(make_repo, monkeypatch, capsys):
    build = importlib.import_module("build_codeql")
    make_repo()
    calls = []

    def fail(command, **kwargs):
        calls.append(command)
        raise RuntimeError("compiler failed")

    monkeypatch.setattr(build.cp, "run", fail)
    assert build.main([]) == 1
    assert len(calls) == 1
    assert "compiler failed" in capsys.readouterr().err
