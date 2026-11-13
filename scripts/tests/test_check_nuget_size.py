"""Small ZIP fixtures cover byte boundaries without allocating large packages."""

from pathlib import Path
import os
import subprocess
import zipfile

import pytest

import check_nuget_size as size
import pack_nuget
from .test_packaging import nuget_values

SCRIPTS = Path(__file__).resolve().parents[1]


@pytest.fixture()
def package(tmp_path):
    path = tmp_path / "test.1.0.0.nupkg"
    with zipfile.ZipFile(path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        archive.writestr("small.hpp", "a")
        archive.writestr("large.lib", bytes(range(256)) * 8)
    return path


@pytest.mark.parametrize("offset,expected", [(-1, 1), (0, 0), (1, 0)])
def test_exact_compressed_byte_boundary(package, monkeypatch, capsys, offset, expected):
    monkeypatch.setenv("NUGET_MAX_PACKAGE_BYTES", str(package.stat().st_size + offset))
    assert size.main([str(package)]) == expected
    output = capsys.readouterr()
    assert "budget" in output.out
    if expected:
        assert "::error title=NuGet package size check failed::" in output.err
        assert output.err.index("large.lib") < output.err.index("small.hpp")
        assert "compressed bytes / uncompressed bytes" in output.err
        assert "split native platforms" in output.err


@pytest.mark.parametrize("budget", ["zero", "-1", "0", "1.5"])
def test_invalid_budget_fails_closed(package, monkeypatch, capsys, budget):
    monkeypatch.setenv("NUGET_MAX_PACKAGE_BYTES", budget)
    assert size.main([str(package)]) == 1
    assert "positive integer" in capsys.readouterr().err


def test_default_budget(package, monkeypatch, capsys):
    monkeypatch.delenv("NUGET_MAX_PACKAGE_BYTES", raising=False)
    assert size.DEFAULT_MAX_BYTES < 250_000_000
    assert size.main([str(package)]) == 0
    assert "249,000,000" in capsys.readouterr().out
    monkeypatch.setenv("NUGET_MAX_PACKAGE_BYTES", "")
    assert size.main([str(package)]) == 0


@pytest.mark.parametrize("exists", [False, True])
def test_missing_or_invalid_package(tmp_path, exists, capsys):
    path = tmp_path / "broken.nupkg"
    if exists:
        path.write_text("not a zip")
    assert size.main([str(path)]) == 1
    assert "::error" in capsys.readouterr().err


def test_pack_rejects_over_budget_package(make_repo, tmp_path, monkeypatch):
    repo = make_repo()
    monkeypatch.setenv("NUGET_MAX_PACKAGE_BYTES", "1")
    with pytest.raises(ValueError, match="exceeding"):
        pack_nuget.pack(repo.layout, tmp_path / "out", nuget_values())


def test_restore_check_rejects_before_any_dotnet_call(package, tmp_path):
    stub = tmp_path / "dotnet"
    calls = tmp_path / "calls"
    stub.write_text('#!/bin/sh\necho called >> "$CALLS"\nexit 1\n')
    stub.chmod(0o755)
    result = subprocess.run(
        ["bash", str(SCRIPTS / "check-nuget-package.sh"), str(package)],
        env={**os.environ, "PATH": f"{tmp_path}{os.pathsep}{os.environ['PATH']}",
             "CALLS": str(calls), "NUGET_MAX_PACKAGE_BYTES": "1"},
        text=True, capture_output=True, timeout=15,
    )
    assert result.returncode != 0
    assert "exceeding" in result.stderr
    assert not calls.exists()
