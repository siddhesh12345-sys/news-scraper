
from __future__ import annotations

import csv
import json
import logging
import re
import shutil

from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from pathlib import Path
from typing import Any

import requests
from bs4 import BeautifulSoup
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


# ==================================================
# CONFIGURATION
# ==================================================

ROOT = Path(__file__).resolve().parent.parent

FEEDS_FILE = ROOT / "config" / "feeds.json"
DATA_DIR = ROOT / "data"
CSV_FILE = DATA_DIR / "news.csv"
BACKUP_FILE = DATA_DIR / "news_backup.csv"

FIELDS = [
    "headline",
    "published",
    "source",
    "link",
    "category"
]

DATA_DIR.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)

logger = logging.getLogger("newspulse")


# ==================================================
# TEXT CLEANING
# ==================================================

def clean_text(value: Any) -> str:

    if value is None:
        return ""

    return re.sub(
        r"\s+",
        " ",
        str(value)
    ).strip()


# ==================================================
# HEADLINE CATEGORIZATION
# ==================================================

def categorize_headline(headline: str) -> str:

    text = headline.lower()

    ott_patterns = [
        r"\bnetflix\b",
        r"\bprime video\b",
        r"\bamazon prime\b",
        r"\bott\b",
        r"\bdisney\s*\+",
        r"\bhotstar\b",
        r"\bsony liv\b",
        r"\bzee5\b",
        r"\bstreaming\b",
        r"\bapple tv\s*\+"
    ]

    studio_patterns = [
        r"\bwarner bros\b",
        r"\bwarner brothers\b",
        r"\bparamount\b",
        r"\buniversal pictures\b",
        r"\bsony pictures\b",
        r"\bdisney studios\b",
        r"\bmarvel studios\b",
        r"\b20th century studios\b",
        r"\bfilm studio\b"
    ]

    if any(re.search(pattern, text) for pattern in ott_patterns):
        return "OTT Platform"

    if any(re.search(pattern, text) for pattern in studio_patterns):
        return "Studio"

    return "Other"


# ==================================================
# DATE PARSING
# ==================================================

def parse_date(value: str) -> str:

    if not value:
        return ""

    try:

        dt = parsedate_to_datetime(value)

        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)

        return dt.astimezone(timezone.utc).strftime(
            "%Y-%m-%d %H:%M UTC"
        )

    except (TypeError, ValueError, OverflowError):

        try:

            dt = datetime.fromisoformat(
                value.replace("Z", "+00:00")
            )

            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)

            return dt.astimezone(timezone.utc).strftime(
                "%Y-%m-%d %H:%M UTC"
            )

        except ValueError:

            return clean_text(value)


# ==================================================
# NEWS SCRAPER
# ==================================================

class NewsScraper:

    def __init__(
        self,
        feeds_file: Path = FEEDS_FILE,
        csv_file: Path = CSV_FILE,
        timeout: int = 15
    ):

        self.feeds_file = Path(feeds_file)
        self.csv_file = Path(csv_file)
        self.timeout = timeout

        self.session = requests.Session()

        retry = Retry(
            total=3,
            connect=3,
            read=3,
            backoff_factor=0.8,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["GET"],
            raise_on_status=False
        )

        adapter = HTTPAdapter(max_retries=retry)

        self.session.mount("https://", adapter)
        self.session.mount("http://", adapter)

        self.session.headers.update({
            "User-Agent": (
                "NewsPulse/1.0 "
                "(educational RSS reader; contact: project-owner)"
            )
        })


    # ==================================================
    # LOAD RSS FEEDS
    # ==================================================

    def load_feeds(self) -> list[dict[str, str]]:

        if not self.feeds_file.exists():
            raise FileNotFoundError(
                f"Feed configuration not found: {self.feeds_file}"
            )

        with self.feeds_file.open(
            "r",
            encoding="utf-8"
        ) as file:

            config = json.load(file)

        feeds = config.get("feeds", [])

        if not isinstance(feeds, list):
            raise ValueError("Invalid feeds configuration.")

        return feeds


    # ==================================================
    # FETCH NEWS FROM RSS
    # ==================================================

    def fetch_feed(
        self,
        feed: dict[str, str]
    ) -> list[dict[str, str]]:

        name = feed["name"]
        url = feed["url"]

        response = self.session.get(
            url,
            timeout=self.timeout
        )

        response.raise_for_status()

        soup = BeautifulSoup(
            response.content,
            "xml"
        )

        entries = soup.find_all("item")

        # Support Atom feeds.
        if not entries:
            entries = soup.find_all("entry")

        records = []

        for entry in entries:

            title_tag = entry.find("title")
            link_tag = entry.find("link")

            date_tag = (
                entry.find("pubDate")
                or entry.find("published")
                or entry.find("updated")
            )

            title = clean_text(
                title_tag.get_text(" ", strip=True)
                if title_tag else ""
            )

            link = ""

            if link_tag:

                link = clean_text(
                    link_tag.get("href")
                    or link_tag.get_text(" ", strip=True)
                )

            if title and link.startswith(("http://", "https://")):

                records.append({

                    "headline": title,

                    "published": parse_date(
                        date_tag.get_text(" ", strip=True)
                        if date_tag else ""
                    ),

                    "source": name,

                    "link": link,

                    "category": categorize_headline(title)

                })

        return records


    # ==================================================
    # READ EXISTING CSV SAFELY
    # ==================================================

    def load_existing(self) -> list[dict[str, str]]:

        if (
            not self.csv_file.exists()
            or self.csv_file.stat().st_size == 0
        ):
            return []

        existing = []

        try:

            with self.csv_file.open(
                "r",
                newline="",
                encoding="utf-8-sig"
            ) as file:

                reader = csv.reader(
                    file,
                    strict=False
                )

                header = next(reader, None)

                if not header:
                    return []

                header = [
                    clean_text(column).lower()
                    for column in header
                ]

                if header != FIELDS:

                    logger.warning(
                        "CSV header does not match expected columns. "
                        "Existing records cannot be safely mapped."
                    )

                    return []

                for line_number, row in enumerate(reader, start=2):

                    # Ignore completely empty rows.
                    if not row or not any(clean_text(v) for v in row):
                        continue

                    # Recover unquoted commas in the headline.
                    # The remaining four fields are kept separate.
                    if len(row) > len(FIELDS):

                        extra = len(row) - len(FIELDS) + 1

                        row = [
                            ",".join(row[:extra]),
                            *row[extra:]
                        ]

                    # Skip rows that cannot be safely reconstructed.
                    if len(row) != len(FIELDS):

                        logger.warning(
                            "Skipping malformed CSV row: %s",
                            line_number
                        )

                        continue

                    record = {
                        field: clean_text(value)
                        for field, value in zip(FIELDS, row)
                    }

                    if record["headline"] and record["link"]:

                        existing.append(record)

        except (OSError, csv.Error, UnicodeError) as error:

            logger.error(
                "Could not read existing CSV: %s",
                error
            )

            raise

        return self.deduplicate(existing)


    # ==================================================
    # REMOVE DUPLICATES
    # ==================================================

    @staticmethod
    def deduplicate(
        records: list[dict[str, str]]
    ) -> list[dict[str, str]]:

        seen = set()
        unique = []

        for row in records:

            link_key = clean_text(
                row.get("link", "")
            ).rstrip("/").lower()

            title_key = clean_text(
                row.get("headline", "")
            ).lower()

            if not link_key or not title_key:
                continue

            if (
                link_key in seen
                or f"title:{title_key}" in seen
            ):
                continue

            seen.add(link_key)
            seen.add(f"title:{title_key}")

            unique.append({

                field: clean_text(
                    row.get(field, "")
                )

                for field in FIELDS

            })

        return unique


    # ==================================================
    # SAVE CSV SAFELY
    # ==================================================

    def save_records(
        self,
        records: list[dict[str, str]]
    ) -> int:

        self.csv_file.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        # Read and validate existing records.
        existing = self.load_existing()

        known = set()

        for row in existing:

            link_key = clean_text(
                row.get("link", "")
            ).rstrip("/").lower()

            title_key = (
                "title:"
                + clean_text(row.get("headline", "")).lower()
            )

            if link_key:
                known.add(link_key)

            if title_key != "title:":
                known.add(title_key)

        # Identify genuinely new headlines.
        new_rows = []

        for row in self.deduplicate(records):

            link_key = row["link"].rstrip("/").lower()

            title_key = "title:" + row["headline"].lower()

            if link_key in known or title_key in known:
                continue

            new_rows.append(row)

            known.add(link_key)
            known.add(title_key)

        # Keep existing and new records together.
        all_rows = self.deduplicate(
            existing + new_rows
        )

        # Back up original CSV before replacing it.
        if (
            self.csv_file.exists()
            and self.csv_file.stat().st_size > 0
            and not BACKUP_FILE.exists()
        ):

            shutil.copy2(
                self.csv_file,
                BACKUP_FILE
            )

            logger.info(
                "Created CSV backup: %s",
                BACKUP_FILE
            )

        # Write a clean CSV file.
        temp_file = self.csv_file.with_name(
            self.csv_file.name + ".tmp"
        )

        try:

            with temp_file.open(
                "w",
                newline="",
                encoding="utf-8-sig"
            ) as file:

                writer = csv.DictWriter(
                    file,
                    fieldnames=FIELDS,
                    extrasaction="ignore",
                    quoting=csv.QUOTE_MINIMAL,
                    lineterminator="\n"
                )

                writer.writeheader()

                writer.writerows(all_rows)

            # Replace the old CSV only after successful writing.
            temp_file.replace(self.csv_file)

        finally:

            if temp_file.exists():
                temp_file.unlink()

        logger.info(
            "CSV saved successfully. Total records: %s",
            len(all_rows)
        )

        return len(new_rows)


    # ==================================================
    # RUN COMPLETE SCRAPER
    # ==================================================

    def run(self) -> dict[str, Any]:

        all_records = []
        errors = []

        feeds = self.load_feeds()

        for feed in feeds:

            try:

                rows = self.fetch_feed(feed)

                all_records.extend(rows)

                logger.info(
                    "Fetched %s headlines from %s",
                    len(rows),
                    feed["name"]
                )

            except (
                requests.RequestException,
                KeyError,
                ValueError
            ) as exc:

                message = (
                    f"{feed.get('name', 'Unknown feed')}: {exc}"
                )

                logger.warning(message)

                errors.append(message)

        unique = self.deduplicate(all_records)

        added = self.save_records(unique)

        return {

            "fetched": len(all_records),

            "unique": len(unique),

            "added": added,

            "duplicates": (
                len(all_records) - len(unique)
                + len(unique) - added
            ),

            "errors": errors

        }


# ==================================================
# MAIN FUNCTION
# ==================================================

def main():

    result = NewsScraper().run()

    print("\nNewsPulse scrape summary")
    print("-" * 28)

    print(f"Fetched:    {result['fetched']}")
    print(f"Unique:     {result['unique']}")
    print(f"New rows:   {result['added']}")
    print(f"Duplicates: {result['duplicates']}")

    if result["errors"]:

        print("\nFeed warnings:")

        for error in result["errors"]:
            print(f"- {error}")


if __name__ == "__main__":
    main()
