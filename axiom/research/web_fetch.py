"""Controlled HTTP fetch for research sources — SSRF-hardened, untrusted by default."""

from __future__ import annotations

import ipaddress
import re
import socket
from dataclasses import dataclass
from datetime import datetime, timezone
from html.parser import HTMLParser
from typing import Iterable
from urllib.parse import urlparse, urljoin

import requests

from axiom.observability.logger import get_logger

logger = get_logger(__name__)

DEFAULT_ALLOWED_HOSTS: frozenset[str] = frozenset(
    {
        "arxiv.org",
        "export.arxiv.org",
        "www.arxiv.org",
        "doi.org",
        "dx.doi.org",
        "pubmed.ncbi.nlm.nih.gov",
        "www.ncbi.nlm.nih.gov",
        "openreview.net",
        "www.openreview.net",
    }
)

MAX_BYTES_DEFAULT = 2 * 1024 * 1024  # 2 MiB
TIMEOUT_DEFAULT = 20.0
MAX_REDIRECTS = 3


class WebFetchError(ValueError):
    """Raised when a URL cannot be fetched safely."""


@dataclass(frozen=True)
class FetchedDocument:
    url: str
    final_url: str
    retrieved_at: str
    content_type: str
    title: str
    text: str
    content_hash: str
    bytes_read: int


class _HTMLTextExtractor(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self._chunks: list[str] = []
        self._skip = False
        self.title = ""
        self._in_title = False

    def handle_starttag(self, tag: str, attrs) -> None:  # type: ignore[no-untyped-def]
        if tag in {"script", "style", "noscript"}:
            self._skip = True
        if tag == "title":
            self._in_title = True

    def handle_endtag(self, tag: str) -> None:
        if tag in {"script", "style", "noscript"}:
            self._skip = False
        if tag == "title":
            self._in_title = False

    def handle_data(self, data: str) -> None:
        if self._skip:
            return
        text = data.strip()
        if not text:
            return
        if self._in_title and not self.title:
            self.title = text
        self._chunks.append(text)

    def get_text(self) -> str:
        return "\n".join(self._chunks)


def _utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _host_allowed(hostname: str, allowed_hosts: Iterable[str]) -> bool:
    host = (hostname or "").lower().rstrip(".")
    if not host:
        return False
    for allowed in allowed_hosts:
        allowed = allowed.lower().rstrip(".")
        if host == allowed or host.endswith("." + allowed):
            return True
    return False


def _is_public_ip(ip_str: str) -> bool:
    try:
        ip = ipaddress.ip_address(ip_str)
    except ValueError:
        return False
    return not (
        ip.is_private
        or ip.is_loopback
        or ip.is_link_local
        or ip.is_multicast
        or ip.is_reserved
        or ip.is_unspecified
    )


def validate_fetch_url(
    url: str,
    *,
    allowed_hosts: Iterable[str] | None = None,
) -> str:
    """Validate URL scheme/host and resolve DNS to public IPs only."""
    parsed = urlparse(url.strip())
    if parsed.scheme != "https":
        raise WebFetchError("Only HTTPS URLs are allowed")
    if not parsed.hostname:
        raise WebFetchError("URL must include a hostname")
    if parsed.username or parsed.password:
        raise WebFetchError("URLs with embedded credentials are not allowed")
    if parsed.port not in (None, 443):
        raise WebFetchError("Only default HTTPS port 443 is allowed")

    hosts = set(allowed_hosts) if allowed_hosts is not None else set(DEFAULT_ALLOWED_HOSTS)
    if not _host_allowed(parsed.hostname, hosts):
        raise WebFetchError(f"Host not on allowlist: {parsed.hostname}")

    try:
        infos = socket.getaddrinfo(parsed.hostname, 443, type=socket.SOCK_STREAM)
    except socket.gaierror as exc:
        raise WebFetchError(f"DNS resolution failed for {parsed.hostname}") from exc

    if not infos:
        raise WebFetchError(f"No addresses resolved for {parsed.hostname}")

    for info in infos:
        sockaddr = info[4]
        ip = sockaddr[0]
        if not _is_public_ip(ip):
            raise WebFetchError(f"Resolved address is not public: {ip}")

    return parsed.geturl()


def _extract_text(content_type: str, raw: bytes, url: str) -> tuple[str, str]:
    """Return (title, text) from response bytes."""
    charset = "utf-8"
    if "charset=" in content_type.lower():
        match = re.search(r"charset=([^\s;]+)", content_type, re.IGNORECASE)
        if match:
            charset = match.group(1).strip("\"'")

    if "pdf" in content_type.lower() or url.lower().endswith(".pdf"):
        from axiom.research.pdf_extractor import PdfExtractor

        extraction = PdfExtractor().extract_bytes(raw)
        title = url.rsplit("/", 1)[-1] or "Fetched PDF"
        return title, extraction.text

    text = raw.decode(charset, errors="replace")
    if "html" in content_type.lower() or text.lstrip().lower().startswith("<!doctype html") or "<html" in text[:500].lower():
        parser = _HTMLTextExtractor()
        parser.feed(text)
        title = parser.title or (url.rsplit("/", 1)[-1] or "Fetched page")
        return title, parser.get_text()

    title = url.rsplit("/", 1)[-1] or "Fetched document"
    return title, text


def fetch_research_url(
    url: str,
    *,
    allowed_hosts: Iterable[str] | None = None,
    timeout_seconds: float = TIMEOUT_DEFAULT,
    max_bytes: int = MAX_BYTES_DEFAULT,
    session: requests.Session | None = None,
) -> FetchedDocument:
    """
    Fetch a research URL with host allowlist, public-IP DNS checks, size/time limits.

    Content is always treated as UNTRUSTED by callers.
    """
    from axiom.skai.extractor import content_hash

    current = validate_fetch_url(url, allowed_hosts=allowed_hosts)
    http = session or requests.Session()
    headers = {
        "User-Agent": "AXIOM-ResearchBot/0.2 (+https://github.com/anujjha101296-lang/AXIOM; research fetch)",
        "Accept": "text/html,application/xhtml+xml,text/plain,application/pdf,application/xml;q=0.9,*/*;q=0.8",
    }

    redirects = 0
    while True:
        resp = http.get(
            current,
            headers=headers,
            timeout=timeout_seconds,
            allow_redirects=False,
            stream=True,
        )
        if resp.is_redirect or resp.status_code in {301, 302, 303, 307, 308}:
            redirects += 1
            if redirects > MAX_REDIRECTS:
                raise WebFetchError("Too many redirects")
            location = resp.headers.get("Location")
            if not location:
                raise WebFetchError("Redirect without Location header")
            next_url = urljoin(current, location)
            current = validate_fetch_url(next_url, allowed_hosts=allowed_hosts)
            continue

        if resp.status_code >= 400:
            raise WebFetchError(f"HTTP {resp.status_code} fetching {current}")

        content_type = resp.headers.get("Content-Type", "application/octet-stream")
        chunks: list[bytes] = []
        total = 0
        for chunk in resp.iter_content(chunk_size=64 * 1024):
            if not chunk:
                continue
            total += len(chunk)
            if total > max_bytes:
                raise WebFetchError(f"Response exceeds max size of {max_bytes} bytes")
            chunks.append(chunk)
        raw = b"".join(chunks)
        title, text = _extract_text(content_type, raw, current)
        text = text.strip()
        if not text:
            raise WebFetchError("No extractable text from fetched URL")

        retrieved_at = _utc_now()
        digest = content_hash(text)
        logger.info(
            "Fetched research URL",
            extra={
                "url": url,
                "final_url": current,
                "bytes": total,
                "content_type": content_type,
            },
        )
        return FetchedDocument(
            url=url.strip(),
            final_url=current,
            retrieved_at=retrieved_at,
            content_type=content_type.split(";")[0].strip().lower(),
            title=title[:300],
            text=text,
            content_hash=digest,
            bytes_read=total,
        )
