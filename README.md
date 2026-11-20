# NewsPulse — News Headline Scraper & Analytics Dashboard

NewsPulse is a Python project that collects publicly available news metadata from RSS feeds, classifies headlines, removes duplicates, stores results in CSV, and displays them in an interactive Streamlit dashboard.

## Features

- Fetches RSS/XML feeds using `requests` and parses them with BeautifulSoup.
- Extracts headline, publication date, publisher/source, and article URL.
- Retries temporary HTTP failures and applies request timeouts.
- Categorizes headlines as **OTT Platform**, **Studio**, or **Other** using keyword and regular-expression rules.
- Removes duplicates using normalized article links and headline text.
- Appends only new records to `data/news.csv`.
- Provides dashboard search, category/source filters, headline links, metrics, chart, and CSV export.

## Project structure

```text
NewsPulse/
├── app.py
├── scraper.py
├── newspulse/
│   ├── __init__.py
│   └── scraper.py
├── config/
│   └── feeds.json
├── data/
│   └── .gitkeep
├── tests/
│   └── test_scraper.py
├── requirements.txt
├── .gitignore
└── README.md
```

## Requirements

- Python 3.10 or newer
- VS Code
- Internet connection

## Run locally in VS Code (Windows)

1. Download or clone this repository and open the `NewsPulse` folder in VS Code.
2. Open **Terminal → New Terminal**.
3. Create a virtual environment:

   ```powershell
   py -m venv .venv
   ```

4. Activate it:

   ```powershell
   .\.venv\Scripts\Activate.ps1
   ```

   If PowerShell blocks activation, run this once in that terminal and retry:

   ```powershell
   Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
   .\.venv\Scripts\Activate.ps1
   ```

5. Install dependencies:

   ```powershell
   python -m pip install --upgrade pip
   pip install -r requirements.txt
   ```

6. Run the scraper from the project root:

   ```powershell
   python scraper.py
   ```

   The collected data is saved to `data/news.csv`. Run the command again later; already-seen links/headlines are skipped.

7. Start the dashboard:

   ```powershell
   streamlit run app.py
   ```

   Streamlit will show a local address, usually `http://localhost:8501`. Open it in your browser.

## Configure news feeds

Edit `config/feeds.json` to add or remove RSS feed names and URLs. Use feeds that permit automated RSS access. Some publishers may change or restrict their feed URLs; a failed feed is reported as a warning while other feeds continue.

## Deploy a live dashboard with Streamlit Community Cloud

1. Create a GitHub repository named `newspulse-news-scraper`.
2. Upload and push the project files to the repository.
3. Open [Streamlit Community Cloud](https://share.streamlit.io/) and sign in with GitHub.
4. Select **Create app**, choose your repository and branch, and set the main file path to `app.py`.
5. Deploy. Streamlit will install packages from `requirements.txt` and provide a public app URL.

**Important deployment note:** Streamlit Community Cloud uses an ephemeral runtime. The dashboard can run live, but CSV data written by the app may reset when the app restarts or redeploys. For durable production storage, connect a database or persistent storage service. Do not commit private credentials or secrets to GitHub.

## Tests

Install pytest if needed:

```powershell
pip install pytest
python -m pytest -q
```

## Limitations and responsible use

- This project reads RSS feeds rather than scraping full publisher webpages.
- It stores metadata and links, not full copyrighted article text.
- Category assignment is rule-based and may misclassify headlines; extend the patterns in `categorize_headline()` to improve it.
- Respect publisher terms, robots policies where applicable, feed rate limits, and copyright.
- This is an educational portfolio project, not a guaranteed real-time news service.

## Resume description

**NewsPulse – News Headline Scraper & Analytics Dashboard | Python, Requests, BeautifulSoup, Pandas, Streamlit, CSV**

- Developed a Python-based RSS scraper to collect news headlines, publication dates, sources, and article URLs from multiple feeds.
- Implemented retry handling, request timeouts, regex-based OTT/Studio categorization, and duplicate detection.
- Stored new records in CSV and built an interactive Streamlit dashboard with search, filters, analytics, and CSV export.
