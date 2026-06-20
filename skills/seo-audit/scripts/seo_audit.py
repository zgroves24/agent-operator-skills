#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import sys
import time
from dataclasses import dataclass, field
from html.parser import HTMLParser
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urljoin, urlparse
from urllib.request import Request, build_opener
from xml.etree import ElementTree as ET

USER_AGENT = "AgentSEOAudit/1.0"

DEFAULT_PUBLIC_PATHS = ["/", "/pricing", "/features", "/blog", "/docs"]
DEFAULT_PRIVATE_PATHS = ["/login", "/account", "/admin", "/reset-password"]
DEFAULT_KEY_SITEMAP_PATHS = ["/", "/pricing", "/features", "/blog"]
DEFAULT_SAMPLE_PREFIXES = ["/blog/", "/docs/", "/guides/", "/features/"]
DEFAULT_PRIVATE_PATTERNS = [
    r"/login/?$",
    r"/account",
    r"/admin",
    r"/api/",
    r"/auth/",
    r"/dashboard",
    r"/settings",
    r"/reset-password",
]


class SeoHtmlParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.title = ""
        self._in_title = False
        self._in_h1 = False
        self._in_json_ld = False
        self._h1_parts: list[str] = []
        self._json_parts: list[str] = []
        self.h1s: list[str] = []
        self.meta: dict[str, str] = {}
        self.links: list[dict[str, str]] = []
        self.anchors: list[str] = []
        self.images: list[dict[str, str]] = []
        self.json_ld_raw: list[str] = []
        self.html_attrs: dict[str, str] = {}

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attrs_dict = {k.lower(): v or "" for k, v in attrs}
        tag = tag.lower()
        if tag == "html":
            self.html_attrs.update(attrs_dict)
        elif tag == "title":
            self._in_title = True
        elif tag == "meta":
            key = (attrs_dict.get("name") or attrs_dict.get("property") or "").lower()
            content = attrs_dict.get("content", "")
            if key and content:
                self.meta[key] = content.strip()
        elif tag == "link":
            self.links.append(attrs_dict)
        elif tag == "a":
            href = attrs_dict.get("href")
            if href:
                self.anchors.append(href)
        elif tag == "img":
            self.images.append(attrs_dict)
        elif tag == "h1":
            self._in_h1 = True
            self._h1_parts = []
        elif tag == "script" and attrs_dict.get("type", "").lower() == "application/ld+json":
            self._in_json_ld = True
            self._json_parts = []

    def handle_endtag(self, tag: str) -> None:
        tag = tag.lower()
        if tag == "title":
            self._in_title = False
        elif tag == "h1":
            self._in_h1 = False
            text = " ".join("".join(self._h1_parts).split())
            if text:
                self.h1s.append(text)
        elif tag == "script" and self._in_json_ld:
            self._in_json_ld = False
            raw = "".join(self._json_parts).strip()
            if raw:
                self.json_ld_raw.append(raw)

    def handle_data(self, data: str) -> None:
        if self._in_title:
            self.title += data
            self.title = " ".join(self.title.split())
        elif self._in_h1:
            self._h1_parts.append(data)
        elif self._in_json_ld:
            self._json_parts.append(data)

    @property
    def canonical(self) -> str | None:
        for link in self.links:
            if link.get("rel", "").lower() == "canonical":
                return link.get("href")
        return None


@dataclass
class FetchResult:
    url: str
    final_url: str
    status: int
    body: str
    content_type: str
    elapsed_ms: int
    error: str | None = None


@dataclass
class Check:
    category: str
    name: str
    weight: float
    score: float
    passed: bool
    message: str


@dataclass
class AuditState:
    checks: list[Check] = field(default_factory=list)
    findings: list[str] = field(default_factory=list)

    def add(self, category: str, name: str, weight: float, passed: bool, message: str, partial: float | None = None) -> None:
        score = weight if passed else 0.0
        if partial is not None:
            score = max(0.0, min(weight, partial))
            passed = score >= weight * 0.999
        self.checks.append(Check(category, name, weight, score, passed, message))
        if score < weight:
            self.findings.append(f"{category}: {name} - {message}")

    @property
    def score(self) -> float:
        return round(sum(check.score for check in self.checks), 1)

    @property
    def possible(self) -> float:
        return round(sum(check.weight for check in self.checks), 1)


def grade(score: float) -> str:
    if score >= 95:
        return "Excellent"
    if score >= 90:
        return "Strong"
    if score >= 80:
        return "Good"
    if score >= 70:
        return "Risky"
    return "Do not ship"


def clean_base(url: str) -> str:
    parsed = urlparse(url)
    if not parsed.scheme:
        url = "https://" + url
    return url.rstrip("/")


def normalize_url(base: str, path: str) -> str:
    if path.startswith("http://") or path.startswith("https://"):
        return path
    return urljoin(base + "/", path.lstrip("/"))


def fetch(url: str, timeout: int = 15) -> FetchResult:
    started = time.perf_counter()
    try:
        opener = build_opener()
        request = Request(url, headers={"User-Agent": USER_AGENT, "Accept": "text/html,application/xml,text/plain,*/*"})
        with opener.open(request, timeout=timeout) as response:
            raw = response.read()
            body = raw.decode(response.headers.get_content_charset() or "utf-8", errors="replace")
            elapsed = int((time.perf_counter() - started) * 1000)
            return FetchResult(url, response.geturl(), response.status, body, response.headers.get("content-type", ""), elapsed)
    except HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        elapsed = int((time.perf_counter() - started) * 1000)
        return FetchResult(url, exc.geturl(), exc.code, body, exc.headers.get("content-type", ""), elapsed, str(exc))
    except URLError as exc:
        elapsed = int((time.perf_counter() - started) * 1000)
        return FetchResult(url, url, 0, "", "", elapsed, str(exc))


def parse_html(body: str) -> SeoHtmlParser:
    parser = SeoHtmlParser()
    parser.feed(body)
    return parser


def json_ld_types(parser: SeoHtmlParser) -> tuple[list[str], list[str]]:
    types: list[str] = []
    errors: list[str] = []
    for raw in parser.json_ld_raw:
        try:
            parsed = json.loads(raw)
        except json.JSONDecodeError as exc:
            errors.append(str(exc))
            continue
        items = parsed if isinstance(parsed, list) else [parsed]
        for item in items:
            if isinstance(item, dict):
                item_type = item.get("@type")
                if isinstance(item_type, list):
                    types.extend(str(value) for value in item_type)
                elif item_type:
                    types.append(str(item_type))
    return types, errors


def sitemap_locs(xml_body: str) -> list[str]:
    if not xml_body.strip():
        return []
    try:
        root = ET.fromstring(xml_body.encode("utf-8"))
    except ET.ParseError:
        return []
    locs: list[str] = []
    for elem in root.iter():
        if elem.tag.endswith("loc") and elem.text:
            locs.append(elem.text.strip())
    return locs


def robots_rules(robots_body: str) -> tuple[list[tuple[bool, str]], list[str]]:
    rules: list[tuple[bool, str]] = []
    sitemaps: list[str] = []
    applies = False
    for raw_line in robots_body.splitlines():
        line = raw_line.split("#", 1)[0].strip()
        if not line or ":" not in line:
            continue
        key, value = [part.strip() for part in line.split(":", 1)]
        key = key.lower()
        if key == "user-agent":
            applies = value == "*"
        elif key == "sitemap":
            sitemaps.append(value)
        elif applies and key in {"allow", "disallow"}:
            rules.append((key == "allow", value))
    return rules, sitemaps


def robots_allows(path: str, rules: list[tuple[bool, str]]) -> bool:
    best: tuple[int, bool] | None = None
    for allow, pattern in rules:
        if not pattern:
            continue
        regex = re.escape(pattern).replace(r"\*", ".*")
        if re.search(regex, path):
            length = len(pattern)
            if best is None or length > best[0]:
                best = (length, allow)
    return True if best is None else best[1]


def ratio_pass(items: list[bool], weight: float) -> float:
    if not items:
        return 0.0
    return weight * (sum(1 for item in items if item) / len(items))


def unique(values: list[str]) -> list[str]:
    seen: set[str] = set()
    out: list[str] = []
    for value in values:
        if value not in seen:
            seen.add(value)
            out.append(value)
    return out


def audit(
    base_url: str,
    sample_limit: int,
    public_paths: list[str],
    private_paths: list[str],
    key_sitemap_paths: list[str],
    sample_prefixes: list[str],
    private_patterns: list[str],
) -> dict[str, Any]:
    base = clean_base(base_url)
    state = AuditState()

    robots = fetch(normalize_url(base, "/robots.txt"))
    state.add("crawl", "robots.txt is reachable", 4, robots.status == 200, f"robots.txt returned {robots.status}")
    rules, robots_sitemaps = robots_rules(robots.body if robots.status == 200 else "")
    root_allowed = robots_allows("/", rules)
    state.add("crawl", "root URL is not blocked by robots", 6, root_allowed, "robots.txt blocks /")
    state.add("crawl", "robots.txt links a sitemap", 3, bool(robots_sitemaps), "robots.txt has no Sitemap line")

    sitemap_url = normalize_url(base, "/sitemap.xml")
    if robots_sitemaps and urlparse(robots_sitemaps[0]).netloc == urlparse(base).netloc:
        sitemap_url = robots_sitemaps[0]
    sitemap = fetch(sitemap_url)
    locs = sitemap_locs(sitemap.body if sitemap.status == 200 else "")
    state.add("crawl", "sitemap is reachable and parseable", 5, sitemap.status == 200 and bool(locs), f"sitemap returned {sitemap.status} with {len(locs)} URLs")

    loc_path_set = {urlparse(loc).path.rstrip("/") or "/" for loc in locs}
    key_present = [(urlparse(normalize_url(base, path)).path.rstrip("/") or "/") in loc_path_set for path in key_sitemap_paths]
    state.add("crawl", "key SEO URLs are in sitemap", 5, all(key_present), f"{sum(key_present)}/{len(key_present)} key URLs found", ratio_pass(key_present, 5))

    private_regexes = [re.compile(pattern) for pattern in private_patterns]
    private_hits = [loc for loc in locs if any(pattern.search(urlparse(loc).path) for pattern in private_regexes)]
    state.add("crawl", "private URLs are omitted from sitemap", 3, not private_hits, f"private-looking sitemap URLs: {private_hits[:5]}")

    sitemap_public_samples: list[str] = []
    for loc in locs:
        path = urlparse(loc).path
        if any(path.startswith(prefix) for prefix in sample_prefixes):
            sitemap_public_samples.append(path)
        if len(sitemap_public_samples) >= sample_limit:
            break

    test_paths = unique(public_paths + sitemap_public_samples + private_paths)
    pages: dict[str, dict[str, Any]] = {}
    public_pages: list[tuple[str, FetchResult, SeoHtmlParser]] = []
    private_pages: list[tuple[str, FetchResult, SeoHtmlParser]] = []

    for path in test_paths:
        result = fetch(normalize_url(base, path))
        parser = parse_html(result.body) if "html" in result.content_type or result.body.lstrip().startswith("<!DOCTYPE") else SeoHtmlParser()
        types, json_errors = json_ld_types(parser)
        data = {
            "requested_path": path,
            "url": result.url,
            "final_url": result.final_url,
            "status": result.status,
            "elapsed_ms": result.elapsed_ms,
            "content_type": result.content_type,
            "title": parser.title,
            "description": parser.meta.get("description"),
            "robots": parser.meta.get("robots"),
            "canonical": parser.canonical,
            "h1s": parser.h1s,
            "json_ld_types": types,
            "json_ld_errors": json_errors,
            "internal_links": len([href for href in parser.anchors if href.startswith("/") or href.startswith(base)]),
            "og_title": parser.meta.get("og:title"),
            "og_description": parser.meta.get("og:description"),
            "viewport": parser.meta.get("viewport"),
            "lang": parser.html_attrs.get("lang"),
            "html_bytes": len(result.body.encode("utf-8")),
        }
        pages[path] = data
        if path in private_paths:
            private_pages.append((path, result, parser))
        else:
            public_pages.append((path, result, parser))

    status_checks = [result.status == 200 and urlparse(result.final_url).path not in private_paths for _, result, _ in public_pages]
    state.add("crawl", "public SEO pages return 200 without private redirect", 4, all(status_checks), f"{sum(status_checks)}/{len(status_checks)} public pages returned clean 200", ratio_pass(status_checks, 4))

    title_checks = [10 <= len(parser.title) <= 70 for _, result, parser in public_pages if result.status == 200]
    state.add("on_page", "public pages have usable titles", 5, all(title_checks), f"{sum(title_checks)}/{len(title_checks)} titles are 10-70 chars", ratio_pass(title_checks, 5))

    desc_checks = [50 <= len(parser.meta.get("description", "")) <= 180 for _, result, parser in public_pages if result.status == 200]
    state.add("on_page", "public pages have usable meta descriptions", 5, all(desc_checks), f"{sum(desc_checks)}/{len(desc_checks)} descriptions are 50-180 chars", ratio_pass(desc_checks, 5))

    h1_checks = [len(parser.h1s) == 1 for _, result, parser in public_pages if result.status == 200]
    state.add("on_page", "public pages have exactly one H1", 4, all(h1_checks), f"{sum(h1_checks)}/{len(h1_checks)} pages have one H1", ratio_pass(h1_checks, 4))

    canonical_checks = []
    for _, result, parser in public_pages:
        if result.status != 200:
            continue
        canonical = parser.canonical or ""
        canonical_checks.append(bool(canonical.startswith("https://") and urlparse(canonical).netloc))
    state.add("on_page", "public pages have absolute HTTPS canonicals", 4, all(canonical_checks), f"{sum(canonical_checks)}/{len(canonical_checks)} pages have absolute HTTPS canonicals", ratio_pass(canonical_checks, 4))

    og_checks = [bool(parser.meta.get("og:title") and parser.meta.get("og:description")) for _, result, parser in public_pages if result.status == 200]
    state.add("on_page", "public pages have Open Graph basics", 3, all(og_checks), f"{sum(og_checks)}/{len(og_checks)} pages include og:title and og:description", ratio_pass(og_checks, 3))

    link_checks = [len([href for href in parser.anchors if href.startswith("/") or href.startswith(base)]) >= 5 for _, result, parser in public_pages if result.status == 200]
    state.add("on_page", "public pages expose internal links", 2, all(link_checks), f"{sum(link_checks)}/{len(link_checks)} pages have at least 5 internal links", ratio_pass(link_checks, 2))

    private_noindex = []
    for _, result, parser in private_pages:
        robots_meta = (parser.meta.get("robots") or "").lower()
        private_noindex.append("noindex" in robots_meta or result.status in {401, 403, 404})
    state.add("on_page", "private/auth pages are noindexed or unavailable", 2, all(private_noindex), f"{sum(private_noindex)}/{len(private_noindex)} private pages noindex/unavailable", ratio_pass(private_noindex, 2))

    all_json_errors = [error for _, _, parser in public_pages for error in json_ld_types(parser)[1]]
    state.add("structured_data", "JSON-LD parses cleanly", 5, not all_json_errors, f"JSON-LD parse errors: {all_json_errors[:3]}")

    all_types = [typ for _, _, parser in public_pages for typ in json_ld_types(parser)[0]]
    state.add("structured_data", "no FAQPage markup on ordinary pages", 3, "FAQPage" not in all_types, "FAQPage markup found")
    state.add("structured_data", "no unsupported app rich-result markup", 3, "SoftwareApplication" not in all_types and "WebApplication" not in all_types, "SoftwareApplication/WebApplication markup found")

    root_types = pages.get("/", {}).get("json_ld_types", [])
    state.add("structured_data", "root exposes Organization or WebSite schema", 2, "Organization" in root_types or "WebSite" in root_types, f"root JSON-LD types: {root_types}")

    coverage_checks = [pages.get(path, {}).get("status") == 200 for path in public_paths]
    state.add("content", "configured public pages exist", 8, all(coverage_checks), f"{sum(coverage_checks)}/{len(coverage_checks)} configured public pages return 200", ratio_pass(coverage_checks, 8))

    sampled_checks = [pages.get(path, {}).get("status") == 200 for path in sitemap_public_samples]
    if sampled_checks:
        state.add("content", "sampled sitemap content pages are reachable", 4, all(sampled_checks), f"{sum(sampled_checks)}/{len(sampled_checks)} sampled URLs return 200", ratio_pass(sampled_checks, 4))
    else:
        state.add("content", "sampled sitemap content pages are reachable", 4, True, "no sitemap sample URLs found")

    response_times = [result.elapsed_ms for _, result, _ in public_pages if result.status == 200]
    avg_ms = sum(response_times) / len(response_times) if response_times else 999999
    state.add("performance", "average public HTML response is fast", 4, avg_ms <= 1000, f"average response {avg_ms:.0f}ms")
    state.add("performance", "no public HTML response is very slow", 2, max(response_times or [999999]) <= 2500, f"max response {max(response_times or [0])}ms")

    size_checks = [len(result.body.encode("utf-8")) <= 1_500_000 for _, result, _ in public_pages if result.status == 200]
    state.add("performance", "public HTML documents are not oversized", 1, all(size_checks), f"{sum(size_checks)}/{len(size_checks)} HTML documents <= 1.5MB", ratio_pass(size_checks, 1))

    viewport_checks = [bool(parser.meta.get("viewport")) for _, result, parser in public_pages if result.status == 200]
    state.add("performance", "public pages include viewport metadata", 2, all(viewport_checks), f"{sum(viewport_checks)}/{len(viewport_checks)} pages include viewport", ratio_pass(viewport_checks, 2))

    lang_checks = [bool(parser.html_attrs.get("lang")) for _, result, parser in public_pages if result.status == 200]
    state.add("performance", "public pages include html lang", 1, all(lang_checks), f"{sum(lang_checks)}/{len(lang_checks)} pages include lang", ratio_pass(lang_checks, 1))

    raw_score = state.score
    raw_possible = state.possible
    score_percent = round((raw_score / raw_possible) * 100, 1) if raw_possible else 0.0

    return {
        "base_url": base,
        "score": score_percent,
        "possible": 100.0,
        "raw_score": raw_score,
        "raw_possible": raw_possible,
        "grade": grade(score_percent),
        "checks": [check.__dict__ for check in state.checks],
        "findings": state.findings,
        "robots": {
            "status": robots.status,
            "sitemaps": robots_sitemaps,
            "root_allowed": root_allowed,
        },
        "sitemap": {
            "status": sitemap.status,
            "url": sitemap_url,
            "url_count": len(locs),
            "private_hits": private_hits[:20],
            "sampled_urls": sitemap_public_samples,
        },
        "pages": pages,
    }


def print_markdown(result: dict[str, Any]) -> None:
    print(f"# SEO Audit: {result['base_url']}")
    print()
    print(f"Score: **{result['score']:.1f}/{result['possible']:.0f} ({result['grade']})**")
    print(f"Raw weighted score: {result['raw_score']:.1f}/{result['raw_possible']:.0f}")
    print()
    print("## Failed Or Partial Checks")
    failed = [check for check in result["checks"] if check["score"] < check["weight"]]
    if not failed:
        print("- None")
    else:
        for check in failed:
            print(f"- [{check['category']}] {check['name']}: {check['score']:.1f}/{check['weight']:.1f} - {check['message']}")
    print()
    print("## Core Evidence")
    print(f"- robots.txt status: {result['robots']['status']}")
    print(f"- root allowed by robots: {result['robots']['root_allowed']}")
    print(f"- sitemap status: {result['sitemap']['status']}")
    print(f"- sitemap URL count: {result['sitemap']['url_count']}")
    print(f"- private-looking sitemap hits: {len(result['sitemap']['private_hits'])}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Deterministic technical SEO audit.")
    parser.add_argument("--base-url", required=True)
    parser.add_argument("--sample-limit", type=int, default=80)
    parser.add_argument("--public-path", action="append", dest="public_paths")
    parser.add_argument("--private-path", action="append", dest="private_paths")
    parser.add_argument("--key-sitemap-path", action="append", dest="key_sitemap_paths")
    parser.add_argument("--sample-prefix", action="append", dest="sample_prefixes")
    parser.add_argument("--private-pattern", action="append", dest="private_patterns")
    parser.add_argument("--json", action="store_true", help="Print JSON instead of Markdown")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    result = audit(
        args.base_url,
        args.sample_limit,
        args.public_paths or DEFAULT_PUBLIC_PATHS,
        args.private_paths or DEFAULT_PRIVATE_PATHS,
        args.key_sitemap_paths or DEFAULT_KEY_SITEMAP_PATHS,
        args.sample_prefixes or DEFAULT_SAMPLE_PREFIXES,
        args.private_patterns or DEFAULT_PRIVATE_PATTERNS,
    )
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print_markdown(result)
    return 0 if result["score"] >= 90 else 2


if __name__ == "__main__":
    sys.exit(main())
