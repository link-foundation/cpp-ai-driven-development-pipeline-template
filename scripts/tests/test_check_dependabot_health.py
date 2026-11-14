"""Small offline checks of the scheduled Dependabot backlog monitor."""

from __future__ import annotations

import json
import subprocess
from datetime import datetime, timedelta, timezone

import pytest

import check_dependabot_health as health

NOW = datetime(2026, 11, 14, tzinfo=timezone.utc)


def pull(number=26, age=15, author="dependabot[bot]", state="open"):
    return {
        "number": number, "title": "Bump CI tools", "state": state,
        "user": {"login": author},
        "created_at": (NOW - timedelta(days=age)).isoformat(),
        "updated_at": NOW.isoformat(),  # Rebases must not reset the age budget.
        "html_url": f"https://github.com/owner/repo/pull/{number}",
    }


@pytest.mark.parametrize("age,expected", [(0, False), (13.9, False), (14, False), (14.001, True), (52, True)])
def test_age_budget_uses_creation_time_and_exact_boundary(age, expected):
    found = health.stale_pulls([pull(age=age)], NOW, 14)
    assert bool(found) == expected
    if found:
        assert found[0][1] == pytest.approx(age)


def test_custom_budget_and_non_dependabot_prs():
    pulls = [pull(), pull(author="human"), pull(author="dependabot"),
             pull(author="renovate[bot]"), pull(state="closed")]
    assert health.stale_pulls(pulls, NOW, 14) == [(pull(), 15)]
    assert health.stale_pulls(pulls, NOW, 30) == []


@pytest.fixture
def api(monkeypatch):
    calls = []

    class Clock(datetime):
        @classmethod
        def now(cls, tz=None):
            return NOW

    monkeypatch.setattr(health, "datetime", Clock)

    def serve(pages=None, error="", raw=None):
        def run(command, **kwargs):
            calls.append(command)
            assert kwargs["capture_output"] and kwargs["text"]
            return subprocess.CompletedProcess(command, int(bool(error)),
                                               json.dumps(pages) if raw is None else raw, error)
        monkeypatch.setattr(health.subprocess, "run", run)
        return calls

    return serve


def test_paginated_get_includes_later_pages_and_no_search_cap(api):
    calls = api([[pull(author="human")] * 100, [pull()]])
    pulls = health.fetch_open_pulls("owner/repo")
    assert health.stale_pulls(pulls, NOW, 14) == [(pull(), 15)]
    assert calls == [["gh", "api", "--paginate", "--slurp",
                      "repos/owner/repo/pulls?state=open&per_page=100"]]


def test_main_reports_every_stale_pr_with_links_and_remediation(api, capsys):
    api([[pull(age=60)], [pull(number=27, age=61)]])
    assert health.main(["--repository", "owner/repo"]) == 1
    output = capsys.readouterr().out
    for number in (26, 27):
        assert f"https://github.com/owner/repo/pull/{number}" in output
    assert "::error title=Dependabot health::" in output
    assert "Review and merge" in output and "close it if obsolete" in output
    assert "2 stale Dependabot" in output


@pytest.mark.parametrize("pages", [[], [[]], [[pull(author="human")]], [[pull(state="closed")]]])
def test_main_passes_empty_or_non_dependabot_backlogs(api, capsys, pages):
    api(pages)
    assert health.main(["--repository", "owner/repo"]) == 0
    assert "No open Dependabot pull requests older than 14 days" in capsys.readouterr().out


def test_main_uses_environment_configuration(api, monkeypatch, capsys):
    calls = api([[pull(age=1)]])
    monkeypatch.setenv("GITHUB_REPOSITORY", "configured/repository")
    monkeypatch.setenv("DEPENDABOT_MAX_OPEN_DAYS", "9999")
    assert health.main([]) == 0
    assert calls[0][-1].startswith("repos/configured/repository/")
    assert "9999 days" in capsys.readouterr().out


@pytest.mark.parametrize("value", ["0", "-1", "", "garbage", "1.5"])
def test_invalid_age_budget_fails_without_an_api_call(api, capsys, value):
    calls = api([[]])
    assert health.main(["--repository", "owner/repo", "--max-open-days", value]) == 1
    assert calls == []
    assert "Health check could not complete" in capsys.readouterr().out


def test_missing_repository_fails_explicitly(api, capsys, monkeypatch):
    monkeypatch.delenv("GITHUB_REPOSITORY", raising=False)
    calls = api([[]])
    assert health.main([]) == 1
    assert not calls
    assert "owner/repo" in capsys.readouterr().out


@pytest.mark.parametrize("response", ["not json", '{}', '[{}]', '[[null]]'])
def test_malformed_api_data_cannot_report_health(api, capsys, response):
    api(raw=response)
    assert health.main(["--repository", "owner/repo"]) == 1
    assert "Health check could not complete" in capsys.readouterr().out


def test_api_refusal_is_visible_and_fails_closed(api, capsys):
    api(error="HTTP 403: Resource not accessible by integration")
    assert health.main(["--repository", "owner/repo"]) == 1
    assert "HTTP 403" in capsys.readouterr().out


@pytest.mark.parametrize("created", [None, "invalid date", "2026-01-01T00:00:00"])
def test_invalid_bot_creation_time_fails_closed(api, capsys, created):
    candidate = pull()
    if created is None:
        del candidate["created_at"]
    else:
        candidate["created_at"] = created
    api([[candidate]])
    assert health.main(["--repository", "owner/repo"]) == 1
    assert "Health check could not complete" in capsys.readouterr().out


def test_api_text_cannot_inject_workflow_commands(api, capsys):
    candidate = pull(age=60)
    candidate["title"] = "100% update\r\n::notice::spoof"
    api([[candidate]])
    assert health.main(["--repository", "owner/repo"]) == 1
    output = capsys.readouterr().out
    assert "100%25 update%0D%0A::notice::spoof" in output
    assert "\n::notice::" not in output


def test_verbose_tracing_is_off_by_default_and_opt_in(monkeypatch, capsys):
    monkeypatch.delenv("CI_VERBOSE", raising=False)
    health.stale_pulls([pull()], NOW, 14)
    assert capsys.readouterr().out == ""
    monkeypatch.setenv("CI_VERBOSE", "true")
    health.stale_pulls([pull()], NOW, 14)
    assert "PR #26: 15.00 days open" in capsys.readouterr().out
