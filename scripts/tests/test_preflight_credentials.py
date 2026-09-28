"""Tests for scripts/preflight-credentials.sh.

The probes run against a local fake of the GitHub API, the NuGet gallery and a
Conan remote, so the rules -- report every failure, unknown is never a pass,
probe with a write -- are tested without touching real infrastructure.
"""

from __future__ import annotations

import json
import os
import subprocess
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
SCRIPT_PATH = ROOT / "scripts" / "preflight-credentials.sh"
REPOSITORY = "owner/repo"


class FakeEndpoints:
    """A scriptable fake of the GitHub, NuGet and Conan endpoints."""

    def __init__(self) -> None:
        self.github_status = 422
        self.nuget_status = 200
        self.conan_status = 200
        self.requests: list[tuple[str, str, dict[str, str]]] = []
        self._server = ThreadingHTTPServer(("127.0.0.1", 0), self._build_handler())
        self._thread = threading.Thread(target=self._server.serve_forever, daemon=True)
        self._thread.start()

    @property
    def url(self) -> str:
        host, port = self._server.server_address
        return f"http://{host}:{port}"

    def stop(self) -> None:
        self._server.shutdown()
        self._server.server_close()

    def _build_handler(self):
        fake = self

        class Handler(BaseHTTPRequestHandler):
            def log_message(self, *args) -> None:
                pass

            def _respond(self, status: int, body: str = "") -> None:
                self.send_response(status)
                self.send_header("Content-Length", str(len(body.encode())))
                self.end_headers()
                if body:
                    self.wfile.write(body.encode())

            def _record(self, method: str) -> None:
                length = int(self.headers.get("Content-Length") or 0)
                if length:
                    self.rfile.read(length)
                fake.requests.append((method, self.path, dict(self.headers)))

            def do_GET(self) -> None:  # noqa: N802
                self._record("GET")
                if self.path == "/conan/v2/users/authenticate":
                    self._respond(fake.conan_status, "conan-jwt" if fake.conan_status == 200 else "")
                else:
                    self._respond(404)

            def do_POST(self) -> None:  # noqa: N802
                self._record("POST")
                if self.path == f"/repos/{REPOSITORY}/git/refs":
                    self._respond(fake.github_status, json.dumps({"message": "Object does not exist"}))
                elif self.path.startswith("/api/v2/package/create-verification-key/"):
                    body = json.dumps({"Key": "secret"}) if fake.nuget_status == 200 else ""
                    self._respond(fake.nuget_status, body)
                else:
                    self._respond(404)

        return Handler


@pytest.fixture()
def fake():
    endpoints = FakeEndpoints()
    yield endpoints
    endpoints.stop()


def run_script(env: dict[str, str]) -> subprocess.CompletedProcess[str]:
    cleared = {
        key: value
        for key, value in os.environ.items()
        if not key.startswith(("GITHUB_", "NUGET_", "CONAN_"))
    }
    merged = {**cleared, "PREFLIGHT_MODE": "release", "PREFLIGHT_CURL_TIMEOUT": "5", **env}
    return subprocess.run(
        ["bash", str(SCRIPT_PATH)], cwd=ROOT, env=merged, capture_output=True, text=True
    )


def github_env(fake: FakeEndpoints) -> dict[str, str]:
    return {"GITHUB_API_URL": fake.url, "GITHUB_REPOSITORY": REPOSITORY, "GITHUB_TOKEN": "ghs_token"}


def nuget_env(fake: FakeEndpoints) -> dict[str, str]:
    return {
        "NUGET_GALLERY_URL": fake.url,
        "NUGET_PUBLISH": "true",
        "NUGET_PACKAGE_ID": "Platform.Example.TemplateLibrary",
        "NUGET_API_KEY": "oy2key",
    }


def conan_env(fake: FakeEndpoints) -> dict[str, str]:
    return {
        "CONAN_REMOTE_URL": f"{fake.url}/conan",
        "CONAN_LOGIN_USERNAME": "user",
        "CONAN_PASSWORD": "password",
    }


def test_github_write_probe_passes_on_422(fake) -> None:
    result = run_script(github_env(fake))
    assert result.returncode == 0, result.stdout + result.stderr
    assert "PASS: GitHub accepted a contents:write request" in result.stdout
    assert "Release preflight: 1 verified, 0 failed, 0 unknown" in result.stdout
    method, path, headers = fake.requests[0]
    assert (method, path) == ("POST", f"/repos/{REPOSITORY}/git/refs")
    assert headers["Authorization"] == "Bearer ghs_token"


@pytest.mark.parametrize("status", [401, 403, 404])
def test_github_refusal_fails_the_release(fake, status: int) -> None:
    fake.github_status = status
    result = run_script(github_env(fake))
    assert result.returncode == 1
    assert f"FAIL: GitHub refused the contents:write probe for {REPOSITORY} ({status})" in result.stdout
    assert "refusing to release with 1 refused credential(s)" in result.stdout


def test_missing_github_token_is_a_failure() -> None:
    result = run_script({"GITHUB_REPOSITORY": REPOSITORY})
    assert result.returncode == 1
    assert "FAIL: GITHUB_TOKEN is not set" in result.stdout


def test_report_mode_reports_failures_without_blocking(fake) -> None:
    fake.github_status = 403
    result = run_script({**github_env(fake), "PREFLIGHT_MODE": "report"})
    assert result.returncode == 0
    assert "::warning::release-preflight:" in result.stdout
    assert "Report mode: the failures above are advisory" in result.stdout


def test_unreachable_github_is_unknown_and_never_a_release_pass() -> None:
    result = run_script(
        {"GITHUB_API_URL": "http://127.0.0.1:9", "GITHUB_REPOSITORY": REPOSITORY, "GITHUB_TOKEN": "t"}
    )
    assert result.returncode == 1
    assert "UNKNOWN: the GitHub API was unreachable" in result.stdout
    assert "verified nothing (1 unknown)" in result.stdout


def test_nuget_is_skipped_unless_enabled(fake) -> None:
    result = run_script({**github_env(fake), "NUGET_API_KEY": "key"})
    assert result.returncode == 0
    assert "SKIP: NUGET_PUBLISH is not true" in result.stdout
    assert not any("verification-key" in path for _, path, _ in fake.requests)


def test_nuget_verification_key_proves_push_scope(fake) -> None:
    result = run_script({**github_env(fake), **nuget_env(fake)})
    assert result.returncode == 0, result.stdout + result.stderr
    assert "PASS: NuGet issued a verification key for Platform.Example.TemplateLibrary" in result.stdout
    assert "secret" not in result.stdout
    nuget_calls = [(p, h) for _, p, h in fake.requests if "verification-key" in p]
    assert nuget_calls[0][0].endswith("/Platform.Example.TemplateLibrary")
    assert nuget_calls[0][1]["X-NuGet-ApiKey"] == "oy2key"


def test_nuget_refusal_fails_the_release(fake) -> None:
    fake.nuget_status = 403
    result = run_script({**github_env(fake), **nuget_env(fake)})
    assert result.returncode == 1
    assert "FAIL: NuGet refused the API key for Platform.Example.TemplateLibrary (403)" in result.stdout


def test_nuget_enabled_without_key_or_id_fails(fake) -> None:
    result = run_script({**github_env(fake), **nuget_env(fake), "NUGET_API_KEY": ""})
    assert "FAIL: NUGET_PUBLISH is true but NUGET_API_KEY is missing" in result.stdout
    result = run_script({**github_env(fake), **nuget_env(fake), "NUGET_PACKAGE_ID": ""})
    assert "FAIL: NUGET_PUBLISH is true but NUGET_PACKAGE_ID is empty" in result.stdout


def test_conan_login_is_unknown_not_a_pass(fake) -> None:
    result = run_script({**github_env(fake), **conan_env(fake)})
    assert result.returncode == 0, result.stdout + result.stderr
    assert "UNKNOWN: the Conan remote accepted the login for user" in result.stdout
    assert "Release preflight: 1 verified, 0 failed, 1 unknown" in result.stdout


def test_conan_login_alone_does_not_pass_a_release(fake) -> None:
    result = run_script({**github_env(fake), "GITHUB_TOKEN": "", **conan_env(fake)})
    assert result.returncode == 1


def test_every_failure_is_reported_not_just_the_first(fake) -> None:
    fake.github_status = 403
    fake.nuget_status = 401
    fake.conan_status = 401
    result = run_script({**github_env(fake), **nuget_env(fake), **conan_env(fake)})
    assert result.returncode == 1
    assert "FAIL: GitHub refused" in result.stdout
    assert "FAIL: NuGet refused" in result.stdout
    assert "FAIL: the Conan remote refused the login" in result.stdout
    assert "refusing to release with 3 refused credential(s)" in result.stdout


def test_step_summary_receives_the_verdict(fake, tmp_path: Path) -> None:
    summary = tmp_path / "summary.md"
    result = run_script({**github_env(fake), "GITHUB_STEP_SUMMARY": str(summary)})
    assert result.returncode == 0
    written = summary.read_text()
    assert "### Release preflight (release mode)" in written
    assert "| verified | 1 |" in written
