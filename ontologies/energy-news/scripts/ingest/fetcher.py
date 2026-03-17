"""Async article fetch/extract pipeline with resumable NDJSON persistence."""

from __future__ import annotations

import asyncio
import contextlib
import ipaddress
import json
import os
import random
import shutil
import time
from dataclasses import dataclass, field
from datetime import UTC, datetime, timedelta
from email.utils import parsedate_to_datetime
from enum import StrEnum
from importlib import import_module, metadata
from typing import TYPE_CHECKING
from urllib.parse import urlsplit, urlunsplit

import httpx
import yaml

from .namespaces import GRAPH_ABOX
from .store import init_store
from .store import query as store_query

if TYPE_CHECKING:
    from pathlib import Path

RETRYABLE_STATUS_CODES = {408, 425, 429, 500, 502, 503, 504}
HTML_CONTENT_TYPES = ("text/html", "application/xhtml+xml")
CHECKPOINT_EVERY = 100
JITTER_RNG = random.SystemRandom()


class FetchState(StrEnum):
    """Finite state model for URL fetch attempts."""

    SUCCEEDED = "succeeded"
    RETRYABLE_FAILED = "retryable_failed"
    TERMINAL_FAILED = "terminal_failed"
    SKIPPED_POLICY = "skipped_policy"


@dataclass(frozen=True)
class FetchPolicy:
    """Network and pipeline controls."""

    domain_delay: float = 1.0
    request_timeout: float = 20.0
    max_retries: int = 3
    backoff_base: float = 0.5
    max_backoff: float = 30.0
    max_bytes: int = 2_000_000
    queue_size: int = 200
    concurrency: int = 20
    max_redirects: int = 10
    user_agent: str = "energy-news-fetcher/1.0"
    circuit_breaker_threshold: int = 5
    progress_every: int = 50


@dataclass(frozen=True)
class DomainPolicy:
    """Declarative domain allow/deny policy."""

    deny_exact: frozenset[str] = frozenset()
    deny_registrable: frozenset[str] = frozenset()
    allow_overrides: frozenset[str] = frozenset()
    domain_delay_overrides: dict[str, float] = field(default_factory=dict)


@dataclass(frozen=True)
class DomainDecision:
    """Result of domain policy evaluation."""

    allowed: bool
    reason: str


@dataclass(frozen=True)
class ResumeEntry:
    """Latest known state for a normalized URL."""

    state: FetchState
    attempt: int
    ts: str | None


@dataclass(frozen=True)
class ResumeIndex:
    """Resumability lookup and parse diagnostics."""

    latest_by_url: dict[str, ResumeEntry]
    malformed_lines: int


@dataclass(frozen=True)
class ExtractorConfig:
    """Trafilatura extraction options."""

    fast: bool = True
    include_comments: bool = False
    include_tables: bool = False
    favor_precision: bool = True


@dataclass(frozen=True)
class ExtractResult:
    """Article extraction outcome."""

    text: str | None
    title: str | None
    date: str | None
    error_kind: str | None


@dataclass(frozen=True)
class FetchEvent:
    """Persisted NDJSON event."""

    schema_version: int
    run_id: str
    url: str
    normalized_url: str | None
    domain: str | None
    attempt: int
    state: FetchState
    http_status: int | None
    error_kind: str | None
    error_detail: str | None
    content_type: str | None
    content_bytes: int | None
    elapsed_ms: int | None
    extractor: str | None
    extractor_version: str | None
    title: str | None
    date: str | None
    text: str | None
    next_retry_at: str | None
    ts: str

    def to_json(self) -> dict[str, object]:
        """Serialize the event to a JSON-safe mapping."""
        return {
            "schema_version": self.schema_version,
            "run_id": self.run_id,
            "url": self.url,
            "normalized_url": self.normalized_url,
            "domain": self.domain,
            "attempt": self.attempt,
            "state": self.state.value,
            "http_status": self.http_status,
            "error_kind": self.error_kind,
            "error_detail": self.error_detail,
            "content_type": self.content_type,
            "content_bytes": self.content_bytes,
            "elapsed_ms": self.elapsed_ms,
            "extractor": self.extractor,
            "extractor_version": self.extractor_version,
            "title": self.title,
            "date": self.date,
            "text": self.text,
            "next_retry_at": self.next_retry_at,
            "ts": self.ts,
        }


@dataclass
class FetchStats:
    """Pipeline counters and latency sample."""

    processed: int = 0
    succeeded: int = 0
    retryable_failed: int = 0
    terminal_failed: int = 0
    skipped_policy: int = 0
    skipped_terminal_resume: int = 0
    malformed_resume_lines: int = 0
    bytes_fetched: int = 0
    latencies_ms: list[int] = field(default_factory=list)

    def as_checkpoint(self, run_id: str) -> dict[str, object]:
        """Checkpoint payload for crash-safe progress snapshots."""
        failure_total = self.retryable_failed + self.terminal_failed
        total = max(self.processed, 1)
        return {
            "run_id": run_id,
            "processed": self.processed,
            "succeeded": self.succeeded,
            "retryable_failed": self.retryable_failed,
            "terminal_failed": self.terminal_failed,
            "skipped_policy": self.skipped_policy,
            "skipped_terminal_resume": self.skipped_terminal_resume,
            "malformed_resume_lines": self.malformed_resume_lines,
            "bytes_fetched": self.bytes_fetched,
            "failure_ratio": failure_total / total,
            "ts": _now_iso(),
        }


@dataclass(frozen=True)
class _AttemptOutcome:
    """Single network+parse attempt result."""

    state: FetchState
    http_status: int | None
    error_kind: str | None
    error_detail: str | None
    content_type: str | None
    content_bytes: int | None
    elapsed_ms: int
    title: str | None
    date: str | None
    text: str | None
    retry_after_seconds: float | None


class _BodyTooLargeError(RuntimeError):
    """Raised when streamed response exceeds configured max bytes."""


def _now_iso() -> str:
    return datetime.now(UTC).isoformat(timespec="seconds")


def _future_iso(seconds: float) -> str:
    return (datetime.now(UTC) + timedelta(seconds=seconds)).isoformat(timespec="seconds")


def normalize_host(url: str) -> str | None:
    """Normalize URL host for policy and rate-limit keys."""
    try:
        parsed = urlsplit(url)
    except ValueError:
        return None

    host = parsed.hostname
    if not host:
        return None

    normalized = host.rstrip(".").lower()
    if normalized.startswith("www."):
        normalized = normalized[4:]
    return normalized or None


def normalize_url(url: str) -> str | None:
    """Canonicalize URL form for resumability indexing."""
    try:
        parsed = urlsplit(url)
    except ValueError:
        return None

    scheme = parsed.scheme.lower()
    if scheme not in {"http", "https"}:
        return None

    host = normalize_host(url)
    if host is None:
        return None

    try:
        port = parsed.port
    except ValueError:
        return None

    netloc = host
    if port is not None:
        default_port = 80 if scheme == "http" else 443
        if port != default_port:
            netloc = f"{host}:{port}"

    path = parsed.path or "/"
    return urlunsplit((scheme, netloc, path, parsed.query, ""))


def _matches_domain(host: str, candidate: str) -> bool:
    return host == candidate or host.endswith(f".{candidate}")


def _is_private_target(host: str) -> bool:
    lowered = host.lower()
    if lowered in {"localhost", "localhost.localdomain"}:
        return True

    try:
        ip_addr = ipaddress.ip_address(lowered)
    except ValueError:
        return False

    return any(
        (
            ip_addr.is_private,
            ip_addr.is_loopback,
            ip_addr.is_link_local,
            ip_addr.is_reserved,
            ip_addr.is_multicast,
            ip_addr.is_unspecified,
        )
    )


def classify_domain(domain: str, policy: DomainPolicy) -> DomainDecision:
    """Evaluate allow/deny policy for a normalized host."""
    if domain in policy.allow_overrides:
        return DomainDecision(allowed=True, reason="allow_override")

    if domain in policy.deny_exact:
        return DomainDecision(allowed=False, reason="deny_exact")

    for blocked in policy.deny_registrable:
        if _matches_domain(domain, blocked):
            return DomainDecision(allowed=False, reason=f"deny_registrable:{blocked}")

    return DomainDecision(allowed=True, reason="allow_default")


def _normalize_domain_list(raw_values: object) -> frozenset[str]:
    if not isinstance(raw_values, list):
        return frozenset()
    values: list[str] = []
    for value in raw_values:
        if isinstance(value, str):
            cleaned = value.strip().lower()
            if cleaned:
                values.append(cleaned)
    return frozenset(values)


def load_domain_policy(path: Path) -> DomainPolicy:
    """Load YAML domain policy. Missing file means empty policy."""
    if not path.exists():
        return DomainPolicy()

    raw = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    if not isinstance(raw, dict):
        return DomainPolicy()

    delay_overrides: dict[str, float] = {}
    raw_overrides = raw.get("domain_delay_overrides", {})
    if isinstance(raw_overrides, dict):
        for key, value in raw_overrides.items():
            if isinstance(key, str) and isinstance(value, int | float):
                cleaned = key.strip().lower()
                if cleaned and value >= 0:
                    delay_overrides[cleaned] = float(value)

    return DomainPolicy(
        deny_exact=_normalize_domain_list(raw.get("deny_exact")),
        deny_registrable=_normalize_domain_list(raw.get("deny_registrable")),
        allow_overrides=_normalize_domain_list(raw.get("allow_overrides")),
        domain_delay_overrides=delay_overrides,
    )


def extract_candidate_urls(
    store_path: Path,
    *,
    domain: str | None = None,
    limit: int | None = None,
) -> list[str]:
    """Read article URLs from Oxigraph ABox graph."""
    store = init_store(store_path)
    requested_domain = domain.strip().lower() if domain else None

    sparql = f"""
    PREFIX enews: <http://example.org/ontology/energy-news#>
    SELECT DISTINCT ?url
    WHERE {{
        GRAPH <{GRAPH_ABOX}> {{
            ?article a enews:Article ;
                     enews:url ?url .
        }}
    }}
    """

    seen: set[str] = set()
    urls: list[str] = []
    for row in store_query(store, sparql):
        raw_url = str(row[0].value)
        normalized = normalize_url(raw_url)
        if normalized is None or normalized in seen:
            continue

        host = normalize_host(normalized)
        if host is None:
            continue

        if requested_domain and not _matches_domain(host, requested_domain):
            continue

        seen.add(normalized)
        urls.append(normalized)
        if limit is not None and len(urls) >= limit:
            break

    return urls


def _coerce_state(raw_state: object) -> FetchState | None:
    normalized: str | None = None

    if isinstance(raw_state, FetchState):
        return raw_state
    if isinstance(raw_state, str):
        normalized = raw_state.strip().lower()

    if normalized is None:
        return None
    if normalized == "ok":
        normalized = FetchState.SUCCEEDED.value
    if normalized.startswith("error"):
        normalized = FetchState.RETRYABLE_FAILED.value

    with contextlib.suppress(ValueError):
        return FetchState(normalized)
    return None


def load_resume_index(cache_path: Path) -> ResumeIndex:
    """Load latest event state for each normalized URL from NDJSON."""
    if not cache_path.exists():
        return ResumeIndex(latest_by_url={}, malformed_lines=0)

    malformed_lines = 0
    latest_by_url: dict[str, ResumeEntry] = {}

    with cache_path.open(encoding="utf-8") as handle:
        for raw_line in handle:
            stripped = raw_line.strip()
            if not stripped:
                continue

            try:
                row = json.loads(stripped)
            except json.JSONDecodeError:
                malformed_lines += 1
                continue

            if not isinstance(row, dict):
                continue

            normalized = row.get("normalized_url")
            if not isinstance(normalized, str):
                raw_url = row.get("url")
                normalized = normalize_url(raw_url) if isinstance(raw_url, str) else None
            if not normalized:
                continue

            state = _coerce_state(row.get("state") or row.get("status"))
            if state is None:
                continue

            raw_attempt = row.get("attempt", 1)
            attempt = int(raw_attempt) if isinstance(raw_attempt, int | float | str) else 1
            attempt = max(attempt, 1)

            ts = row.get("ts")
            ts_value = str(ts) if isinstance(ts, str) else None
            latest_by_url[normalized] = ResumeEntry(state=state, attempt=attempt, ts=ts_value)

    return ResumeIndex(latest_by_url=latest_by_url, malformed_lines=malformed_lines)


def is_terminal_state(state: FetchState) -> bool:
    return state in {FetchState.SUCCEEDED, FetchState.TERMINAL_FAILED, FetchState.SKIPPED_POLICY}


def classify_fetch_failure(
    http_status: int | None,
    exc: Exception | None,
) -> FetchState:
    """Classify fetch failures as retryable vs terminal."""
    if http_status is not None and http_status in RETRYABLE_STATUS_CODES:
        return FetchState.RETRYABLE_FAILED
    if isinstance(exc, httpx.TimeoutException | httpx.NetworkError | httpx.RemoteProtocolError):
        return FetchState.RETRYABLE_FAILED
    return FetchState.TERMINAL_FAILED


def compute_backoff_seconds(attempt: int, base: float, cap: float) -> float:
    """Exponential backoff with bounded jitter."""
    exponent = max(attempt - 1, 0)
    base_delay = base * (2**exponent)
    jitter = float(JITTER_RNG.uniform(0.0, base))
    return float(min(cap, base_delay + jitter))


def should_retry(event: FetchEvent, policy: FetchPolicy) -> bool:
    """Whether a failed event should be retried by policy."""
    return event.state == FetchState.RETRYABLE_FAILED and event.attempt <= policy.max_retries


def reduce_stats(stats: FetchStats, event: FetchEvent) -> FetchStats:
    """Update aggregate counters from an event."""
    stats.processed += 1
    if event.state == FetchState.SUCCEEDED:
        stats.succeeded += 1
    elif event.state == FetchState.RETRYABLE_FAILED:
        stats.retryable_failed += 1
    elif event.state == FetchState.TERMINAL_FAILED:
        stats.terminal_failed += 1
    elif event.state == FetchState.SKIPPED_POLICY:
        stats.skipped_policy += 1

    if event.content_bytes:
        stats.bytes_fetched += event.content_bytes
    if event.elapsed_ms is not None:
        stats.latencies_ms.append(event.elapsed_ms)
    return stats


def _parse_retry_after_seconds(value: str | None) -> float | None:
    if not value:
        return None

    with contextlib.suppress(ValueError):
        seconds = int(value)
        return max(float(seconds), 0.0)

    with contextlib.suppress(ValueError, TypeError):
        when = parsedate_to_datetime(value)
        if when.tzinfo is None:
            when = when.replace(tzinfo=UTC)
        delta = (when - datetime.now(UTC)).total_seconds()
        return max(delta, 0.0)
    return None


def _is_html_content_type(content_type: str | None) -> bool:
    if content_type is None:
        return True
    lowered = content_type.lower()
    return any(token in lowered for token in HTML_CONTENT_TYPES)


def _parse_content_length(value: str | None) -> int | None:
    if value is None:
        return None
    with contextlib.suppress(ValueError):
        parsed = int(value)
        return parsed if parsed >= 0 else None
    return None


async def _read_body_limited(response: httpx.Response, max_bytes: int) -> bytes:
    chunks: list[bytes] = []
    total = 0
    async for chunk in response.aiter_bytes():
        total += len(chunk)
        if total > max_bytes:
            msg = f"response exceeded max bytes ({max_bytes})"
            raise _BodyTooLargeError(msg)
        chunks.append(chunk)
    return b"".join(chunks)


def _extract_article_sync(html: str, url: str, config: ExtractorConfig) -> ExtractResult:
    try:
        trafilatura = import_module("trafilatura")
    except ModuleNotFoundError:
        return ExtractResult(text=None, title=None, date=None, error_kind="missing_trafilatura")

    kwargs = {
        "url": url,
        "fast": config.fast,
        "include_comments": config.include_comments,
        "include_tables": config.include_tables,
        "favor_precision": config.favor_precision,
    }

    text: str | None
    try:
        text = trafilatura.extract(html, **kwargs)
    except TypeError:
        kwargs.pop("fast", None)
        try:
            text = trafilatura.extract(html, **kwargs)
        except Exception as exc:  # pragma: no cover - defensive path
            return ExtractResult(
                text=None,
                title=None,
                date=None,
                error_kind=f"extract_error:{type(exc).__name__}",
            )
    except Exception as exc:  # pragma: no cover - defensive path
        return ExtractResult(
            text=None,
            title=None,
            date=None,
            error_kind=f"extract_error:{type(exc).__name__}",
        )

    title: str | None = None
    date: str | None = None
    extract_metadata = getattr(trafilatura, "extract_metadata", None)
    if callable(extract_metadata):
        with contextlib.suppress(Exception):
            meta = extract_metadata(html)
            title = getattr(meta, "title", None) or None
            date = getattr(meta, "date", None) or None

    cleaned = text.strip() if isinstance(text, str) and text.strip() else None
    return ExtractResult(
        text=cleaned,
        title=title,
        date=date,
        error_kind=None if cleaned else "empty_extract",
    )


async def extract_article(html: str, url: str, *, config: ExtractorConfig) -> ExtractResult:
    """Run Trafilatura extraction in a worker thread."""
    return await asyncio.to_thread(_extract_article_sync, html, url, config)


@contextlib.contextmanager
def _run_lock(lock_path: Path):
    """Single-process lock for a cache path."""
    lock_path.parent.mkdir(parents=True, exist_ok=True)
    try:
        fd = os.open(lock_path, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
    except FileExistsError as exc:  # pragma: no cover - process-level behavior
        msg = f"fetch run lock already exists: {lock_path}"
        raise RuntimeError(msg) from exc

    try:
        os.write(fd, f"{os.getpid()}\n".encode())
        os.close(fd)
        yield
    finally:
        with contextlib.suppress(FileNotFoundError):
            lock_path.unlink()


def _check_disk_space(path: Path, minimum_free_bytes: int = 256 * 1024 * 1024) -> None:
    usage = shutil.disk_usage(path.parent)
    if usage.free < minimum_free_bytes:
        msg = (
            f"insufficient free disk for fetch cache at {path.parent} "
            f"(free={usage.free}, required>={minimum_free_bytes})"
        )
        raise RuntimeError(msg)


def _domain_delay_for(domain: str, policy: FetchPolicy, domain_policy: DomainPolicy) -> float:
    override = domain_policy.domain_delay_overrides.get(domain)
    if override is not None:
        return override
    return policy.domain_delay


async def _apply_domain_delay(
    domain: str,
    policy: FetchPolicy,
    domain_policy: DomainPolicy,
    domain_locks: dict[str, asyncio.Lock],
    next_allowed_by_domain: dict[str, float],
) -> None:
    lock = domain_locks.setdefault(domain, asyncio.Lock())
    async with lock:
        now = time.monotonic()
        earliest = next_allowed_by_domain.get(domain, 0.0)
        if earliest > now:
            await asyncio.sleep(earliest - now)
        delay = _domain_delay_for(domain, policy, domain_policy)
        next_allowed_by_domain[domain] = time.monotonic() + max(delay, 0.0)


def _trafilatura_version() -> str | None:
    with contextlib.suppress(Exception):
        return metadata.version("trafilatura")
    return None


def _write_checkpoint(path: Path, checkpoint: dict[str, object]) -> None:
    path.write_text(json.dumps(checkpoint, indent=2), encoding="utf-8")


def _build_event(
    *,
    run_id: str,
    url: str,
    normalized_url: str | None,
    domain: str | None,
    attempt: int,
    outcome: _AttemptOutcome,
    next_retry_at: str | None = None,
) -> FetchEvent:
    return FetchEvent(
        schema_version=1,
        run_id=run_id,
        url=url,
        normalized_url=normalized_url,
        domain=domain,
        attempt=attempt,
        state=outcome.state,
        http_status=outcome.http_status,
        error_kind=outcome.error_kind,
        error_detail=outcome.error_detail,
        content_type=outcome.content_type,
        content_bytes=outcome.content_bytes,
        elapsed_ms=outcome.elapsed_ms,
        extractor="trafilatura",
        extractor_version=_trafilatura_version(),
        title=outcome.title,
        date=outcome.date,
        text=outcome.text,
        next_retry_at=next_retry_at,
        ts=_now_iso(),
    )


async def _attempt_fetch_and_extract(
    client: httpx.AsyncClient,
    url: str,
    policy: FetchPolicy,
    extractor_config: ExtractorConfig,
    parse_sem: asyncio.Semaphore,
) -> _AttemptOutcome:
    started = time.perf_counter()
    try:
        async with client.stream("GET", url, follow_redirects=True) as response:
            status = response.status_code
            content_type = response.headers.get("content-type")
            retry_after = _parse_retry_after_seconds(response.headers.get("retry-after"))

            if status >= 400:
                state = classify_fetch_failure(status, None)
                return _AttemptOutcome(
                    state=state,
                    http_status=status,
                    error_kind=f"http_{status}",
                    error_detail=None,
                    content_type=content_type,
                    content_bytes=None,
                    elapsed_ms=_elapsed_ms(started),
                    title=None,
                    date=None,
                    text=None,
                    retry_after_seconds=retry_after,
                )

            if not _is_html_content_type(content_type):
                return _AttemptOutcome(
                    state=FetchState.TERMINAL_FAILED,
                    http_status=status,
                    error_kind="unsupported_content_type",
                    error_detail=content_type,
                    content_type=content_type,
                    content_bytes=None,
                    elapsed_ms=_elapsed_ms(started),
                    title=None,
                    date=None,
                    text=None,
                    retry_after_seconds=None,
                )

            content_length = _parse_content_length(response.headers.get("content-length"))
            if content_length is not None and content_length > policy.max_bytes:
                return _AttemptOutcome(
                    state=FetchState.TERMINAL_FAILED,
                    http_status=status,
                    error_kind="oversize_content_length",
                    error_detail=f"{content_length}>{policy.max_bytes}",
                    content_type=content_type,
                    content_bytes=content_length,
                    elapsed_ms=_elapsed_ms(started),
                    title=None,
                    date=None,
                    text=None,
                    retry_after_seconds=None,
                )

            body = await _read_body_limited(response, policy.max_bytes)
    except asyncio.CancelledError:
        raise
    except _BodyTooLargeError:
        return _AttemptOutcome(
            state=FetchState.TERMINAL_FAILED,
            http_status=None,
            error_kind="oversize_body",
            error_detail=f"max_bytes={policy.max_bytes}",
            content_type=None,
            content_bytes=policy.max_bytes + 1,
            elapsed_ms=_elapsed_ms(started),
            title=None,
            date=None,
            text=None,
            retry_after_seconds=None,
        )
    except Exception as exc:
        state = classify_fetch_failure(None, exc)
        return _AttemptOutcome(
            state=state,
            http_status=None,
            error_kind=type(exc).__name__,
            error_detail=str(exc),
            content_type=None,
            content_bytes=None,
            elapsed_ms=_elapsed_ms(started),
            title=None,
            date=None,
            text=None,
            retry_after_seconds=None,
        )

    encoding = response.encoding or "utf-8"
    html = body.decode(encoding, errors="replace")
    async with parse_sem:
        extract = await extract_article(html, url, config=extractor_config)

    if extract.text:
        state = FetchState.SUCCEEDED
        error_kind = None
    else:
        state = FetchState.TERMINAL_FAILED
        error_kind = extract.error_kind or "empty_extract"

    return _AttemptOutcome(
        state=state,
        http_status=response.status_code,
        error_kind=error_kind,
        error_detail=None,
        content_type=response.headers.get("content-type"),
        content_bytes=len(body),
        elapsed_ms=_elapsed_ms(started),
        title=extract.title,
        date=extract.date,
        text=extract.text,
        retry_after_seconds=None,
    )


def _elapsed_ms(started: float) -> int:
    return int((time.perf_counter() - started) * 1000)


async def _process_url(
    *,
    url: str,
    run_id: str,
    resume_entry: ResumeEntry | None,
    client: httpx.AsyncClient,
    policy: FetchPolicy,
    domain_policy: DomainPolicy,
    extractor_config: ExtractorConfig,
    parse_sem: asyncio.Semaphore,
    domain_locks: dict[str, asyncio.Lock],
    next_allowed_by_domain: dict[str, float],
    domain_failure_counts: dict[str, int],
) -> list[FetchEvent]:
    normalized = normalize_url(url)
    domain = normalize_host(normalized or url)

    if normalized is None:
        outcome = _AttemptOutcome(
            state=FetchState.TERMINAL_FAILED,
            http_status=None,
            error_kind="invalid_url",
            error_detail=url,
            content_type=None,
            content_bytes=None,
            elapsed_ms=0,
            title=None,
            date=None,
            text=None,
            retry_after_seconds=None,
        )
        return [
            _build_event(
                run_id=run_id,
                url=url,
                normalized_url=None,
                domain=domain,
                attempt=1,
                outcome=outcome,
            )
        ]

    if domain is None:
        outcome = _AttemptOutcome(
            state=FetchState.TERMINAL_FAILED,
            http_status=None,
            error_kind="missing_domain",
            error_detail=normalized,
            content_type=None,
            content_bytes=None,
            elapsed_ms=0,
            title=None,
            date=None,
            text=None,
            retry_after_seconds=None,
        )
        return [
            _build_event(
                run_id=run_id,
                url=url,
                normalized_url=normalized,
                domain=None,
                attempt=1,
                outcome=outcome,
            )
        ]

    if _is_private_target(domain):
        outcome = _AttemptOutcome(
            state=FetchState.TERMINAL_FAILED,
            http_status=None,
            error_kind="ssrf_blocked",
            error_detail=domain,
            content_type=None,
            content_bytes=None,
            elapsed_ms=0,
            title=None,
            date=None,
            text=None,
            retry_after_seconds=None,
        )
        return [
            _build_event(
                run_id=run_id,
                url=url,
                normalized_url=normalized,
                domain=domain,
                attempt=1,
                outcome=outcome,
            )
        ]

    decision = classify_domain(domain, domain_policy)
    if not decision.allowed:
        outcome = _AttemptOutcome(
            state=FetchState.SKIPPED_POLICY,
            http_status=None,
            error_kind="domain_policy",
            error_detail=decision.reason,
            content_type=None,
            content_bytes=None,
            elapsed_ms=0,
            title=None,
            date=None,
            text=None,
            retry_after_seconds=None,
        )
        return [
            _build_event(
                run_id=run_id,
                url=url,
                normalized_url=normalized,
                domain=domain,
                attempt=1,
                outcome=outcome,
            )
        ]

    if domain_failure_counts.get(domain, 0) >= policy.circuit_breaker_threshold:
        outcome = _AttemptOutcome(
            state=FetchState.SKIPPED_POLICY,
            http_status=None,
            error_kind="circuit_open",
            error_detail=f"failures={domain_failure_counts.get(domain, 0)}",
            content_type=None,
            content_bytes=None,
            elapsed_ms=0,
            title=None,
            date=None,
            text=None,
            retry_after_seconds=None,
        )
        return [
            _build_event(
                run_id=run_id,
                url=url,
                normalized_url=normalized,
                domain=domain,
                attempt=1,
                outcome=outcome,
            )
        ]

    events: list[FetchEvent] = []
    attempt = 1
    if resume_entry is not None and resume_entry.state == FetchState.RETRYABLE_FAILED:
        attempt = max(resume_entry.attempt + 1, 1)

    final_attempt = attempt + policy.max_retries
    while attempt <= final_attempt:
        await _apply_domain_delay(
            domain=domain,
            policy=policy,
            domain_policy=domain_policy,
            domain_locks=domain_locks,
            next_allowed_by_domain=next_allowed_by_domain,
        )

        outcome = await _attempt_fetch_and_extract(
            client=client,
            url=normalized,
            policy=policy,
            extractor_config=extractor_config,
            parse_sem=parse_sem,
        )

        next_retry_at: str | None = None
        retry_delay: float | None = None
        if outcome.state == FetchState.RETRYABLE_FAILED and attempt < final_attempt:
            retry_delay = outcome.retry_after_seconds
            if retry_delay is None:
                retry_delay = compute_backoff_seconds(
                    attempt=attempt,
                    base=policy.backoff_base,
                    cap=policy.max_backoff,
                )
            retry_delay = min(retry_delay, policy.max_backoff)
            next_retry_at = _future_iso(retry_delay)

        event = _build_event(
            run_id=run_id,
            url=url,
            normalized_url=normalized,
            domain=domain,
            attempt=attempt,
            outcome=outcome,
            next_retry_at=next_retry_at,
        )
        events.append(event)

        if outcome.state == FetchState.SUCCEEDED:
            domain_failure_counts[domain] = 0
            break

        if outcome.state == FetchState.RETRYABLE_FAILED and attempt < final_attempt:
            domain_failure_counts[domain] = domain_failure_counts.get(domain, 0) + 1
            wait_seconds = retry_delay
            if wait_seconds is None:
                wait_seconds = compute_backoff_seconds(
                    attempt=attempt,
                    base=policy.backoff_base,
                    cap=policy.max_backoff,
                )
            wait_seconds = min(wait_seconds, policy.max_backoff)
            await asyncio.sleep(wait_seconds)
            attempt += 1
            continue

        if outcome.state != FetchState.SUCCEEDED:
            domain_failure_counts[domain] = domain_failure_counts.get(domain, 0) + 1
        break

    return events


async def _worker_task(
    *,
    run_id: str,
    url_queue: asyncio.Queue[str | None],
    result_queue: asyncio.Queue[FetchEvent | None],
    resume_index: ResumeIndex,
    client: httpx.AsyncClient,
    policy: FetchPolicy,
    domain_policy: DomainPolicy,
    extractor_config: ExtractorConfig,
    parse_sem: asyncio.Semaphore,
    domain_locks: dict[str, asyncio.Lock],
    next_allowed_by_domain: dict[str, float],
    domain_failure_counts: dict[str, int],
) -> None:
    while True:
        raw_url = await url_queue.get()
        if raw_url is None:
            url_queue.task_done()
            break

        normalized = normalize_url(raw_url)
        resume_entry = resume_index.latest_by_url.get(normalized) if normalized else None
        events = await _process_url(
            url=raw_url,
            run_id=run_id,
            resume_entry=resume_entry,
            client=client,
            policy=policy,
            domain_policy=domain_policy,
            extractor_config=extractor_config,
            parse_sem=parse_sem,
            domain_locks=domain_locks,
            next_allowed_by_domain=next_allowed_by_domain,
            domain_failure_counts=domain_failure_counts,
        )
        for event in events:
            await result_queue.put(event)
        url_queue.task_done()


async def _writer_task(
    *,
    run_id: str,
    result_queue: asyncio.Queue[FetchEvent | None],
    cache_path: Path,
    checkpoint_path: Path,
    fail_fast_threshold: float | None,
    progress_every: int,
) -> FetchStats:
    stats = FetchStats()
    cache_path.parent.mkdir(parents=True, exist_ok=True)
    checkpoint_path.parent.mkdir(parents=True, exist_ok=True)

    with cache_path.open("a", encoding="utf-8") as handle:
        while True:
            event = await result_queue.get()
            if event is None:
                result_queue.task_done()
                break

            handle.write(json.dumps(event.to_json(), ensure_ascii=False))
            handle.write("\n")
            handle.flush()
            reduce_stats(stats, event)

            if progress_every > 0 and stats.processed % progress_every == 0:
                print(
                    "  Progress: "
                    f"processed={stats.processed} "
                    f"ok={stats.succeeded} "
                    f"retryable={stats.retryable_failed} "
                    f"terminal={stats.terminal_failed} "
                    f"skipped={stats.skipped_policy}"
                )

            if stats.processed % CHECKPOINT_EVERY == 0:
                checkpoint = stats.as_checkpoint(run_id)
                await asyncio.to_thread(_write_checkpoint, checkpoint_path, checkpoint)

            if (
                fail_fast_threshold is not None
                and fail_fast_threshold < 1.0
                and stats.processed >= 50
            ):
                failure_ratio = (stats.retryable_failed + stats.terminal_failed) / stats.processed
                if failure_ratio >= fail_fast_threshold:
                    result_queue.task_done()
                    msg = (
                        "aborting fetch due to failure ratio threshold "
                        f"({failure_ratio:.3f} >= {fail_fast_threshold:.3f})"
                    )
                    raise RuntimeError(msg)

            result_queue.task_done()

    checkpoint = stats.as_checkpoint(run_id)
    await asyncio.to_thread(_write_checkpoint, checkpoint_path, checkpoint)
    return stats


def _checkpoint_path(cache_path: Path) -> Path:
    return cache_path.with_suffix(f"{cache_path.suffix}.checkpoint.json")


def _lock_path(cache_path: Path) -> Path:
    return cache_path.with_suffix(f"{cache_path.suffix}.lock")


def _should_skip_resume(
    normalized_url: str,
    *,
    resume: bool,
    resume_index: ResumeIndex,
) -> bool:
    if not resume:
        return False
    entry = resume_index.latest_by_url.get(normalized_url)
    if entry is None:
        return False
    return is_terminal_state(entry.state)


async def run_fetch_pipeline(
    urls: list[str],
    cache_path: Path,
    *,
    concurrency: int,
    domain_delay: float,
    request_timeout: float,
    max_retries: int,
    max_bytes: int,
    queue_size: int,
    user_agent: str,
    resume: bool,
    domain_policy: DomainPolicy | None = None,
    fail_fast_threshold: float | None = None,
    progress_every: int = 50,
) -> FetchStats:
    """Run structured async fetch pipeline and persist NDJSON events."""
    _check_disk_space(cache_path)

    run_id = _now_iso()
    effective_domain_policy = domain_policy or DomainPolicy()
    resume_index = load_resume_index(cache_path) if resume else ResumeIndex({}, malformed_lines=0)

    policy = FetchPolicy(
        concurrency=max(concurrency, 1),
        domain_delay=max(domain_delay, 0.0),
        request_timeout=max(request_timeout, 0.1),
        max_retries=max(max_retries, 0),
        max_bytes=max(max_bytes, 1024),
        queue_size=max(queue_size, 1),
        user_agent=user_agent,
        progress_every=max(progress_every, 0),
    )
    extractor_config = ExtractorConfig()

    seen_inputs: set[str] = set()
    pending_urls: list[str] = []
    skipped_resume = 0

    for raw_url in urls:
        normalized = normalize_url(raw_url)
        if normalized is None:
            pending_urls.append(raw_url)
            continue
        if normalized in seen_inputs:
            continue
        seen_inputs.add(normalized)
        if _should_skip_resume(normalized, resume=resume, resume_index=resume_index):
            skipped_resume += 1
            continue
        pending_urls.append(normalized)

    timeout = httpx.Timeout(
        connect=policy.request_timeout,
        read=policy.request_timeout,
        write=policy.request_timeout,
        pool=policy.request_timeout,
    )
    limits = httpx.Limits(
        max_connections=policy.concurrency,
        max_keepalive_connections=policy.concurrency,
    )
    headers = {
        "User-Agent": policy.user_agent,
        "Accept": "text/html,application/xhtml+xml;q=0.9,*/*;q=0.1",
    }

    url_queue: asyncio.Queue[str | None] = asyncio.Queue(maxsize=policy.queue_size)
    result_queue: asyncio.Queue[FetchEvent | None] = asyncio.Queue(maxsize=policy.queue_size)
    domain_locks: dict[str, asyncio.Lock] = {}
    next_allowed_by_domain: dict[str, float] = {}
    domain_failure_counts: dict[str, int] = {}
    parse_sem = asyncio.Semaphore(max(1, policy.concurrency // 2))

    checkpoint_path = _checkpoint_path(cache_path)
    lock_path = _lock_path(cache_path)

    stats: FetchStats
    with _run_lock(lock_path):
        async with httpx.AsyncClient(
            timeout=timeout,
            limits=limits,
            headers=headers,
            trust_env=False,
            max_redirects=policy.max_redirects,
        ) as client:
            writer_handle: asyncio.Task[FetchStats] | None = None
            async with asyncio.TaskGroup() as tg:
                writer_handle = tg.create_task(
                    _writer_task(
                        run_id=run_id,
                        result_queue=result_queue,
                        cache_path=cache_path,
                        checkpoint_path=checkpoint_path,
                        fail_fast_threshold=fail_fast_threshold,
                        progress_every=policy.progress_every,
                    )
                )
                for _ in range(policy.concurrency):
                    tg.create_task(
                        _worker_task(
                            run_id=run_id,
                            url_queue=url_queue,
                            result_queue=result_queue,
                            resume_index=resume_index,
                            client=client,
                            policy=policy,
                            domain_policy=effective_domain_policy,
                            extractor_config=extractor_config,
                            parse_sem=parse_sem,
                            domain_locks=domain_locks,
                            next_allowed_by_domain=next_allowed_by_domain,
                            domain_failure_counts=domain_failure_counts,
                        )
                    )

                for url in pending_urls:
                    await url_queue.put(url)
                for _ in range(policy.concurrency):
                    await url_queue.put(None)

                await url_queue.join()
                await result_queue.put(None)
                await result_queue.join()

            if writer_handle is None:
                msg = "writer task was not created"
                raise RuntimeError(msg)
            stats = writer_handle.result()

    stats.skipped_terminal_resume = skipped_resume
    stats.malformed_resume_lines = resume_index.malformed_lines
    return stats
