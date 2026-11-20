
# 📰 NewsPulse — News Headline Scraper & Analytics Dashboard

**NewsPulse** is a Python-based news headline scraper and analytics dashboard that collects publicly available news metadata from RSS feeds, categorizes headlines, removes duplicate records, and displays the results through an interactive Streamlit web application.

<p align="center">
  <a href="https://news-scraper-ddalyncnkpu4ccbdk73493.streamlit.app/">
    <img src="https://img.shields.io/badge/Live%20Demo-Open%20NewsPulse-brightgreen?style=for-the-badge&logo=streamlit" alt="Live Demo">
  </a>
  <a href="https://github.com/siddhesh12345-sys/news-scraper">
    <img src="https://img.shields.io/badge/GitHub-Repository-black?style=for-the-badge&logo=github" alt="GitHub Repository">
  </a>
</p>

🌐 **Live Website:** https://news-scraper-ddalyncnkpu4ccbdk73493.streamlit.app/

📂 **GitHub Repository:** https://github.com/siddhesh12345-sys/news-scraper

---

## 🚀 Features

- Fetches RSS/XML feeds using `requests` and parses them with BeautifulSoup.
- Extracts news headlines, publication dates, publisher names, and article URLs.
- Implements retry handling and request timeouts for temporary HTTP failures.
- Categorizes headlines into **OTT Platform**, **Studio**, and **Other** using keyword and regular-expression rules.
- Removes duplicate records using normalized article links and headline text.
- Stores collected news data in CSV format.
- Appends only new records without duplicating existing headlines.
- Provides an interactive Streamlit dashboard with:
  - News headline search
  - Category and source filters
  - Clickable article links
  - News analytics and metrics
  - Charts and visualizations
  - CSV data export

---

## 🛠️ Technologies Used

| Technology | Purpose |
|---|---|
| Python | Core programming language |
| Requests | Fetching RSS feeds |
| BeautifulSoup | XML/RSS parsing |
| Pandas | Data processing and analysis |
| Streamlit | Interactive web dashboard |
| CSV | Data storage |
| Regular Expressions | Headline categorization |
| Pytest | Unit testing |
| Git & GitHub | Version control |

---

## 📁 Project Structure

```text
NewsPulse/
│
├── app.py
├── scraper.py
│
├── newspulse/
│   ├── __init__.py
│   └── scraper.py
│
├── config/
│   └── feeds.json
│
├── data/
│   └── .gitkeep
│
├── tests/
│   └── test_scraper.py
│
├── requirements.txt
├── .gitignore
└── README.md
```

---

## 💻 Requirements

- Python 3.10 or newer
- Visual Studio Code
- Git
- Internet connection

---

## ⚙️ Installation & Setup

### 1. Clone the Repository

Open the VS Code terminal and run:

```powershell
git clone https://github.com/siddhesh12345-sys/news-scraper.git
```

### 2. Open the Project Folder

```powershell
cd news-scraper
```

### 3. Create a Virtual Environment

```powershell
py -m venv .venv
```

### 4. Activate the Virtual Environment

```powershell
.\.venv\Scripts\Activate.ps1
```

If PowerShell blocks activation, run:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
```

Then activate again:

```powershell
.\.venv\Scripts\Activate.ps1
```

### 5. Install Dependencies

```powershell
python -m pip install --upgrade pip
pip install -r requirements.txt
```

---

## ▶️ Running the Project

### Step 1: Run the News Scraper

```powershell
python scraper.py
```

The scraper fetches news metadata from configured RSS feeds and saves the collected records in:

```text
data/news.csv
```

Previously collected headlines are skipped to prevent duplicate entries.

### Step 2: Launch the Streamlit Dashboard

```powershell
streamlit run app.py
```

The dashboard will run locally at:

**http://localhost:8501**

Open the URL in your browser to explore the NewsPulse dashboard.

---

## 📰 Configure News Feeds

You can customize the RSS feeds by editing:

```text
config/feeds.json
```

Add or remove RSS feed names and URLs according to your requirements.

The scraper handles individual feed failures and continues processing other available feeds.

---

## ☁️ Live Deployment

NewsPulse is deployed using **Streamlit Community Cloud**.

Deployment steps:

1. Push the project files to your GitHub repository.
2. Visit [Streamlit Community Cloud](https://share.streamlit.io/).
3. Sign in using your GitHub account.
4. Select **Create App**.
5. Choose your GitHub repository and branch.
6. Set the main file path to `app.py`.
7. Click **Deploy**.

**Live Application:** [Open NewsPulse Dashboard](https://news-scraper-ddalyncnkpu4ccbdk73493.streamlit.app/)

**Deployment Note:** Streamlit Community Cloud uses an ephemeral runtime. CSV files generated during runtime may not persist after restarts or redeployments. Use a database or persistent storage solution for long-term data storage.

---

## 🧪 Running Tests

Install Pytest if it is not already installed:

```powershell
pip install pytest
```

Run the test suite:

```powershell
python -m pytest -q
```

---

## ⚠️ Limitations & Responsible Use

- The project collects RSS feed metadata rather than scraping complete publisher webpages.
- It stores headlines and article links, not full copyrighted article content.
- Headline categorization uses rule-based logic and may occasionally misclassify records.
- RSS feed availability depends on individual publishers.
- Follow publisher terms, applicable robots policies, rate limits, and copyright requirements.

---

## 📄 Resume Description

**NewsPulse – News Headline Scraper & Analytics Dashboard**

*Python | Requests | BeautifulSoup | Pandas | Streamlit | CSV*

- Developed a Python-based RSS scraper to collect news headlines, publication dates, sources, and article URLs from multiple feeds.
- Implemented retry handling, request timeouts, regex-based OTT/Studio categorization, and duplicate detection.
- Stored new records in CSV and developed an interactive Streamlit dashboard featuring search, filters, analytics, and CSV export.

---

## 👨‍💻 Author

**Siddhesh Bane**

- GitHub: [siddhesh12345-sys](https://github.com/siddhesh12345-sys)
- Project Repository: [NewsPulse](https://github.com/siddhesh12345-sys/news-scraper)
- Live Application: [NewsPulse Dashboard](https://news-scraper-ddalyncnkpu4ccbdk73493.streamlit.app/)

---

⭐ If you find this project useful, consider giving it a star on GitHub!
