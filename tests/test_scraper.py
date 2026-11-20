from newspulse.scraper import categorize_headline, parse_date, NewsScraper


def test_category_ott():
    assert categorize_headline("Netflix announces a new series") == "OTT Platform"


def test_category_studio():
    assert categorize_headline("Warner Bros reveals its upcoming film") == "Studio"


def test_category_other():
    assert categorize_headline("Local team wins championship") == "Other"


def test_parse_empty_date():
    assert parse_date("") == ""


def test_deduplicate_by_title_and_link():
    rows = [
        {"headline": "A headline", "published": "", "source": "A", "link": "https://example.com/1", "category": "Other"},
        {"headline": "A headline", "published": "", "source": "B", "link": "https://example.com/2", "category": "Other"},
        {"headline": "Another headline", "published": "", "source": "A", "link": "https://example.com/1", "category": "Other"},
    ]
    assert len(NewsScraper.deduplicate(rows)) == 1
