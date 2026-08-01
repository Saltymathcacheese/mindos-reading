#!/usr/bin/env python3
"""
MindOS WeRead Data Pipeline
Fetches WeRead data and converts into structured cognitive analysis input.

Usage: python3 weread_fetch.py [--output weread.json]

Requires: WEREAD_API_KEY env var or --api-key flag.
Python >= 3.11
"""

from __future__ import annotations

import argparse
import json
import logging
import os
import sys
import time
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

import requests

# =====================================================
# Logging
# =====================================================
logger = logging.getLogger("mindos.weread")


def setup_logging(verbose: bool = False) -> None:
    logging.basicConfig(
        level=logging.DEBUG if verbose else logging.INFO,
        format="%(asctime)s | %(levelname)s | %(message)s",
    )


# =====================================================
# Config
# =====================================================
@dataclass
class Config:
    api_url: str = "https://i.weread.qq.com/api/agent/gateway"
    skill_version: str = "1.0.4"
    timeout: int = 15
    retries: int = 3
    backoff: float = 2.0


# =====================================================
# Exceptions
# =====================================================
class WeReadError(Exception):
    pass


class AuthenticationError(WeReadError):
    pass


class NetworkError(WeReadError):
    pass


# =====================================================
# API Client
# =====================================================
class WeReadClient:
    def __init__(self, config: Config, api_key: str):
        self.config = config
        self.key = api_key
        if not self.key or not self.key.startswith("wrk-"):
            raise AuthenticationError(
                "WEREAD_API_KEY missing or invalid. Expected format: wrk-xxxxxxxx"
            )

    def request(self, **payload: Any) -> dict:
        """Call weread agent gateway. Payload must include api_name at top level.
        skill_version is auto-injected. Business params flatten at body top level."""
        body: dict[str, Any] = {
            **payload,
            "skill_version": self.config.skill_version,
        }
        headers = {
            "Authorization": f"Bearer {self.key}",
            "Content-Type": "application/json",
        }

        last_error: Exception | None = None
        for attempt in range(self.config.retries):
            try:
                response = requests.post(
                    self.config.api_url,
                    json=body,
                    headers=headers,
                    timeout=self.config.timeout,
                )
                if response.status_code == 401:
                    raise AuthenticationError("API authentication failed")
                response.raise_for_status()
                data = response.json()
                if data.get("errcode", 0) != 0:
                    raise WeReadError(
                        f"API error {data.get('errcode')}: {data.get('errmsg', 'unknown')}"
                    )
                return data
            except (requests.RequestException, WeReadError) as e:
                last_error = e
                if isinstance(e, AuthenticationError):
                    raise  # don't retry auth errors
                wait = self.config.backoff**attempt
                logger.warning("Retry %s/%s after %ss", attempt + 1, self.config.retries, wait)
                time.sleep(wait)

        raise NetworkError(str(last_error))

    # ── API Methods ──
    def get_stats(self, mode: str = "monthly", base_time: int | None = None) -> dict:
        params: dict[str, Any] = {"api_name": "/readdata/detail", "mode": mode}
        if base_time is not None:
            params["baseTime"] = base_time
        return self.request(**params)

    def _get_notebooks_page(self, last_sort: int | None = None, count: int = 100) -> dict:
        """Internal: fetch a single page of notebooks. Use fetch_all_notebooks() instead."""
        params: dict[str, Any] = {"api_name": "/user/notebooks", "count": count}
        if last_sort is not None:
            params["lastSort"] = last_sort
        return self.request(**params)

    MAX_NOTEBOOK_PAGES = 100

    def fetch_all_notebooks(self, count: int = 100) -> list[dict]:
        """Paginate notebooks until hasMore=0, with safety cap at MAX_NOTEBOOK_PAGES."""
        all_books: list[dict] = []
        last_sort: int | None = None
        pages = 0
        while pages < self.MAX_NOTEBOOK_PAGES:
            data = self._get_notebooks_page(last_sort=last_sort, count=count)
            books = data.get("books", [])
            all_books.extend(books)
            pages += 1
            if not data.get("hasMore") or not books:
                break
            last_sort = data.get("lastSort") or (books[-1].get("sort", 0) if books else None)
        return all_books

    def get_shelf(self) -> dict:
        return self.request(api_name="/shelf/sync")

    def get_highlights(self, book_id: str) -> dict:
        return self.request(api_name="/book/bookmarklist", bookId=book_id)


# =====================================================
# Normalizer
# =====================================================
class WeReadNormalizer:
    @staticmethod
    def seconds_to_display(seconds: int) -> dict:
        """Convert seconds to {hours, minutes} dict."""
        s = int(seconds or 0)
        return {"hours": s // 3600, "minutes": (s % 3600) // 60, "total_seconds": s}

    @staticmethod
    def normalize_stats(data: dict) -> dict:
        return {
            "reading_time": WeReadNormalizer.seconds_to_display(
                data.get("totalReadTime", 0)
            ),
            "read_days": data.get("readDays", 0),
            "day_average_seconds": data.get("dayAverageReadTime", 0),
            "compare": data.get("compare", 0),
            "prefer_categories": data.get("preferCategory", []),
            "read_longest": data.get("readLongest", []),
            "read_stat": data.get("readStat", []),
        }

    @staticmethod
    def normalize_books(notebooks: list[dict]) -> list[dict]:
        """Parse /user/notebooks books[] into flat book records sorted by total_notes desc.
        Handles nested book.bookId / book.title structure."""
        books: list[dict] = []
        for item in notebooks:
            book_info = item.get("book", {})
            total = (
                item.get("reviewCount", 0)
                + item.get("noteCount", 0)
                + item.get("bookmarkCount", 0)
            )
            books.append(
                {
                    "book_id": item.get("bookId") or book_info.get("bookId", ""),
                    "title": book_info.get("title", "?"),
                    "author": book_info.get("author", "?"),
                    "categories": [c.get("title", "") for c in book_info.get("categories", [])],
                    "deep_link": book_info.get("deepLink", ""),
                    "review_count": item.get("reviewCount", 0),
                    "note_count": item.get("noteCount", 0),
                    "bookmark_count": item.get("bookmarkCount", 0),
                    "total_notes": total,
                    "marked_status": item.get("markedStatus", 0),
                    "reading_progress": item.get("readingProgress", 0),
                }
            )
        books.sort(key=lambda x: x["total_notes"], reverse=True)
        return books

    @staticmethod
    def normalize_shelf(data: dict) -> dict:
        books = data.get("books", [])
        albums = data.get("albums", [])
        mp = data.get("mp", {})
        archives = data.get("archive", [])
        return {
            "total_items": len(books) + len(albums) + (1 if mp else 0),
            "ebook_count": len(books),
            "album_count": len(albums),
            "has_articles": bool(mp),
            "archives": [
                {"name": a.get("name", ""), "book_count": len(a.get("bookIds", []))}
                for a in archives
            ],
        }


# =====================================================
# Highlight Sampler
# =====================================================
class HighlightSampler:
    @staticmethod
    def sample(highlights: list[dict], limit: int = 8) -> list[dict]:
        """Sample evenly from highlight list. Returns {markText, chapter} per item."""
        if not highlights:
            return []
        if len(highlights) <= limit:
            items = highlights
        else:
            step = len(highlights) / limit
            items = [highlights[int(i * step)] for i in range(limit)]

        return [
            {
                "text": h.get("markText", "")[:100],
                "chapter_uid": h.get("chapterUid"),
            }
            for h in items
        ]


# =====================================================
# Pipeline
# =====================================================
def run_pipeline(api_key: str, prev_month: str | None = None) -> dict:
    config = Config()
    client = WeReadClient(config, api_key)

    # ── Current month stats ──
    stats_raw = client.get_stats(mode="monthly")
    stats = WeReadNormalizer.normalize_stats(stats_raw)

    # ── Previous month stats ──
    prev_stats = None
    if prev_month:
        try:
            parts = prev_month.split("-")
            y, m = int(parts[0]), int(parts[1])
            ts = int(datetime(y, m, 1, 0, 0, 0).timestamp())
            prev_raw = client.get_stats(mode="monthly", base_time=ts)
            prev_stats = WeReadNormalizer.normalize_stats(prev_raw)
        except (ValueError, IndexError):
            logger.warning("Invalid --prev-month format, skipping")

    # ── Notebooks ──
    notebooks_raw = client.fetch_all_notebooks()
    books = WeReadNormalizer.normalize_books(notebooks_raw)

    # ── Shelf ──
    shelf_raw = client.get_shelf()
    shelf = WeReadNormalizer.normalize_shelf(shelf_raw)

    # ── Top 3 highlights ──
    highlights: list[dict] = []
    for book in books[:3]:
        try:
            raw = client.get_highlights(book["book_id"])
            sampled = HighlightSampler.sample(raw.get("updated", []))
            highlights.append({"book": book["title"], "highlights": sampled})
        except WeReadError:
            highlights.append({"book": book["title"], "highlights": []})

    return {
        "stats": stats,
        "prev_stats": prev_stats,
        "books_top10": books[:10],
        "books_total": len(books),
        "total_notes_all_books": sum(b["total_notes"] for b in books),
        "shelf": shelf,
        "highlights_top3": highlights,
    }


# =====================================================
# CLI
# =====================================================
def main():
    parser = argparse.ArgumentParser(description="MindOS WeRead Data Pipeline")
    parser.add_argument("--api-key", default=None, help="WeRead API key (or set WEREAD_API_KEY env)")
    parser.add_argument("--output", default=None, help="Write JSON to file")
    parser.add_argument("--prev-month", default=None, help="Previous month for comparison (YYYY-MM)")
    parser.add_argument("--verbose", action="store_true")
    args = parser.parse_args()

    setup_logging(args.verbose)

    api_key = args.api_key or os.environ.get("WEREAD_API_KEY", "")
    if not api_key:
        print(json.dumps({"success": False, "error": "WEREAD_API_KEY not set"}))
        sys.exit(1)

    try:
        result = run_pipeline(api_key, prev_month=args.prev_month)
        output = json.dumps({"success": True, "data": result}, ensure_ascii=False, indent=2)
        if args.output:
            Path(args.output).write_text(output, encoding="utf-8")
        print(output)
    except Exception as e:
        logger.exception("Pipeline failed")
        print(json.dumps({"success": False, "error": str(e)}, ensure_ascii=False))
        sys.exit(1)


if __name__ == "__main__":
    main()
