"""URL shortener resolution — brand map + async generic resolution + cache."""

from __future__ import annotations

import asyncio
import json
import sys
from typing import TYPE_CHECKING, Any
from urllib.parse import urlparse

if TYPE_CHECKING:
    from pathlib import Path

import httpx

# ---------------------------------------------------------------------------
# Brand shorteners — static domain→domain map (no HTTP needed)
# ---------------------------------------------------------------------------

BRAND_SHORTENERS: dict[str, str] = {
    "reut.rs": "reuters.com",
    "nyti.ms": "nytimes.com",
    "wapo.st": "washingtonpost.com",
    "cnb.cx": "cnbc.com",
    "wrd.cm": "wired.com",
    "on.ft.com": "ft.com",
    "econ.st": "economist.com",
    "bloom.bg": "bloomberg.com",
    "politi.co": "politico.com",
    "cnn.it": "cnn.com",
    "apnews.com": "apnews.com",
    "bbc.in": "bbc.co.uk",
    "fxn.ws": "foxnews.com",
    "hill.cm": "thehill.com",
    "trib.al": "trib.al",  # This one is generic, handled below
}

# ---------------------------------------------------------------------------
# Generic shortener domains — require HTTP HEAD to resolve
# ---------------------------------------------------------------------------

GENERIC_SHORTENER_DOMAINS: set[str] = {
    "bit.ly",
    "buff.ly",
    "dlvr.it",
    "ow.ly",
    "trib.al",
    "t.co",
    "is.gd",
    "tinyurl.com",
    "goo.gl",
    "rb.gy",
    "shorturl.at",
    "lnkd.in",
}


def extract_domain(url: str) -> str | None:
    """Extract domain from URL, stripping www. prefix."""
    try:
        parsed = urlparse(url)
    except Exception:
        return None
    else:
        domain = parsed.netloc
        if domain.startswith("www."):
            domain = domain[4:]
        return domain if domain else None


def is_brand_shortener(url: str) -> str | None:
    """Check if URL domain is a brand shortener. Returns resolved domain or None."""
    domain = extract_domain(url)
    if not domain:
        return None
    # Check full domain (e.g., on.ft.com)
    if domain in BRAND_SHORTENERS:
        resolved = BRAND_SHORTENERS[domain]
        # trib.al is in both maps; treat as generic
        if resolved != domain:
            return resolved
    return None


def is_generic_shortener(url: str) -> bool:
    """Check if URL uses a generic shortener domain requiring HTTP resolution."""
    domain = extract_domain(url)
    return domain in GENERIC_SHORTENER_DOMAINS if domain else False


# ---------------------------------------------------------------------------
# Cache I/O
# ---------------------------------------------------------------------------


def load_cache(path: Path) -> dict[str, str]:
    """Load the shortener resolution cache from JSON file."""
    if path.exists():
        with path.open(encoding="utf-8") as f:
            data: dict[str, str] = json.load(f)
            return data
    return {}


def save_cache(cache: dict[str, str], path: Path) -> None:
    """Save the shortener resolution cache to JSON file."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(cache, f, indent=2, sort_keys=True)


# ---------------------------------------------------------------------------
# Async generic shortener resolution
# ---------------------------------------------------------------------------


async def _resolve_one(
    client: httpx.AsyncClient,
    url: str,
    semaphore: asyncio.Semaphore,
) -> tuple[str, str | None]:
    """Resolve a single shortened URL via HTTP HEAD, following redirects."""
    async with semaphore:
        try:
            resp = await client.head(url, follow_redirects=True, timeout=10.0)
        except Exception as exc:
            print(f"  Failed to resolve {url}: {exc}", file=sys.stderr)
            return url, None
        else:
            return url, str(resp.url)


async def _resolve_batch(
    urls: list[str],
    concurrency: int = 20,
) -> dict[str, str]:
    """Resolve a batch of shortened URLs concurrently."""
    semaphore = asyncio.Semaphore(concurrency)
    results: dict[str, str] = {}

    async with httpx.AsyncClient() as client:
        tasks = [_resolve_one(client, url, semaphore) for url in urls]
        for coro in asyncio.as_completed(tasks):
            url, resolved = await coro
            if resolved:
                results[url] = resolved

    return results


def _find_chain_urls(cache: dict[str, str]) -> list[str]:
    """Find cached entries where the resolved URL is still a shortener domain.

    Returns:
        List of resolved URLs that need a second pass of resolution.
    """
    chain_urls: list[str] = []
    for resolved in cache.values():
        domain = extract_domain(resolved)
        if domain and domain in GENERIC_SHORTENER_DOMAINS:
            chain_urls.append(resolved)
    return sorted(set(chain_urls))


def resolve_generic_shorteners(
    urls: list[str],
    cache: dict[str, str],
    *,
    concurrency: int = 20,
    max_chain_depth: int = 3,
) -> dict[str, str]:
    """Resolve generic shortener URLs, using cache for already-resolved ones.

    Follows shortener chains — if a shortened URL resolves to another
    shortener (e.g. bit.ly → buff.ly → final), iterates up to
    max_chain_depth times to reach the final destination.

    Args:
        urls: List of shortened URLs to resolve.
        cache: Existing cache of url→resolved_url mappings.
        concurrency: Max concurrent HTTP requests.
        max_chain_depth: Maximum number of chain resolution passes.

    Returns:
        Updated cache with all resolved URLs.
    """
    to_resolve = [u for u in urls if u not in cache]

    if to_resolve:
        print(f"  Resolving {len(to_resolve)} shortener URLs (concurrency={concurrency})...")
        new_results = asyncio.run(_resolve_batch(to_resolve, concurrency))
        cache.update(new_results)
        print(f"  Resolved {len(new_results)}/{len(to_resolve)} URLs")
    else:
        print("  All shortener URLs already cached.")

    # Follow shortener chains — resolved URLs that are themselves shorteners
    for depth in range(max_chain_depth):
        chain_urls = _find_chain_urls(cache)
        if not chain_urls:
            break

        # Filter to only URLs not already in cache
        to_resolve_chain = [u for u in chain_urls if u not in cache]
        if not to_resolve_chain:
            # All chain URLs are already cached — apply transitive resolution
            _apply_chain_resolution(cache)
            chain_remaining = _find_chain_urls(cache)
            if not chain_remaining:
                break
            print(f"  Chain pass {depth + 2}: {len(chain_remaining)} still unresolved")
            continue

        print(
            f"  Chain pass {depth + 2}: resolving {len(to_resolve_chain)} "
            f"shortener-to-shortener URLs..."
        )
        chain_results = asyncio.run(_resolve_batch(to_resolve_chain, concurrency))
        cache.update(chain_results)
        print(f"  Resolved {len(chain_results)}/{len(to_resolve_chain)} chain URLs")

        # Apply transitive resolution to update original→final mappings
        _apply_chain_resolution(cache)

    return cache


def _apply_chain_resolution(cache: dict[str, str]) -> None:
    """Update cache entries so originals point to final destinations.

    If cache has A→B and B→C, updates A→C.
    """
    updated = 0
    for original in list(cache):
        resolved = cache[original]
        # Follow chain through cache
        seen: set[str] = {original, resolved}
        while resolved in cache and cache[resolved] not in seen:
            resolved = cache[resolved]
            seen.add(resolved)
        if resolved != cache[original]:
            cache[original] = resolved
            updated += 1
    if updated:
        print(f"  Updated {updated} cache entries via chain resolution")


def collect_shortener_urls(posts: list[dict[str, Any]]) -> list[str]:
    """Collect all shortener URLs (generic + brand) from post embeds.

    Both generic shorteners (bit.ly, buff.ly) and brand shorteners (reut.rs,
    bloom.bg) are collected so that HTTP resolution can determine the final
    canonical URL for each.

    Args:
        posts: List of post dicts from SkyGent.

    Returns:
        Deduplicated list of shortener URLs needing resolution.
    """
    urls: set[str] = set()
    for post in posts:
        embed = post.get("embed")
        if not embed:
            continue
        tag = embed.get("_tag")
        if tag == "External":
            uri = embed.get("uri", "")
            if is_generic_shortener(uri) or is_brand_shortener(uri):
                urls.add(uri)
    return sorted(urls)
