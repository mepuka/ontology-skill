"""Unit tests for the Energy News ABox ETL pipeline."""

from __future__ import annotations

from pathlib import Path

import pytest
from rdflib import Graph, Literal, Namespace
from rdflib.namespace import RDF, XSD

ENEWS = Namespace("http://example.org/ontology/energy-news#")
DATA = Namespace("http://example.org/data/")

PROJECT = Path(__file__).resolve().parent.parent
REF_PATH = PROJECT / "energy-news-reference-individuals.ttl"


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture(scope="module")
def ref_graph() -> Graph:
    """Load the reference individuals graph."""
    g = Graph()
    g.parse(str(REF_PATH), format="turtle")
    return g


@pytest.fixture
def sample_external_post() -> dict:
    """A sample post with External embed."""
    return {
        "uri": "at://did:plc:abc123/app.bsky.feed.post/3lbphn3qxk22l",
        "cid": "bafyrei_test",
        "author": "reuters.com",
        "authorDid": "did:plc:abc123",
        "authorProfile": {
            "did": "did:plc:abc123",
            "handle": "reuters.com",
            "displayName": "Reuters",
        },
        "text": "Big news on #solar energy and battery storage in Australia",
        "createdAt": "2026-02-01T09:00:00.000Z",
        "hashtags": ["#solar"],
        "mentions": [],
        "mentionDids": [],
        "links": ["https://reuters.com/article/test-solar"],
        "embed": {
            "uri": "https://reuters.com/article/test-solar",
            "title": "Australia solar farm reaches record output",
            "description": "A major solar farm in Queensland has set new records.",
            "_tag": "External",
        },
        "metrics": {
            "replyCount": 5,
            "repostCount": 12,
            "likeCount": 42,
            "quoteCount": 3,
        },
    }


@pytest.fixture
def sample_images_post() -> dict:
    """A sample post with Images embed."""
    return {
        "uri": "at://did:plc:def456/app.bsky.feed.post/3lfsrh6kenj2u",
        "author": "energynews.bsky.social",
        "authorProfile": {
            "handle": "energynews.bsky.social",
            "displayName": "Energy News",
        },
        "text": "Wind turbine installation photos #wind",
        "createdAt": "2026-02-02T10:30:00.000Z",
        "hashtags": ["#wind"],
        "mentions": [],
        "embed": {
            "images": [
                {
                    "thumb": "https://cdn.bsky.app/img/thumb/1.jpg",
                    "fullsize": "https://cdn.bsky.app/img/full/1.jpg",
                    "alt": "Wind turbines at sunset",
                },
                {
                    "thumb": "https://cdn.bsky.app/img/thumb/2.jpg",
                    "fullsize": "https://cdn.bsky.app/img/full/2.jpg",
                    "alt": "",
                },
            ],
            "_tag": "Images",
        },
        "recordEmbed": {
            "images": [
                {"alt": "Wind turbines at sunset", "image": {"mimeType": "image/jpeg"}},
                {"alt": "", "image": {"mimeType": "image/png"}},
            ],
        },
        "metrics": {"replyCount": 0, "repostCount": 1, "likeCount": 5},
    }


@pytest.fixture
def sample_record_post() -> dict:
    """A sample post with Record embed (quote post)."""
    return {
        "uri": "at://did:plc:ghi789/app.bsky.feed.post/3kquotepost1",
        "author": "quoter.bsky.social",
        "authorProfile": {"handle": "quoter.bsky.social", "displayName": "Quoter"},
        "text": "Great thread on CCS technology",
        "createdAt": "2026-02-03T14:00:00.000Z",
        "hashtags": [],
        "mentions": [],
        "embed": {
            "record": {
                "uri": "at://did:plc:orig/app.bsky.feed.post/3koriginalpost",
            },
            "_tag": "Record",
        },
        "metrics": {"replyCount": 0, "repostCount": 0, "likeCount": 1},
    }


@pytest.fixture
def sample_no_embed_post() -> dict:
    """A sample text-only post."""
    return {
        "uri": "at://did:plc:jkl012/app.bsky.feed.post/3ltextonly001",
        "author": "textonly.bsky.social",
        "authorProfile": {"handle": "textonly.bsky.social", "displayName": "Text Only"},
        "text": "Just sharing thoughts on nuclear energy policy",
        "createdAt": "2026-02-04T08:00:00.000Z",
        "hashtags": [],
        "mentions": [],
        "metrics": {"replyCount": 0, "repostCount": 0, "likeCount": 0},
    }


# ---------------------------------------------------------------------------
# IRI minting
# ---------------------------------------------------------------------------


class TestIRIMinting:
    """Test IRI minting helpers."""

    def test_extract_rkey(self) -> None:
        """Extract record key from AT-URI."""
        from ingest.transform import _extract_rkey

        uri = "at://did:plc:abc/app.bsky.feed.post/3lbphn3qxk22l"
        assert _extract_rkey(uri) == "3lbphn3qxk22l"

    def test_hash_url(self) -> None:
        """URL hash is deterministic and 12 chars."""
        from ingest.transform import _hash_url

        h1 = _hash_url("https://reuters.com/article/test")
        h2 = _hash_url("https://reuters.com/article/test")
        h3 = _hash_url("https://reuters.com/article/other")
        assert h1 == h2
        assert h1 != h3
        assert len(h1) == 12

    def test_slugify_handle(self) -> None:
        """Handle slugification removes dots and dashes."""
        from ingest.transform import _slugify_handle

        assert _slugify_handle("reuters.com") == "reuters_com"
        assert _slugify_handle("energy-news.bsky.social") == "energy_news_bsky_social"


# ---------------------------------------------------------------------------
# Shorteners
# ---------------------------------------------------------------------------


class TestShorteners:
    """Test URL shortener utilities."""

    def test_extract_domain(self) -> None:
        """Domain extraction strips www. prefix."""
        from ingest.shorteners import extract_domain

        assert extract_domain("https://www.reuters.com/article/x") == "reuters.com"
        assert extract_domain("https://reuters.com/article/x") == "reuters.com"
        assert extract_domain("https://bit.ly/abc123") == "bit.ly"

    def test_is_brand_shortener(self) -> None:
        """Brand shorteners resolve without HTTP."""
        from ingest.shorteners import is_brand_shortener

        assert is_brand_shortener("https://reut.rs/abc123") == "reuters.com"
        assert is_brand_shortener("https://nyti.ms/abc123") == "nytimes.com"
        assert is_brand_shortener("https://reuters.com/article/x") is None

    def test_is_generic_shortener(self) -> None:
        """Generic shortener detection works."""
        from ingest.shorteners import is_generic_shortener

        assert is_generic_shortener("https://bit.ly/abc123") is True
        assert is_generic_shortener("https://buff.ly/abc123") is True
        assert is_generic_shortener("https://reuters.com/article/x") is False

    def test_collect_shortener_urls(self) -> None:
        """Collect generic shortener URLs from post embeds."""
        from ingest.shorteners import collect_shortener_urls

        posts = [
            {"embed": {"uri": "https://bit.ly/abc123", "_tag": "External"}},
            {"embed": {"uri": "https://reuters.com/x", "_tag": "External"}},
            {"embed": {"uri": "https://bit.ly/abc123", "_tag": "External"}},  # dupe
            {"embed": {"uri": "https://buff.ly/xyz", "_tag": "External"}},
            {"embed": {"_tag": "Images"}},
            {},
        ]
        urls = collect_shortener_urls(posts)
        assert len(urls) == 2
        assert "https://bit.ly/abc123" in urls
        assert "https://buff.ly/xyz" in urls


# ---------------------------------------------------------------------------
# Publications
# ---------------------------------------------------------------------------


class TestPublications:
    """Test publication resolution."""

    def test_build_ref_index(self, ref_graph: Graph) -> None:
        """Reference index contains 10 publications."""
        from ingest.publications import build_ref_publication_index

        index = build_ref_publication_index(ref_graph)
        assert len(index.domains) >= 10
        assert "reuters.com" in index.domains
        assert "electrek.co" in index.domains

    def test_resolve_reference_publication(self, ref_graph: Graph) -> None:
        """Reference publication resolved for known domain."""
        from ingest.publications import build_ref_publication_index, resolve_publication

        index = build_ref_publication_index(ref_graph)
        g = Graph()
        pub = resolve_publication("https://reuters.com/article/test", index, g)
        assert pub is not None
        assert "reuters" in str(pub).lower()

    def test_resolve_brand_shortener(self, ref_graph: Graph) -> None:
        """Brand shortener resolves to known publication."""
        from ingest.publications import build_ref_publication_index, resolve_publication

        index = build_ref_publication_index(ref_graph)
        g = Graph()
        pub = resolve_publication("https://reut.rs/abc123", index, g)
        assert pub is not None
        assert "reuters" in str(pub).lower()

    def test_resolve_new_domain_mints_publication(self, ref_graph: Graph) -> None:
        """Unknown domain gets a new minted Publication."""
        from ingest.publications import build_ref_publication_index, resolve_publication

        index = build_ref_publication_index(ref_graph)
        g = Graph()
        pub = resolve_publication("https://newsite.example.com/article/1", index, g)
        assert pub is not None
        assert (pub, RDF.type, ENEWS.Publication) in g
        assert (pub, ENEWS.siteDomain, Literal("newsite.example.com")) in g

    def test_resolve_cached_shortener(self, ref_graph: Graph) -> None:
        """Generic shortener resolved via cache."""
        from ingest.publications import build_ref_publication_index, resolve_publication

        index = build_ref_publication_index(ref_graph)
        g = Graph()
        cache = {"https://bit.ly/abc": "https://reuters.com/article/real"}
        pub = resolve_publication("https://bit.ly/abc", index, g, shortener_cache=cache)
        assert pub is not None
        assert "reuters" in str(pub).lower()


# ---------------------------------------------------------------------------
# Topics
# ---------------------------------------------------------------------------


class TestTopics:
    """Test topic matching."""

    def test_build_topic_lookup(self, ref_graph: Graph) -> None:
        """Topic lookup indexes labels and altLabels."""
        from ingest.topics import build_topic_lookup

        lookup = build_topic_lookup(ref_graph)
        assert len(lookup.keywords) > 50
        # Check a known label
        assert lookup.get("solar") is not None
        # Check a known altLabel
        assert lookup.get("CCS") is not None or lookup.get("ccs") is not None

    def test_match_hashtags(self, ref_graph: Graph) -> None:
        """Hashtag matching finds topics."""
        from ingest.topics import build_topic_lookup, match_topics

        lookup = build_topic_lookup(ref_graph)
        matched = match_topics("", ["#solar"], lookup)
        assert len(matched) >= 1

    def test_match_keywords_in_text(self, ref_graph: Graph) -> None:
        """Keyword matching finds topics in text."""
        from ingest.topics import build_topic_lookup, match_topics

        lookup = build_topic_lookup(ref_graph)
        matched = match_topics("Big news about nuclear energy and wind power", [], lookup)
        assert len(matched) >= 1


# ---------------------------------------------------------------------------
# Transform
# ---------------------------------------------------------------------------


class TestTransform:
    """Test the core transform pipeline."""

    def _make_indexes(self, ref_graph: Graph):
        from ingest.publications import build_ref_publication_index
        from ingest.topics import build_topic_lookup

        return build_ref_publication_index(ref_graph), build_topic_lookup(ref_graph)

    def test_external_embed(self, ref_graph: Graph, sample_external_post: dict) -> None:
        """External embed creates Post, Author, Embed, Article, Publication."""
        from ingest.transform import transform_posts

        pub_index, topic_lookup = self._make_indexes(ref_graph)
        g, stats = transform_posts([sample_external_post], pub_index, topic_lookup)

        assert stats.posts == 1
        assert stats.embeds_external == 1
        assert stats.articles == 1
        assert stats.authors == 1

        # Post exists
        post_uri = DATA["post/3lbphn3qxk22l"]
        assert (post_uri, RDF.type, ENEWS.Post) in g
        assert (post_uri, ENEWS.postText, None) in g

        # Author exists
        author_uri = DATA["author/reuters_com"]
        assert (author_uri, RDF.type, ENEWS.AuthorAccount) in g
        assert (author_uri, ENEWS.handle, Literal("reuters.com")) in g
        assert (author_uri, ENEWS.onPlatform, ENEWS.Bluesky) in g
        assert (author_uri, ENEWS.displayName, Literal("Reuters")) in g

        # Embed exists
        embed_uri = DATA["embed/3lbphn3qxk22l"]
        assert (embed_uri, RDF.type, ENEWS.EmbeddedExternalLink) in g
        assert (post_uri, ENEWS.hasEmbed, embed_uri) in g

        # Article exists with Publication
        articles = list(g.subjects(RDF.type, ENEWS.Article))
        assert len(articles) >= 1

        # Metrics
        assert (
            post_uri,
            ENEWS.likeCount,
            Literal(42, datatype=XSD.nonNegativeInteger),
        ) in g
        assert (
            post_uri,
            ENEWS.repostCount,
            Literal(12, datatype=XSD.nonNegativeInteger),
        ) in g

    def test_images_embed(self, ref_graph: Graph, sample_images_post: dict) -> None:
        """Images embed creates MediaAttachments with fullsize URLs and alt text."""
        from ingest.transform import transform_posts

        pub_index, topic_lookup = self._make_indexes(ref_graph)
        g, stats = transform_posts([sample_images_post], pub_index, topic_lookup)

        assert stats.posts == 1
        assert stats.embeds_images == 1
        assert stats.media_attachments == 2

        # Media 1
        media1 = DATA["media/3lfsrh6kenj2u_1"]
        assert (media1, RDF.type, ENEWS.MediaAttachment) in g
        assert (
            media1,
            ENEWS.mediaUri,
            Literal("https://cdn.bsky.app/img/full/1.jpg", datatype=XSD.anyURI),
        ) in g
        assert (media1, ENEWS.altText, Literal("Wind turbines at sunset")) in g
        assert (media1, ENEWS.mimeType, Literal("image/jpeg")) in g

        # Media 2 — no alt text (empty string)
        media2 = DATA["media/3lfsrh6kenj2u_2"]
        assert (media2, RDF.type, ENEWS.MediaAttachment) in g
        assert (media2, ENEWS.mimeType, Literal("image/png")) in g
        # Empty alt should NOT be added
        alt_texts = list(g.objects(media2, ENEWS.altText))
        assert len(alt_texts) == 0

    def test_record_embed(self, ref_graph: Graph, sample_record_post: dict) -> None:
        """Record embed creates isReplyTo link."""
        from ingest.transform import transform_posts

        pub_index, topic_lookup = self._make_indexes(ref_graph)
        g, stats = transform_posts([sample_record_post], pub_index, topic_lookup)

        assert stats.embeds_record == 1

        post_uri = DATA["post/3kquotepost1"]
        quoted_uri = DATA["post/3koriginalpost"]
        assert (post_uri, ENEWS.isReplyTo, quoted_uri) in g

    def test_no_embed(self, ref_graph: Graph, sample_no_embed_post: dict) -> None:
        """Text-only post creates just Post + Author."""
        from ingest.transform import transform_posts

        pub_index, topic_lookup = self._make_indexes(ref_graph)
        g, stats = transform_posts([sample_no_embed_post], pub_index, topic_lookup)

        assert stats.posts == 1
        assert stats.embeds_none == 1
        assert stats.articles == 0

        post_uri = DATA["post/3ltextonly001"]
        assert (post_uri, RDF.type, ENEWS.Post) in g

    def test_multiple_posts(
        self,
        ref_graph: Graph,
        sample_external_post: dict,
        sample_images_post: dict,
        sample_no_embed_post: dict,
    ) -> None:
        """Multiple posts produce correct aggregate stats."""
        from ingest.transform import transform_posts

        pub_index, topic_lookup = self._make_indexes(ref_graph)
        posts = [sample_external_post, sample_images_post, sample_no_embed_post]
        _g, stats = transform_posts(posts, pub_index, topic_lookup)

        assert stats.posts == 3
        assert stats.embeds_external == 1
        assert stats.embeds_images == 1
        assert stats.embeds_none == 1
        assert stats.authors == 3  # three different handles


# ---------------------------------------------------------------------------
# Dedup
# ---------------------------------------------------------------------------


class TestDedup:
    """Test article deduplication."""

    def test_dedup_merges_same_url(self) -> None:
        """Articles with the same URL are merged."""
        from ingest.dedup import deduplicate_articles

        g = Graph()
        url = Literal("https://reuters.com/article/test", datatype=XSD.anyURI)

        art1 = DATA["article/aaa"]
        art2 = DATA["article/bbb"]
        g.add((art1, RDF.type, ENEWS.Article))
        g.add((art1, ENEWS.url, url))
        g.add((art1, ENEWS.coversTopic, ENEWS.Solar))

        g.add((art2, RDF.type, ENEWS.Article))
        g.add((art2, ENEWS.url, url))
        g.add((art2, ENEWS.coversTopic, ENEWS.Wind))

        # Post referencing the duplicate
        post = DATA["post/xyz"]
        g.add((post, ENEWS.sharesArticle, art2))

        merged = deduplicate_articles(g)
        assert merged == 1

        # art1 keeps both topics
        topics = set(g.objects(art1, ENEWS.coversTopic))
        assert ENEWS.Solar in topics
        assert ENEWS.Wind in topics

        # Post now points to canonical
        assert (post, ENEWS.sharesArticle, art1) in g
        assert (post, ENEWS.sharesArticle, art2) not in g

        # art2 is gone
        assert (art2, RDF.type, ENEWS.Article) not in g

    def test_no_dedup_different_urls(self) -> None:
        """Articles with different URLs are not merged."""
        from ingest.dedup import deduplicate_articles

        g = Graph()
        art1 = DATA["article/aaa"]
        art2 = DATA["article/bbb"]
        g.add((art1, RDF.type, ENEWS.Article))
        g.add((art1, ENEWS.url, Literal("https://a.com/1", datatype=XSD.anyURI)))
        g.add((art2, RDF.type, ENEWS.Article))
        g.add((art2, ENEWS.url, Literal("https://b.com/2", datatype=XSD.anyURI)))

        merged = deduplicate_articles(g)
        assert merged == 0


# ---------------------------------------------------------------------------
# Namespaces
# ---------------------------------------------------------------------------


class TestNamespaces:
    """Test namespace configuration."""

    def test_bind_abox_prefixes(self) -> None:
        """bind_abox_prefixes sets expected prefixes."""
        from ingest.namespaces import bind_abox_prefixes

        g = Graph()
        bind_abox_prefixes(g)
        ns_map = dict(g.namespaces())
        assert "enews" in ns_map
        assert "data" in ns_map
        assert "schema" in ns_map
