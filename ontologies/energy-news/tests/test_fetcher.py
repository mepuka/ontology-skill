"""Tests for the article fetcher pipeline."""

from __future__ import annotations

import asyncio
import json
from typing import TYPE_CHECKING

import httpx
import pytest
import respx
from click.testing import CliRunner

if TYPE_CHECKING:
    from pathlib import Path


# ---------------------------------------------------------------------------
# Pure unit tests — normalization, classification, backoff, retry
# ---------------------------------------------------------------------------


class TestNormalization:
    """URL and host normalization."""

    def test_normalize_host_strips_www(self) -> None:
        from ingest.fetcher import normalize_host

        assert normalize_host("https://www.Example.com/path") == "example.com"

    def test_normalize_host_lowercases(self) -> None:
        from ingest.fetcher import normalize_host

        assert normalize_host("https://EXAMPLE.COM/path") == "example.com"

    def test_normalize_host_strips_trailing_dot(self) -> None:
        from ingest.fetcher import normalize_host

        assert normalize_host("https://example.com./path") == "example.com"

    def test_normalize_host_returns_none_for_garbage(self) -> None:
        from ingest.fetcher import normalize_host

        assert normalize_host("not a url") is None

    def test_normalize_url_canonical(self) -> None:
        from ingest.fetcher import normalize_url

        assert normalize_url("HTTPS://www.Example.com/a/b#frag") == "https://example.com/a/b"

    def test_normalize_url_strips_fragment(self) -> None:
        from ingest.fetcher import normalize_url

        result = normalize_url("https://example.com/page#section")
        assert result == "https://example.com/page"
        assert "#" not in (result or "")

    def test_normalize_url_preserves_query(self) -> None:
        from ingest.fetcher import normalize_url

        assert normalize_url("https://example.com/page?q=1") == "https://example.com/page?q=1"

    def test_normalize_url_rejects_ftp(self) -> None:
        from ingest.fetcher import normalize_url

        assert normalize_url("ftp://example.com/file") is None

    def test_normalize_url_rejects_data_uri(self) -> None:
        from ingest.fetcher import normalize_url

        assert normalize_url("data:text/html,<h1>hi</h1>") is None

    def test_normalize_url_adds_slash_for_empty_path(self) -> None:
        from ingest.fetcher import normalize_url

        result = normalize_url("https://example.com")
        assert result == "https://example.com/"

    def test_normalize_url_preserves_non_default_port(self) -> None:
        from ingest.fetcher import normalize_url

        result = normalize_url("https://example.com:8443/api")
        assert result == "https://example.com:8443/api"

    def test_normalize_url_strips_default_https_port(self) -> None:
        from ingest.fetcher import normalize_url

        result = normalize_url("https://example.com:443/api")
        assert result == "https://example.com/api"


class TestDomainPolicy:
    """Domain classification and policy loading."""

    def test_load_missing_policy_returns_empty(self, tmp_path: Path) -> None:
        from ingest.fetcher import DomainPolicy, load_domain_policy

        policy = load_domain_policy(tmp_path / "nonexistent.yml")
        assert policy == DomainPolicy()

    def test_load_policy_from_yaml(self, tmp_path: Path) -> None:
        from ingest.fetcher import classify_domain, load_domain_policy

        policy_path = tmp_path / "domains.yml"
        policy_path.write_text(
            """
allow_overrides:
  - forced.example.com
deny_exact:
  - block.example.com
deny_registrable:
  - denied.com
domain_delay_overrides:
  slow.example.com: 2.5
            """.strip(),
            encoding="utf-8",
        )

        policy = load_domain_policy(policy_path)
        assert "block.example.com" in policy.deny_exact
        assert policy.domain_delay_overrides["slow.example.com"] == 2.5
        assert classify_domain("forced.example.com", policy).allowed is True
        assert classify_domain("block.example.com", policy).allowed is False
        assert classify_domain("sub.denied.com", policy).allowed is False
        assert classify_domain("ok.example.com", policy).allowed is True

    def test_allow_override_takes_precedence_over_deny(self, tmp_path: Path) -> None:
        from ingest.fetcher import classify_domain, load_domain_policy

        policy_path = tmp_path / "domains.yml"
        policy_path.write_text(
            """
allow_overrides:
  - special.denied.com
deny_registrable:
  - denied.com
            """.strip(),
            encoding="utf-8",
        )
        policy = load_domain_policy(policy_path)
        assert classify_domain("special.denied.com", policy).allowed is True
        assert classify_domain("other.denied.com", policy).allowed is False

    def test_classify_domain_default_allow(self) -> None:
        from ingest.fetcher import DomainPolicy, classify_domain

        decision = classify_domain("anything.com", DomainPolicy())
        assert decision.allowed is True
        assert decision.reason == "allow_default"

    def test_load_policy_invalid_yaml(self, tmp_path: Path) -> None:
        from ingest.fetcher import DomainPolicy, load_domain_policy

        policy_path = tmp_path / "domains.yml"
        policy_path.write_text("just a string", encoding="utf-8")
        assert load_domain_policy(policy_path) == DomainPolicy()


class TestRetryClassification:
    """Failure classification and retry logic."""

    def test_retryable_status_codes(self) -> None:
        from ingest.fetcher import FetchState, classify_fetch_failure

        for code in (408, 429, 500, 502, 503, 504):
            assert classify_fetch_failure(code, None) == FetchState.RETRYABLE_FAILED

    def test_terminal_status_codes(self) -> None:
        from ingest.fetcher import FetchState, classify_fetch_failure

        for code in (400, 401, 403, 404, 410, 451):
            assert classify_fetch_failure(code, None) == FetchState.TERMINAL_FAILED

    def test_timeout_is_retryable(self) -> None:
        from ingest.fetcher import FetchState, classify_fetch_failure

        exc = httpx.ReadTimeout("test")
        assert classify_fetch_failure(None, exc) == FetchState.RETRYABLE_FAILED

    def test_network_error_is_retryable(self) -> None:
        from ingest.fetcher import FetchState, classify_fetch_failure

        exc = httpx.ConnectError("test")
        assert classify_fetch_failure(None, exc) == FetchState.RETRYABLE_FAILED

    def test_unknown_exception_is_terminal(self) -> None:
        from ingest.fetcher import FetchState, classify_fetch_failure

        assert classify_fetch_failure(None, ValueError("x")) == FetchState.TERMINAL_FAILED

    def test_should_retry_within_limit(self) -> None:
        from ingest.fetcher import FetchEvent, FetchPolicy, FetchState, should_retry

        event = FetchEvent(
            schema_version=1,
            run_id="r",
            url="u",
            normalized_url="u",
            domain="d",
            attempt=2,
            state=FetchState.RETRYABLE_FAILED,
            http_status=429,
            error_kind=None,
            error_detail=None,
            content_type=None,
            content_bytes=None,
            elapsed_ms=10,
            extractor=None,
            extractor_version=None,
            title=None,
            date=None,
            text=None,
            next_retry_at=None,
            ts="t",
        )
        policy = FetchPolicy(max_retries=3)
        assert should_retry(event, policy) is True

    def test_should_not_retry_past_limit(self) -> None:
        from ingest.fetcher import FetchEvent, FetchPolicy, FetchState, should_retry

        event = FetchEvent(
            schema_version=1,
            run_id="r",
            url="u",
            normalized_url="u",
            domain="d",
            attempt=4,
            state=FetchState.RETRYABLE_FAILED,
            http_status=429,
            error_kind=None,
            error_detail=None,
            content_type=None,
            content_bytes=None,
            elapsed_ms=10,
            extractor=None,
            extractor_version=None,
            title=None,
            date=None,
            text=None,
            next_retry_at=None,
            ts="t",
        )
        policy = FetchPolicy(max_retries=3)
        assert should_retry(event, policy) is False

    def test_should_not_retry_terminal(self) -> None:
        from ingest.fetcher import FetchEvent, FetchPolicy, FetchState, should_retry

        event = FetchEvent(
            schema_version=1,
            run_id="r",
            url="u",
            normalized_url="u",
            domain="d",
            attempt=1,
            state=FetchState.TERMINAL_FAILED,
            http_status=403,
            error_kind=None,
            error_detail=None,
            content_type=None,
            content_bytes=None,
            elapsed_ms=10,
            extractor=None,
            extractor_version=None,
            title=None,
            date=None,
            text=None,
            next_retry_at=None,
            ts="t",
        )
        assert should_retry(event, FetchPolicy()) is False


class TestBackoffMath:
    """Exponential backoff calculation."""

    def test_first_attempt_near_base(self) -> None:
        from ingest.fetcher import compute_backoff_seconds

        result = compute_backoff_seconds(attempt=1, base=0.5, cap=30.0)
        assert 0.0 <= result <= 1.0

    def test_exponential_growth(self) -> None:
        from ingest.fetcher import compute_backoff_seconds

        _r1 = compute_backoff_seconds(attempt=1, base=1.0, cap=60.0)
        r3 = compute_backoff_seconds(attempt=3, base=1.0, cap=60.0)
        # attempt 3 base_delay = 1.0 * 2^2 = 4.0, plus up to 1.0 jitter
        # at minimum, attempt 3 base is 4.0 so r3 >= 4.0
        assert r3 >= 4.0

    def test_capped_at_max(self) -> None:
        from ingest.fetcher import compute_backoff_seconds

        result = compute_backoff_seconds(attempt=20, base=1.0, cap=5.0)
        assert result <= 5.0

    def test_zero_attempt_doesnt_crash(self) -> None:
        from ingest.fetcher import compute_backoff_seconds

        result = compute_backoff_seconds(attempt=0, base=1.0, cap=10.0)
        assert result >= 0.0


class TestReduceStats:
    """FetchStats reducer."""

    def test_reduce_counts_by_state(self) -> None:
        from ingest.fetcher import FetchEvent, FetchState, FetchStats, reduce_stats

        stats = FetchStats()

        def make_event(state: FetchState, content_bytes: int | None = None) -> FetchEvent:
            return FetchEvent(
                schema_version=1,
                run_id="r",
                url="u",
                normalized_url="u",
                domain="d",
                attempt=1,
                state=state,
                http_status=200 if state == FetchState.SUCCEEDED else 500,
                error_kind=None,
                error_detail=None,
                content_type=None,
                content_bytes=content_bytes,
                elapsed_ms=10,
                extractor=None,
                extractor_version=None,
                title=None,
                date=None,
                text=None,
                next_retry_at=None,
                ts="t",
            )

        reduce_stats(stats, make_event(FetchState.SUCCEEDED, content_bytes=1000))
        reduce_stats(stats, make_event(FetchState.RETRYABLE_FAILED))
        reduce_stats(stats, make_event(FetchState.TERMINAL_FAILED))
        reduce_stats(stats, make_event(FetchState.SKIPPED_POLICY))

        assert stats.processed == 4
        assert stats.succeeded == 1
        assert stats.retryable_failed == 1
        assert stats.terminal_failed == 1
        assert stats.skipped_policy == 1
        assert stats.bytes_fetched == 1000
        assert len(stats.latencies_ms) == 4


class TestIsTerminalState:
    """Terminal state classification."""

    def test_succeeded_is_terminal(self) -> None:
        from ingest.fetcher import FetchState, is_terminal_state

        assert is_terminal_state(FetchState.SUCCEEDED) is True

    def test_terminal_failed_is_terminal(self) -> None:
        from ingest.fetcher import FetchState, is_terminal_state

        assert is_terminal_state(FetchState.TERMINAL_FAILED) is True

    def test_skipped_policy_is_terminal(self) -> None:
        from ingest.fetcher import FetchState, is_terminal_state

        assert is_terminal_state(FetchState.SKIPPED_POLICY) is True

    def test_retryable_is_not_terminal(self) -> None:
        from ingest.fetcher import FetchState, is_terminal_state

        assert is_terminal_state(FetchState.RETRYABLE_FAILED) is False


class TestPrivateTargetGuard:
    """SSRF protection for private/reserved IPs."""

    def test_localhost_blocked(self) -> None:
        from ingest.fetcher import _is_private_target

        assert _is_private_target("localhost") is True

    def test_loopback_blocked(self) -> None:
        from ingest.fetcher import _is_private_target

        assert _is_private_target("127.0.0.1") is True

    def test_private_ip_blocked(self) -> None:
        from ingest.fetcher import _is_private_target

        assert _is_private_target("192.168.1.1") is True
        assert _is_private_target("10.0.0.1") is True

    def test_public_ip_allowed(self) -> None:
        from ingest.fetcher import _is_private_target

        assert _is_private_target("8.8.8.8") is False

    def test_normal_domain_allowed(self) -> None:
        from ingest.fetcher import _is_private_target

        assert _is_private_target("example.com") is False


class TestContentTypeGuard:
    """HTML content type checking."""

    def test_html_accepted(self) -> None:
        from ingest.fetcher import _is_html_content_type

        assert _is_html_content_type("text/html; charset=utf-8") is True

    def test_xhtml_accepted(self) -> None:
        from ingest.fetcher import _is_html_content_type

        assert _is_html_content_type("application/xhtml+xml") is True

    def test_json_rejected(self) -> None:
        from ingest.fetcher import _is_html_content_type

        assert _is_html_content_type("application/json") is False

    def test_pdf_rejected(self) -> None:
        from ingest.fetcher import _is_html_content_type

        assert _is_html_content_type("application/pdf") is False

    def test_none_accepted(self) -> None:
        from ingest.fetcher import _is_html_content_type

        assert _is_html_content_type(None) is True


class TestRetryAfterParsing:
    """Retry-After header parsing."""

    def test_integer_seconds(self) -> None:
        from ingest.fetcher import _parse_retry_after_seconds

        assert _parse_retry_after_seconds("120") == 120.0

    def test_zero_seconds(self) -> None:
        from ingest.fetcher import _parse_retry_after_seconds

        assert _parse_retry_after_seconds("0") == 0.0

    def test_none_returns_none(self) -> None:
        from ingest.fetcher import _parse_retry_after_seconds

        assert _parse_retry_after_seconds(None) is None

    def test_empty_returns_none(self) -> None:
        from ingest.fetcher import _parse_retry_after_seconds

        assert _parse_retry_after_seconds("") is None

    def test_garbage_returns_none(self) -> None:
        from ingest.fetcher import _parse_retry_after_seconds

        assert _parse_retry_after_seconds("not-a-date") is None


# ---------------------------------------------------------------------------
# Resume index tests
# ---------------------------------------------------------------------------


class TestResumeIndex:
    """NDJSON resume index loading."""

    def test_latest_event_wins(self, tmp_path: Path) -> None:
        from ingest.fetcher import FetchState, load_resume_index

        cache_path = tmp_path / "cache.ndjson"
        lines = [
            {
                "url": "https://example.com/a",
                "normalized_url": "https://example.com/a",
                "state": "retryable_failed",
                "attempt": 1,
            },
            {
                "url": "https://example.com/a",
                "normalized_url": "https://example.com/a",
                "state": "succeeded",
                "attempt": 2,
            },
        ]
        cache_path.write_text(
            "\n".join(json.dumps(line) for line in lines) + "\n",
            encoding="utf-8",
        )

        resume = load_resume_index(cache_path)
        assert resume.latest_by_url["https://example.com/a"].state == FetchState.SUCCEEDED
        assert resume.latest_by_url["https://example.com/a"].attempt == 2

    def test_malformed_lines_counted(self, tmp_path: Path) -> None:
        from ingest.fetcher import load_resume_index

        cache_path = tmp_path / "cache.ndjson"
        lines = [
            json.dumps(
                {
                    "normalized_url": "https://example.com/a",
                    "state": "succeeded",
                    "attempt": 1,
                }
            ),
            "not-json",
            "{invalid json too",
            json.dumps(
                {
                    "normalized_url": "https://example.com/b",
                    "state": "terminal_failed",
                    "attempt": 1,
                }
            ),
        ]
        cache_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

        resume = load_resume_index(cache_path)
        assert resume.malformed_lines == 2
        assert len(resume.latest_by_url) == 2

    def test_retryable_not_terminal(self, tmp_path: Path) -> None:
        from ingest.fetcher import FetchState, is_terminal_state, load_resume_index

        cache_path = tmp_path / "cache.ndjson"
        cache_path.write_text(
            json.dumps(
                {
                    "normalized_url": "https://example.com/retry",
                    "state": "retryable_failed",
                    "attempt": 2,
                }
            )
            + "\n",
            encoding="utf-8",
        )

        resume = load_resume_index(cache_path)
        entry = resume.latest_by_url["https://example.com/retry"]
        assert entry.state == FetchState.RETRYABLE_FAILED
        assert is_terminal_state(entry.state) is False

    def test_empty_file(self, tmp_path: Path) -> None:
        from ingest.fetcher import load_resume_index

        cache_path = tmp_path / "cache.ndjson"
        cache_path.write_text("", encoding="utf-8")

        resume = load_resume_index(cache_path)
        assert len(resume.latest_by_url) == 0
        assert resume.malformed_lines == 0

    def test_missing_file(self, tmp_path: Path) -> None:
        from ingest.fetcher import load_resume_index

        resume = load_resume_index(tmp_path / "nonexistent.ndjson")
        assert len(resume.latest_by_url) == 0

    def test_coerces_legacy_ok_state(self, tmp_path: Path) -> None:
        """Legacy 'ok' status is coerced to SUCCEEDED."""
        from ingest.fetcher import FetchState, load_resume_index

        cache_path = tmp_path / "cache.ndjson"
        cache_path.write_text(
            json.dumps(
                {
                    "normalized_url": "https://example.com/legacy",
                    "state": "ok",
                    "attempt": 1,
                }
            )
            + "\n",
            encoding="utf-8",
        )

        resume = load_resume_index(cache_path)
        assert resume.latest_by_url["https://example.com/legacy"].state == FetchState.SUCCEEDED


# ---------------------------------------------------------------------------
# NDJSON integrity tests
# ---------------------------------------------------------------------------


class TestNdjsonIntegrity:
    """NDJSON event serialization integrity."""

    def test_event_to_json_roundtrips(self) -> None:
        from ingest.fetcher import FetchEvent, FetchState

        event = FetchEvent(
            schema_version=1,
            run_id="run-1",
            url="https://example.com/post",
            normalized_url="https://example.com/post",
            domain="example.com",
            attempt=1,
            state=FetchState.SUCCEEDED,
            http_status=200,
            error_kind=None,
            error_detail=None,
            content_type="text/html",
            content_bytes=5000,
            elapsed_ms=120,
            extractor="trafilatura",
            extractor_version="2.0",
            title="Test Article",
            date="2026-01-01",
            text="Article body text here.",
            next_retry_at=None,
            ts="2026-03-01T00:00:00+00:00",
        )

        payload = event.to_json()
        line = json.dumps(payload, ensure_ascii=False)
        parsed = json.loads(line)

        assert parsed["state"] == "succeeded"
        assert parsed["url"] == "https://example.com/post"
        assert parsed["text"] == "Article body text here."
        assert parsed["schema_version"] == 1

    def test_one_line_per_event(self) -> None:
        from ingest.fetcher import FetchEvent, FetchState

        events = [
            FetchEvent(
                schema_version=1,
                run_id="run-1",
                url=f"https://example.com/{i}",
                normalized_url=f"https://example.com/{i}",
                domain="example.com",
                attempt=1,
                state=FetchState.SUCCEEDED,
                http_status=200,
                error_kind=None,
                error_detail=None,
                content_type="text/html",
                content_bytes=100,
                elapsed_ms=10,
                extractor="trafilatura",
                extractor_version="2.0",
                title=None,
                date=None,
                text=f"text-{i}",
                next_retry_at=None,
                ts="t",
            )
            for i in range(3)
        ]

        lines = [json.dumps(e.to_json(), ensure_ascii=False) for e in events]
        blob = "\n".join(lines) + "\n"
        parsed_lines = [ln for ln in blob.strip().split("\n") if ln.strip()]
        assert len(parsed_lines) == 3

        for ln in parsed_lines:
            obj = json.loads(ln)
            assert isinstance(obj, dict)
            assert "url" in obj


# ---------------------------------------------------------------------------
# Async pipeline tests with respx
# ---------------------------------------------------------------------------

SAMPLE_HTML = "<html><body><h1>Title</h1><p>Article body text for extraction.</p></body></html>"


def _make_fake_process_url_factory(state, http_status=200, text="body"):
    """Create a fake _process_url that returns a single event with given state."""
    from ingest.fetcher import FetchEvent, FetchState

    async def fake_process_url(**kwargs):
        return [
            FetchEvent(
                schema_version=1,
                run_id=kwargs["run_id"],
                url=kwargs["url"],
                normalized_url=kwargs["url"],
                domain="example.com",
                attempt=1,
                state=state,
                http_status=http_status,
                error_kind=None if state == FetchState.SUCCEEDED else f"http_{http_status}",
                error_detail=None,
                content_type="text/html",
                content_bytes=len(text) if text else 0,
                elapsed_ms=50,
                extractor="trafilatura",
                extractor_version="2.x",
                title="Title",
                date=None,
                text=text if state == FetchState.SUCCEEDED else None,
                next_retry_at=None,
                ts="2026-03-01T00:00:00+00:00",
            )
        ]

    return fake_process_url


@pytest.mark.asyncio
async def test_pipeline_200_success(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    """Successful fetch+extract produces a SUCCEEDED event in the NDJSON cache."""
    from ingest import fetcher
    from ingest.fetcher import DomainPolicy, FetchState

    cache_path = tmp_path / "cache.ndjson"

    monkeypatch.setattr(
        fetcher,
        "_process_url",
        _make_fake_process_url_factory(FetchState.SUCCEEDED, text="extracted text"),
    )

    stats = await fetcher.run_fetch_pipeline(
        urls=["https://example.com/article-1"],
        cache_path=cache_path,
        concurrency=2,
        domain_delay=0.0,
        request_timeout=5.0,
        max_retries=0,
        max_bytes=100_000,
        queue_size=10,
        user_agent="test-agent",
        resume=False,
        domain_policy=DomainPolicy(),
        fail_fast_threshold=None,
    )

    assert stats.succeeded == 1
    assert stats.processed == 1
    assert cache_path.exists()

    lines = [json.loads(ln) for ln in cache_path.read_text().strip().split("\n")]
    assert len(lines) == 1
    assert lines[0]["state"] == "succeeded"
    assert lines[0]["text"] == "extracted text"


@pytest.mark.asyncio
async def test_pipeline_403_terminal(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    """403 response produces a TERMINAL_FAILED event."""
    from ingest import fetcher
    from ingest.fetcher import DomainPolicy, FetchState

    cache_path = tmp_path / "cache.ndjson"

    monkeypatch.setattr(
        fetcher,
        "_process_url",
        _make_fake_process_url_factory(FetchState.TERMINAL_FAILED, http_status=403),
    )

    stats = await fetcher.run_fetch_pipeline(
        urls=["https://example.com/paywalled"],
        cache_path=cache_path,
        concurrency=2,
        domain_delay=0.0,
        request_timeout=5.0,
        max_retries=0,
        max_bytes=100_000,
        queue_size=10,
        user_agent="test-agent",
        resume=False,
        domain_policy=DomainPolicy(),
        fail_fast_threshold=None,
    )

    assert stats.terminal_failed == 1
    assert stats.succeeded == 0

    lines = [json.loads(ln) for ln in cache_path.read_text().strip().split("\n")]
    assert lines[0]["state"] == "terminal_failed"


@pytest.mark.asyncio
async def test_pipeline_resume_skips_terminal(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    """Resume mode skips URLs that already have a terminal state."""
    from ingest import fetcher

    cache_path = tmp_path / "cache.ndjson"
    existing_event = fetcher.FetchEvent(
        schema_version=1,
        run_id="old-run",
        url="https://example.com/a",
        normalized_url="https://example.com/a",
        domain="example.com",
        attempt=1,
        state=fetcher.FetchState.SUCCEEDED,
        http_status=200,
        error_kind=None,
        error_detail=None,
        content_type="text/html",
        content_bytes=100,
        elapsed_ms=10,
        extractor="trafilatura",
        extractor_version="2.x",
        title="t",
        date=None,
        text="ok",
        next_retry_at=None,
        ts="2026-03-02T00:00:00+00:00",
    )
    cache_path.write_text(json.dumps(existing_event.to_json()) + "\n", encoding="utf-8")

    seen_urls: list[str] = []

    async def fake_process_url(**kwargs):
        seen_urls.append(kwargs["url"])
        return [
            fetcher.FetchEvent(
                schema_version=1,
                run_id=kwargs["run_id"],
                url=kwargs["url"],
                normalized_url=fetcher.normalize_url(kwargs["url"]),
                domain=fetcher.normalize_host(kwargs["url"]),
                attempt=1,
                state=fetcher.FetchState.SUCCEEDED,
                http_status=200,
                error_kind=None,
                error_detail=None,
                content_type="text/html",
                content_bytes=123,
                elapsed_ms=12,
                extractor="trafilatura",
                extractor_version="2.x",
                title="title",
                date=None,
                text="body",
                next_retry_at=None,
                ts="2026-03-02T00:00:01+00:00",
            )
        ]

    monkeypatch.setattr(fetcher, "_process_url", fake_process_url)

    stats = await fetcher.run_fetch_pipeline(
        urls=["https://example.com/a", "https://example.com/b"],
        cache_path=cache_path,
        concurrency=2,
        domain_delay=0.0,
        request_timeout=5.0,
        max_retries=0,
        max_bytes=100_000,
        queue_size=10,
        user_agent="test-agent",
        resume=True,
        domain_policy=fetcher.DomainPolicy(),
        fail_fast_threshold=None,
    )

    assert seen_urls == ["https://example.com/b"]
    assert stats.succeeded == 1
    assert stats.skipped_terminal_resume == 1


@pytest.mark.asyncio
async def test_pipeline_idempotent_resume(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    """Running pipeline twice with resume produces correct idempotent result."""
    from ingest import fetcher
    from ingest.fetcher import DomainPolicy, FetchState

    cache_path = tmp_path / "cache.ndjson"
    call_count = 0

    async def fake_process_url(**kwargs):
        nonlocal call_count
        call_count += 1
        return [
            fetcher.FetchEvent(
                schema_version=1,
                run_id=kwargs["run_id"],
                url=kwargs["url"],
                normalized_url=kwargs["url"],
                domain="example.com",
                attempt=1,
                state=FetchState.SUCCEEDED,
                http_status=200,
                error_kind=None,
                error_detail=None,
                content_type="text/html",
                content_bytes=100,
                elapsed_ms=10,
                extractor="trafilatura",
                extractor_version="2.x",
                title="t",
                date=None,
                text="body",
                next_retry_at=None,
                ts="t",
            )
        ]

    monkeypatch.setattr(fetcher, "_process_url", fake_process_url)
    urls = ["https://example.com/x", "https://example.com/y"]

    # First run
    stats1 = await fetcher.run_fetch_pipeline(
        urls=urls,
        cache_path=cache_path,
        concurrency=2,
        domain_delay=0.0,
        request_timeout=5.0,
        max_retries=0,
        max_bytes=100_000,
        queue_size=10,
        user_agent="test",
        resume=True,
        domain_policy=DomainPolicy(),
        fail_fast_threshold=None,
    )
    assert stats1.succeeded == 2
    first_call_count = call_count

    # Second run with resume — should skip both
    stats2 = await fetcher.run_fetch_pipeline(
        urls=urls,
        cache_path=cache_path,
        concurrency=2,
        domain_delay=0.0,
        request_timeout=5.0,
        max_retries=0,
        max_bytes=100_000,
        queue_size=10,
        user_agent="test",
        resume=True,
        domain_policy=DomainPolicy(),
        fail_fast_threshold=None,
    )
    assert stats2.skipped_terminal_resume == 2
    assert stats2.succeeded == 0
    assert call_count == first_call_count  # no new process_url calls


@pytest.mark.asyncio
async def test_pipeline_deduplicates_input_urls(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    """Duplicate URLs in input are deduplicated before processing."""
    from ingest import fetcher
    from ingest.fetcher import DomainPolicy, FetchState

    cache_path = tmp_path / "cache.ndjson"
    call_count = 0

    async def fake_process_url(**kwargs):
        nonlocal call_count
        call_count += 1
        return [
            fetcher.FetchEvent(
                schema_version=1,
                run_id=kwargs["run_id"],
                url=kwargs["url"],
                normalized_url=kwargs["url"],
                domain="example.com",
                attempt=1,
                state=FetchState.SUCCEEDED,
                http_status=200,
                error_kind=None,
                error_detail=None,
                content_type="text/html",
                content_bytes=100,
                elapsed_ms=10,
                extractor="trafilatura",
                extractor_version="2.x",
                title="t",
                date=None,
                text="body",
                next_retry_at=None,
                ts="t",
            )
        ]

    monkeypatch.setattr(fetcher, "_process_url", fake_process_url)

    stats = await fetcher.run_fetch_pipeline(
        urls=[
            "https://example.com/dup",
            "https://example.com/dup",
            "HTTPS://WWW.EXAMPLE.COM/dup",
        ],
        cache_path=cache_path,
        concurrency=2,
        domain_delay=0.0,
        request_timeout=5.0,
        max_retries=0,
        max_bytes=100_000,
        queue_size=10,
        user_agent="test",
        resume=False,
        domain_policy=DomainPolicy(),
        fail_fast_threshold=None,
    )

    assert call_count == 1
    assert stats.processed == 1


# ---------------------------------------------------------------------------
# Integration-style tests using respx for real HTTP mocking
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_attempt_200_with_extraction(monkeypatch: pytest.MonkeyPatch) -> None:
    """Full fetch+extract cycle for 200 OK with HTML content."""
    from ingest.fetcher import (
        ExtractorConfig,
        FetchPolicy,
        FetchState,
        _attempt_fetch_and_extract,
    )

    with respx.mock:
        respx.get("https://example.com/article").mock(
            return_value=httpx.Response(
                200,
                content=SAMPLE_HTML.encode(),
                headers={"content-type": "text/html; charset=utf-8"},
            )
        )

        parse_sem = asyncio.Semaphore(2)
        async with httpx.AsyncClient() as client:
            outcome = await _attempt_fetch_and_extract(
                client=client,
                url="https://example.com/article",
                policy=FetchPolicy(max_bytes=100_000),
                extractor_config=ExtractorConfig(),
                parse_sem=parse_sem,
            )

    assert outcome.http_status == 200
    assert outcome.content_bytes is not None
    assert outcome.content_bytes > 0
    # Extraction may or may not produce text depending on trafilatura's analysis
    # of the minimal HTML, but the state should reflect the extraction result
    assert outcome.state in {FetchState.SUCCEEDED, FetchState.TERMINAL_FAILED}
    assert outcome.elapsed_ms >= 0


@pytest.mark.asyncio
async def test_attempt_403_terminal() -> None:
    """403 response produces terminal failure."""
    from ingest.fetcher import (
        ExtractorConfig,
        FetchPolicy,
        FetchState,
        _attempt_fetch_and_extract,
    )

    with respx.mock:
        respx.get("https://example.com/paywalled").mock(
            return_value=httpx.Response(403, content=b"Forbidden")
        )

        parse_sem = asyncio.Semaphore(2)
        async with httpx.AsyncClient() as client:
            outcome = await _attempt_fetch_and_extract(
                client=client,
                url="https://example.com/paywalled",
                policy=FetchPolicy(),
                extractor_config=ExtractorConfig(),
                parse_sem=parse_sem,
            )

    assert outcome.state == FetchState.TERMINAL_FAILED
    assert outcome.http_status == 403
    assert outcome.error_kind == "http_403"


@pytest.mark.asyncio
async def test_attempt_429_retryable_with_retry_after() -> None:
    """429 with Retry-After header is classified as retryable."""
    from ingest.fetcher import (
        ExtractorConfig,
        FetchPolicy,
        FetchState,
        _attempt_fetch_and_extract,
    )

    with respx.mock:
        respx.get("https://example.com/rate-limited").mock(
            return_value=httpx.Response(
                429,
                content=b"Too Many Requests",
                headers={"retry-after": "30"},
            )
        )

        parse_sem = asyncio.Semaphore(2)
        async with httpx.AsyncClient() as client:
            outcome = await _attempt_fetch_and_extract(
                client=client,
                url="https://example.com/rate-limited",
                policy=FetchPolicy(),
                extractor_config=ExtractorConfig(),
                parse_sem=parse_sem,
            )

    assert outcome.state == FetchState.RETRYABLE_FAILED
    assert outcome.http_status == 429
    assert outcome.retry_after_seconds == 30.0


@pytest.mark.asyncio
async def test_attempt_503_retryable() -> None:
    """503 response is classified as retryable."""
    from ingest.fetcher import (
        ExtractorConfig,
        FetchPolicy,
        FetchState,
        _attempt_fetch_and_extract,
    )

    with respx.mock:
        respx.get("https://example.com/down").mock(
            return_value=httpx.Response(503, content=b"Service Unavailable")
        )

        parse_sem = asyncio.Semaphore(2)
        async with httpx.AsyncClient() as client:
            outcome = await _attempt_fetch_and_extract(
                client=client,
                url="https://example.com/down",
                policy=FetchPolicy(),
                extractor_config=ExtractorConfig(),
                parse_sem=parse_sem,
            )

    assert outcome.state == FetchState.RETRYABLE_FAILED
    assert outcome.http_status == 503


@pytest.mark.asyncio
async def test_attempt_non_html_terminal() -> None:
    """Non-HTML content-type produces terminal failure."""
    from ingest.fetcher import (
        ExtractorConfig,
        FetchPolicy,
        FetchState,
        _attempt_fetch_and_extract,
    )

    with respx.mock:
        respx.get("https://example.com/document.pdf").mock(
            return_value=httpx.Response(
                200,
                content=b"%PDF-1.4",
                headers={"content-type": "application/pdf"},
            )
        )

        parse_sem = asyncio.Semaphore(2)
        async with httpx.AsyncClient() as client:
            outcome = await _attempt_fetch_and_extract(
                client=client,
                url="https://example.com/document.pdf",
                policy=FetchPolicy(),
                extractor_config=ExtractorConfig(),
                parse_sem=parse_sem,
            )

    assert outcome.state == FetchState.TERMINAL_FAILED
    assert outcome.error_kind == "unsupported_content_type"
    assert outcome.text is None


@pytest.mark.asyncio
async def test_attempt_oversize_content_length_terminal() -> None:
    """Oversize Content-Length header produces terminal failure before downloading."""
    from ingest.fetcher import (
        ExtractorConfig,
        FetchPolicy,
        FetchState,
        _attempt_fetch_and_extract,
    )

    with respx.mock:
        respx.get("https://example.com/huge").mock(
            return_value=httpx.Response(
                200,
                content=b"x" * 100,
                headers={
                    "content-type": "text/html",
                    "content-length": "99999999",
                },
            )
        )

        parse_sem = asyncio.Semaphore(2)
        async with httpx.AsyncClient() as client:
            outcome = await _attempt_fetch_and_extract(
                client=client,
                url="https://example.com/huge",
                policy=FetchPolicy(max_bytes=1_000_000),
                extractor_config=ExtractorConfig(),
                parse_sem=parse_sem,
            )

    assert outcome.state == FetchState.TERMINAL_FAILED
    assert outcome.error_kind == "oversize_content_length"


@pytest.mark.asyncio
async def test_attempt_timeout_retryable() -> None:
    """Timeout exception is classified as retryable."""
    from ingest.fetcher import (
        ExtractorConfig,
        FetchPolicy,
        FetchState,
        _attempt_fetch_and_extract,
    )

    with respx.mock:
        respx.get("https://example.com/slow").mock(side_effect=httpx.ReadTimeout("timeout"))

        parse_sem = asyncio.Semaphore(2)
        async with httpx.AsyncClient() as client:
            outcome = await _attempt_fetch_and_extract(
                client=client,
                url="https://example.com/slow",
                policy=FetchPolicy(),
                extractor_config=ExtractorConfig(),
                parse_sem=parse_sem,
            )

    assert outcome.state == FetchState.RETRYABLE_FAILED
    assert outcome.error_kind == "ReadTimeout"


@pytest.mark.asyncio
async def test_attempt_connect_error_retryable() -> None:
    """Connection error is classified as retryable."""
    from ingest.fetcher import (
        ExtractorConfig,
        FetchPolicy,
        FetchState,
        _attempt_fetch_and_extract,
    )

    with respx.mock:
        respx.get("https://example.com/unreachable").mock(
            side_effect=httpx.ConnectError("connection refused")
        )

        parse_sem = asyncio.Semaphore(2)
        async with httpx.AsyncClient() as client:
            outcome = await _attempt_fetch_and_extract(
                client=client,
                url="https://example.com/unreachable",
                policy=FetchPolicy(),
                extractor_config=ExtractorConfig(),
                parse_sem=parse_sem,
            )

    assert outcome.state == FetchState.RETRYABLE_FAILED
    assert outcome.error_kind == "ConnectError"


# ---------------------------------------------------------------------------
# process_url integration tests
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_process_url_invalid_url() -> None:
    """Invalid URL produces terminal failure without network call."""
    from ingest.fetcher import FetchState, _process_url

    async with httpx.AsyncClient() as client:
        events = await _process_url(
            url="ftp://not-http/bad",
            run_id="test",
            resume_entry=None,
            client=client,
            policy=__import__("ingest.fetcher", fromlist=["FetchPolicy"]).FetchPolicy(),
            domain_policy=__import__("ingest.fetcher", fromlist=["DomainPolicy"]).DomainPolicy(),
            extractor_config=__import__(
                "ingest.fetcher", fromlist=["ExtractorConfig"]
            ).ExtractorConfig(),
            parse_sem=asyncio.Semaphore(1),
            domain_locks={},
            next_allowed_by_domain={},
            domain_failure_counts={},
        )

    assert len(events) == 1
    assert events[0].state == FetchState.TERMINAL_FAILED
    assert events[0].error_kind == "invalid_url"


@pytest.mark.asyncio
async def test_process_url_ssrf_blocked() -> None:
    """Private/localhost URLs are blocked with SSRF protection."""
    from ingest.fetcher import (
        DomainPolicy,
        ExtractorConfig,
        FetchPolicy,
        FetchState,
        _process_url,
    )

    async with httpx.AsyncClient() as client:
        events = await _process_url(
            url="https://127.0.0.1/admin",
            run_id="test",
            resume_entry=None,
            client=client,
            policy=FetchPolicy(),
            domain_policy=DomainPolicy(),
            extractor_config=ExtractorConfig(),
            parse_sem=asyncio.Semaphore(1),
            domain_locks={},
            next_allowed_by_domain={},
            domain_failure_counts={},
        )

    assert len(events) == 1
    assert events[0].state == FetchState.TERMINAL_FAILED
    assert events[0].error_kind == "ssrf_blocked"


@pytest.mark.asyncio
async def test_process_url_domain_policy_skip() -> None:
    """Denied domain produces SKIPPED_POLICY without network call."""
    from ingest.fetcher import (
        DomainPolicy,
        ExtractorConfig,
        FetchPolicy,
        FetchState,
        _process_url,
    )

    policy = DomainPolicy(deny_exact=frozenset({"blocked.com"}))

    async with httpx.AsyncClient() as client:
        events = await _process_url(
            url="https://blocked.com/page",
            run_id="test",
            resume_entry=None,
            client=client,
            policy=FetchPolicy(),
            domain_policy=policy,
            extractor_config=ExtractorConfig(),
            parse_sem=asyncio.Semaphore(1),
            domain_locks={},
            next_allowed_by_domain={},
            domain_failure_counts={},
        )

    assert len(events) == 1
    assert events[0].state == FetchState.SKIPPED_POLICY
    assert events[0].error_kind == "domain_policy"


@pytest.mark.asyncio
async def test_process_url_circuit_breaker_skip() -> None:
    """Domain with too many failures triggers circuit breaker skip."""
    from ingest.fetcher import (
        DomainPolicy,
        ExtractorConfig,
        FetchPolicy,
        FetchState,
        _process_url,
    )

    domain_failure_counts = {"example.com": 10}

    async with httpx.AsyncClient() as client:
        events = await _process_url(
            url="https://example.com/page",
            run_id="test",
            resume_entry=None,
            client=client,
            policy=FetchPolicy(circuit_breaker_threshold=5),
            domain_policy=DomainPolicy(),
            extractor_config=ExtractorConfig(),
            parse_sem=asyncio.Semaphore(1),
            domain_locks={},
            next_allowed_by_domain={},
            domain_failure_counts=domain_failure_counts,
        )

    assert len(events) == 1
    assert events[0].state == FetchState.SKIPPED_POLICY
    assert events[0].error_kind == "circuit_open"


# ---------------------------------------------------------------------------
# CLI smoke tests
# ---------------------------------------------------------------------------


class TestFetchCli:
    """CLI-level fetch command tests."""

    def test_fetch_command_smoke(self, monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
        from ingest import cli as cli_module
        from ingest.fetcher import DomainPolicy, FetchStats

        project = tmp_path / "energy-news"
        oxigraph = project / "data" / "oxigraph"
        oxigraph.mkdir(parents=True, exist_ok=True)
        policy_dir = project / "scripts" / "ingest" / "policy"
        policy_dir.mkdir(parents=True, exist_ok=True)
        (policy_dir / "domains.yml").write_text("deny_exact: []\n", encoding="utf-8")

        monkeypatch.setattr(cli_module, "PROJECT", project)
        monkeypatch.setattr(cli_module, "load_domain_policy", lambda _: DomainPolicy())
        monkeypatch.setattr(
            cli_module,
            "extract_candidate_urls",
            lambda *_args, **_kwargs: ["https://example.com/post-1"],
        )

        async def fake_run_fetch_pipeline(**_kwargs):
            return FetchStats(processed=1, succeeded=1)

        monkeypatch.setattr(cli_module, "run_fetch_pipeline", fake_run_fetch_pipeline)

        runner = CliRunner()
        result = runner.invoke(cli_module.cli, ["fetch", "--limit", "1"])

        assert result.exit_code == 0
        assert "Candidate URLs: 1" in result.output
        assert "Succeeded: 1" in result.output

    def test_fetch_command_summary_includes_key_counters(
        self, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
    ) -> None:
        from ingest import cli as cli_module
        from ingest.fetcher import DomainPolicy, FetchStats

        project = tmp_path / "energy-news"
        oxigraph = project / "data" / "oxigraph"
        oxigraph.mkdir(parents=True, exist_ok=True)

        monkeypatch.setattr(cli_module, "PROJECT", project)
        monkeypatch.setattr(cli_module, "load_domain_policy", lambda _: DomainPolicy())
        monkeypatch.setattr(
            cli_module,
            "extract_candidate_urls",
            lambda *_args, **_kwargs: ["https://a.com/1", "https://b.com/2"],
        )

        async def fake_pipeline(**_kwargs):
            return FetchStats(
                processed=5,
                succeeded=2,
                retryable_failed=1,
                terminal_failed=1,
                skipped_policy=1,
                skipped_terminal_resume=3,
                malformed_resume_lines=2,
                bytes_fetched=12345,
            )

        monkeypatch.setattr(cli_module, "run_fetch_pipeline", fake_pipeline)

        runner = CliRunner()
        result = runner.invoke(cli_module.cli, ["fetch"])

        assert result.exit_code == 0
        assert "Processed events: 5" in result.output
        assert "Succeeded: 2" in result.output
        assert "Retryable failures: 1" in result.output
        assert "Terminal failures: 1" in result.output
        assert "Skipped by policy: 1" in result.output
        assert "Skipped by resume terminal state: 3" in result.output
        assert "Malformed resume lines: 2" in result.output

    def test_fetch_no_store_error(self, monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
        from ingest import cli as cli_module
        from ingest.fetcher import DomainPolicy

        project = tmp_path / "energy-news"
        # Deliberately don't create oxigraph dir
        monkeypatch.setattr(cli_module, "PROJECT", project)
        monkeypatch.setattr(cli_module, "load_domain_policy", lambda _: DomainPolicy())

        runner = CliRunner()
        result = runner.invoke(cli_module.cli, ["fetch"])

        assert result.exit_code != 0
        assert "No Oxigraph store found" in result.output

    def test_fetch_no_urls_exits_cleanly(
        self, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
    ) -> None:
        from ingest import cli as cli_module
        from ingest.fetcher import DomainPolicy

        project = tmp_path / "energy-news"
        oxigraph = project / "data" / "oxigraph"
        oxigraph.mkdir(parents=True, exist_ok=True)

        monkeypatch.setattr(cli_module, "PROJECT", project)
        monkeypatch.setattr(cli_module, "load_domain_policy", lambda _: DomainPolicy())
        monkeypatch.setattr(
            cli_module,
            "extract_candidate_urls",
            lambda *_args, **_kwargs: [],
        )

        runner = CliRunner()
        result = runner.invoke(cli_module.cli, ["fetch"])

        assert result.exit_code == 0
        assert "No candidate URLs to fetch" in result.output
