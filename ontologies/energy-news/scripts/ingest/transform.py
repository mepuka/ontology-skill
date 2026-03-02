"""Stage 2: Transform SkyGent JSON posts into RDF triples."""

from __future__ import annotations

import hashlib
from dataclasses import dataclass, field
from typing import Any

from rdflib import Graph, Literal, URIRef
from rdflib.namespace import RDF, RDFS, XSD

from .namespaces import DATA, ENEWS, bind_abox_prefixes
from .publications import PublicationIndex, resolve_publication
from .topics import TopicLookup, match_topics


@dataclass
class TransformStats:
    """Counters for the transform stage."""

    posts: int = 0
    authors: int = 0
    embeds_external: int = 0
    embeds_images: int = 0
    embeds_video: int = 0
    embeds_record: int = 0
    embeds_record_with_media: int = 0
    embeds_none: int = 0
    articles: int = 0
    media_attachments: int = 0
    publications_minted: int = 0
    topics_matched: int = 0
    skipped: int = 0
    embed_types: dict[str, int] = field(default_factory=dict)


def _extract_rkey(at_uri: str) -> str:
    """Extract the record key from an AT-URI.

    E.g. 'at://did:plc:xxx/app.bsky.feed.post/3lbphn3qxk22l' -> '3lbphn3qxk22l'
    """
    return at_uri.rsplit("/", 1)[-1]


def _hash_url(url: str) -> str:
    """Create a short hash of a URL for Article IRI minting."""
    return hashlib.sha256(url.encode()).hexdigest()[:12]


def _slugify_handle(handle: str) -> str:
    """Convert a Bluesky handle to a safe IRI slug.

    E.g. 'reuters.com' -> 'reuters_com'
    """
    slug = handle.replace(".", "_").replace("-", "_").replace("@", "")
    return slug.rstrip("_")


def transform_posts(
    posts: list[dict[str, Any]],
    pub_index: PublicationIndex,
    topic_lookup: TopicLookup,
    shortener_cache: dict[str, str] | None = None,
) -> tuple[Graph, TransformStats]:
    """Transform a list of SkyGent posts into an RDF graph.

    Args:
        posts: List of post dicts from SkyGent --full output.
        pub_index: Publication index for domain→Publication resolution.
        topic_lookup: Topic lookup for hashtag/keyword matching.
        shortener_cache: Cache of shortened URL → resolved URL mappings.

    Returns:
        Tuple of (ABox Graph, TransformStats).
    """
    g = Graph()
    bind_abox_prefixes(g)
    stats = TransformStats()
    seen_authors: dict[str, URIRef] = {}

    for post in posts:
        _transform_one_post(g, post, pub_index, topic_lookup, shortener_cache, stats, seen_authors)

    stats.authors = len(seen_authors)
    return g, stats


def _transform_one_post(
    g: Graph,
    post: dict[str, Any],
    pub_index: PublicationIndex,
    topic_lookup: TopicLookup,
    shortener_cache: dict[str, str] | None,
    stats: TransformStats,
    seen_authors: dict[str, URIRef],
) -> None:
    """Transform a single post dict into RDF triples."""
    at_uri = post.get("uri", "")
    if not at_uri:
        stats.skipped += 1
        return

    rkey = _extract_rkey(at_uri)
    post_uri = DATA[f"post/{rkey}"]

    # --- Post ---
    g.add((post_uri, RDF.type, ENEWS.Post))
    text = post.get("text", "")
    if text:
        g.add((post_uri, ENEWS.postText, Literal(text)))

    created_at = post.get("createdAt")
    if created_at:
        g.add((post_uri, ENEWS.createdAt, Literal(created_at, datatype=XSD.dateTime)))

    # --- Author ---
    author_handle = post.get("author", "")
    if author_handle:
        author_uri = _get_or_create_author(g, author_handle, post, seen_authors)
        g.add((post_uri, ENEWS.postedBy, author_uri))

    # --- Metrics ---
    metrics = post.get("metrics", {})
    if metrics:
        _add_metrics(g, post_uri, metrics)

    # --- Reply chain ---
    _add_reply_chain(g, post_uri, post)

    # --- Embed dispatch ---
    _dispatch_embed(g, post_uri, rkey, post, pub_index, topic_lookup, shortener_cache, stats)

    stats.posts += 1


def _add_reply_chain(g: Graph, post_uri: URIRef, post: dict[str, Any]) -> None:
    """Add isReplyTo link if the post is a reply."""
    reply = post.get("reply")
    if not reply:
        return
    parent = reply.get("parent", {})
    parent_uri_str = parent.get("uri", "")
    if parent_uri_str:
        parent_rkey = _extract_rkey(parent_uri_str)
        g.add((post_uri, ENEWS.isReplyTo, DATA[f"post/{parent_rkey}"]))


def _dispatch_embed(
    g: Graph,
    post_uri: URIRef,
    rkey: str,
    post: dict[str, Any],
    pub_index: PublicationIndex,
    topic_lookup: TopicLookup,
    shortener_cache: dict[str, str] | None,
    stats: TransformStats,
) -> None:
    """Dispatch embed handling based on _tag type."""
    embed = post.get("embed")
    if not embed:
        stats.embeds_none += 1
        return

    tag = embed.get("_tag", "")
    stats.embed_types[tag] = stats.embed_types.get(tag, 0) + 1

    if tag == "External":
        _handle_external_embed(
            g, post_uri, rkey, embed, pub_index, topic_lookup, shortener_cache, stats, post
        )
    elif tag == "Images":
        _handle_images_embed(g, post_uri, rkey, embed, stats, post.get("recordEmbed"))
    elif tag == "Video":
        _handle_video_embed(g, post_uri, rkey, embed, stats, post.get("recordEmbed"))
    elif tag == "Record":
        _handle_record_embed(g, post_uri, embed, stats)
    elif tag == "RecordWithMedia":
        _handle_record_with_media_embed(g, post_uri, rkey, embed, stats)
    else:
        stats.embeds_none += 1


def _get_or_create_author(
    g: Graph,
    handle: str,
    post: dict[str, Any],
    seen_authors: dict[str, URIRef],
) -> URIRef:
    """Get or create an AuthorAccount individual."""
    if handle in seen_authors:
        return seen_authors[handle]

    slug = _slugify_handle(handle)
    author_uri = DATA[f"author/{slug}"]
    g.add((author_uri, RDF.type, ENEWS.AuthorAccount))
    g.add((author_uri, ENEWS.handle, Literal(handle)))
    g.add((author_uri, ENEWS.onPlatform, ENEWS.Bluesky))
    g.add((author_uri, RDFS.label, Literal(handle, lang="en")))

    # Display name from author profile
    profile = post.get("authorProfile", {})
    display_name = profile.get("displayName", "")
    if display_name:
        g.add((author_uri, ENEWS.displayName, Literal(display_name)))

    seen_authors[handle] = author_uri
    return author_uri


def _add_metrics(g: Graph, post_uri: URIRef, metrics: dict[str, Any]) -> None:
    """Add engagement metrics to a Post."""
    like_count = metrics.get("likeCount")
    if like_count is not None:
        g.add((post_uri, ENEWS.likeCount, Literal(like_count, datatype=XSD.nonNegativeInteger)))

    reply_count = metrics.get("replyCount")
    if reply_count is not None:
        g.add((post_uri, ENEWS.replyCount, Literal(reply_count, datatype=XSD.nonNegativeInteger)))

    repost_count = metrics.get("repostCount")
    if repost_count is not None:
        g.add((post_uri, ENEWS.repostCount, Literal(repost_count, datatype=XSD.nonNegativeInteger)))


def _handle_external_embed(
    g: Graph,
    post_uri: URIRef,
    rkey: str,
    embed: dict[str, Any],
    pub_index: PublicationIndex,
    topic_lookup: TopicLookup,
    shortener_cache: dict[str, str] | None,
    stats: TransformStats,
    post: dict[str, Any],
) -> None:
    """Handle an External embed — create EmbeddedExternalLink + Article + Publication."""
    link_uri_str = embed.get("uri", "")
    if not link_uri_str:
        return

    # --- EmbeddedExternalLink ---
    embed_uri = DATA[f"embed/{rkey}"]
    g.add((embed_uri, RDF.type, ENEWS.EmbeddedExternalLink))
    g.add((embed_uri, ENEWS.linkUri, Literal(link_uri_str, datatype=XSD.anyURI)))
    g.add((post_uri, ENEWS.hasEmbed, embed_uri))

    title = embed.get("title", "")
    if title:
        g.add((embed_uri, ENEWS.linkTitle, Literal(title)))

    description = embed.get("description", "")
    if description:
        g.add((embed_uri, ENEWS.linkDescription, Literal(description)))

    thumb = embed.get("thumb", "")
    if thumb:
        g.add((embed_uri, ENEWS.thumbnailUri, Literal(thumb, datatype=XSD.anyURI)))

    stats.embeds_external += 1

    # --- Article stub ---
    # Resolve effective URL through shortener cache (covers generic + brand shorteners)
    effective_url = link_uri_str
    if shortener_cache and link_uri_str in shortener_cache:
        effective_url = shortener_cache[link_uri_str]

    url_hash = _hash_url(effective_url)
    article_uri = DATA[f"article/{url_hash}"]
    g.add((article_uri, RDF.type, ENEWS.Article))
    g.add((article_uri, ENEWS.url, Literal(effective_url, datatype=XSD.anyURI)))

    # Only set title/description if not already present (multiple posts may share an article)
    if title and not g.value(article_uri, ENEWS.title):
        g.add((article_uri, ENEWS.title, Literal(title)))
    if description and not g.value(article_uri, ENEWS.description):
        g.add((article_uri, ENEWS.description, Literal(description)))

    g.add((post_uri, ENEWS.sharesArticle, article_uri))
    stats.articles += 1

    # --- Publication ---
    pub_uri = resolve_publication(link_uri_str, pub_index, g, shortener_cache)
    if pub_uri:
        g.add((article_uri, ENEWS.publishedBy, pub_uri))

    # --- Topic matching ---
    hashtags = post.get("hashtags", [])
    combined_text = f"{title} {description} {post.get('text', '')}"
    matched_topics = match_topics(combined_text, hashtags, topic_lookup)
    for topic_uri in matched_topics:
        g.add((article_uri, ENEWS.coversTopic, topic_uri))
        stats.topics_matched += 1


def _handle_images_embed(
    g: Graph,
    post_uri: URIRef,
    rkey: str,
    embed: dict[str, Any],
    stats: TransformStats,
    record_embed: dict[str, Any] | None = None,
) -> None:
    """Handle an Images embed — create MediaAttachment per image."""
    images = embed.get("images", [])

    for i, image in enumerate(images):
        media_uri = DATA[f"media/{rkey}_{i + 1}"]
        g.add((media_uri, RDF.type, ENEWS.MediaAttachment))
        g.add((post_uri, ENEWS.hasMedia, media_uri))

        # Full-size URL from the --full output
        fullsize = image.get("fullsize", "")
        if fullsize:
            g.add((media_uri, ENEWS.mediaUri, Literal(fullsize, datatype=XSD.anyURI)))

        # Alt text
        alt = image.get("alt", "")
        if alt:
            g.add((media_uri, ENEWS.altText, Literal(alt)))

        # MIME type from recordEmbed if available
        if record_embed:
            re_images = record_embed.get("images", [])
            if i < len(re_images):
                image_blob = re_images[i].get("image", {})
                mime_type = image_blob.get("mimeType", "")
                if mime_type:
                    g.add((media_uri, ENEWS.mimeType, Literal(mime_type)))

        stats.media_attachments += 1

    stats.embeds_images += 1


def _handle_video_embed(
    g: Graph,
    post_uri: URIRef,
    rkey: str,
    embed: dict[str, Any],
    stats: TransformStats,
    record_embed: dict[str, Any] | None = None,
) -> None:
    """Handle a Video embed — create MediaAttachment with video metadata."""
    media_uri = DATA[f"media/{rkey}_video"]
    g.add((media_uri, RDF.type, ENEWS.MediaAttachment))
    g.add((post_uri, ENEWS.hasMedia, media_uri))

    # Video embeds may have playlist/thumbnail — use one (maxCount 1)
    playlist = embed.get("playlist", "")
    thumbnail = embed.get("thumbnail", "")
    video_url = playlist or thumbnail
    if video_url:
        g.add((media_uri, ENEWS.mediaUri, Literal(video_url, datatype=XSD.anyURI)))

    # MIME type hint
    if record_embed:
        video = record_embed.get("video", {})
        mime_type = video.get("mimeType", "")
        if mime_type:
            g.add((media_uri, ENEWS.mimeType, Literal(mime_type)))

    g.add((media_uri, ENEWS.mimeType, Literal("video/mp4")))
    stats.media_attachments += 1
    stats.embeds_video += 1


def _handle_record_embed(
    g: Graph,
    post_uri: URIRef,
    embed: dict[str, Any],
    stats: TransformStats,
) -> None:
    """Handle a Record embed (quote post) — create isReplyTo link."""
    record = embed.get("record", {})
    quoted_uri = record.get("uri", "")
    if quoted_uri:
        quoted_rkey = _extract_rkey(quoted_uri)
        g.add((post_uri, ENEWS.isReplyTo, DATA[f"post/{quoted_rkey}"]))
    stats.embeds_record += 1


def _handle_record_with_media_embed(
    g: Graph,
    post_uri: URIRef,
    rkey: str,
    embed: dict[str, Any],
    stats: TransformStats,
) -> None:
    """Handle a RecordWithMedia embed — isReplyTo + MediaAttachments."""
    # Record part
    record = embed.get("record", {})
    quoted_uri = record.get("uri", "")
    if quoted_uri:
        quoted_rkey = _extract_rkey(quoted_uri)
        g.add((post_uri, ENEWS.isReplyTo, DATA[f"post/{quoted_rkey}"]))

    # Media part — check for images in the embed
    media = embed.get("media", {})
    images = media.get("images", [])
    for i, image in enumerate(images):
        media_uri = DATA[f"media/{rkey}_{i + 1}"]
        g.add((media_uri, RDF.type, ENEWS.MediaAttachment))
        g.add((post_uri, ENEWS.hasMedia, media_uri))

        fullsize = image.get("fullsize", "")
        if fullsize:
            g.add((media_uri, ENEWS.mediaUri, Literal(fullsize, datatype=XSD.anyURI)))

        alt = image.get("alt", "")
        if alt:
            g.add((media_uri, ENEWS.altText, Literal(alt)))

        stats.media_attachments += 1

    stats.embeds_record_with_media += 1
