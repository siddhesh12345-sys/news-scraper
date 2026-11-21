
from pathlib import Path
import html
import pandas as pd
import streamlit as st

from scraper import NewsScraper


# ==================================================
# CONFIGURATION
# ==================================================

ROOT = Path(__file__).resolve().parent
DATA_DIR = ROOT / "data"
CSV_PATH = DATA_DIR / "news.csv"

DATA_DIR.mkdir(parents=True, exist_ok=True)

EXPECTED_COLUMNS = [
    "headline",
    "published",
    "source",
    "link",
    "category"
]

st.set_page_config(
    page_title="NewsPulse | News Intelligence",
    page_icon="📰",
    layout="wide"
)


# ==================================================
# PROFESSIONAL DESIGN / CUSTOM CSS
# ==================================================

st.markdown("""
<style>

.stApp {
    background: #0b1120;
    color: #f1f5f9;
    font-family: "Inter", "Segoe UI", Arial, sans-serif;
}

.block-container {
    max-width: 1300px;
    padding-top: 2rem;
    padding-bottom: 3rem;
}

h1 {
    color: #f8fafc !important;
    font-size: 40px !important;
    font-weight: 800 !important;
}

h2, h3, h4 {
    color: #f1f5f9 !important;
    font-weight: 700 !important;
}

.stMarkdown p,
label {
    color: #dbe5f2;
}

[data-testid="stCaptionContainer"] {
    color: #a9bad0 !important;
}

[data-testid="stMetric"] {
    background: #17243a;
    border: 1px solid #304663;
    padding: 20px;
    border-radius: 14px;
}

[data-testid="stMetricLabel"] {
    color: #bdcbe0 !important;
    font-weight: 600;
}

[data-testid="stMetricValue"] {
    color: #60a5fa !important;
    font-size: 30px !important;
    font-weight: 800 !important;
}

.stTextInput input {
    background: #17243a !important;
    color: #ffffff !important;
    border: 1px solid #3b506d !important;
    border-radius: 9px !important;
}

.stTextInput input::placeholder {
    color: #a8b6c9 !important;
    opacity: 1;
}

.stSelectbox div[data-baseweb="select"] > div {
    background: #17243a !important;
    color: #ffffff !important;
    border: 1px solid #3b506d !important;
    border-radius: 9px !important;
}

.stSelectbox span {
    color: #ffffff !important;
}

[data-baseweb="popover"],
[data-baseweb="menu"] {
    background: #17243a !important;
}

[data-baseweb="menu"] li {
    color: #ffffff !important;
}

.news-card {
    background: #17243a;
    border: 1px solid #304663;
    padding: 20px;
    border-radius: 13px;
    margin-bottom: 14px;
    transition: all 0.2s ease;
}

.news-card:hover {
    border-color: #60a5fa;
    transform: translateY(-2px);
}

.news-card a {
    color: #93c5fd !important;
    font-size: 17px;
    font-weight: 700;
    text-decoration: none;
    line-height: 1.6;
}

.news-card a:hover {
    color: #bfdbfe !important;
    text-decoration: underline;
}

.small-muted {
    color: #b0bfd3 !important;
    font-size: 13px;
    margin-top: 10px;
}

.stButton > button,
.stDownloadButton > button {
    background: #2563eb !important;
    color: #ffffff !important;
    border: 1px solid #3b82f6 !important;
    border-radius: 9px !important;
    padding: 10px 18px;
    font-weight: 700 !important;
}

.stButton > button:hover,
.stDownloadButton > button:hover {
    background: #1d4ed8 !important;
    border-color: #60a5fa !important;
}

.stButton > button p,
.stDownloadButton > button p {
    color: #ffffff !important;
    font-weight: 700 !important;
}

hr {
    border-color: #26364e !important;
}

[data-testid="stSidebar"] {
    background: #111c2e;
}

[data-testid="stSidebar"] * {
    color: #e2eaf5;
}

footer {
    visibility: hidden;
}

</style>
""", unsafe_allow_html=True)


# ==================================================
# HEADER
# ==================================================

st.title("📰 NewsPulse")

st.markdown("""
<p style="
    color:#a9bad0;
    font-size:16px;
    font-weight:500;
    margin-top:-10px;
">
    News Intelligence & Analytics Dashboard
</p>
""", unsafe_allow_html=True)

st.divider()


# ==================================================
# LOAD DATA - IMPROVED CSV HANDLING
# ==================================================

@st.cache_data
def load_data(path, modified):

    file_path = Path(path)

    if not file_path.exists() or file_path.stat().st_size == 0:
        return pd.DataFrame(columns=EXPECTED_COLUMNS)

    data = None
    last_error = None

    # Try supported encodings and CSV parsing methods.
    for encoding in ["utf-8-sig", "utf-8", "latin-1"]:

        try:

            data = pd.read_csv(
                file_path,
                encoding=encoding,
                on_bad_lines="warn",
                skipinitialspace=True
            )

            break

        except (
            pd.errors.ParserError,
            UnicodeDecodeError,
            pd.errors.EmptyDataError
        ) as error:

            last_error = error

            # Try another encoding if reading fails.
            continue

    if data is None:

        st.error(
            f"Unable to read news.csv: {last_error}"
        )

        return pd.DataFrame(columns=EXPECTED_COLUMNS)

    # Remove unnamed or unnecessary CSV columns.
    data = data.loc[
        :,
        ~data.columns.astype(str).str.startswith("Unnamed")
    ]

    # Add missing expected columns.
    for column in EXPECTED_COLUMNS:

        if column not in data.columns:
            data[column] = ""

    # Keep only expected columns.
    data = data[EXPECTED_COLUMNS].copy()

    # Handle missing values.
    data = data.fillna("")

    # Convert columns to strings.
    for column in EXPECTED_COLUMNS:

        data[column] = data[column].astype(str).str.strip()

    # Remove completely empty headlines.
    data = data[
        data["headline"].str.strip() != ""
    ]

    # Remove duplicate headlines and links.
    data = data.drop_duplicates(
        subset=["link", "headline"],
        keep="last"
    )

    return data.reset_index(drop=True)


# ==================================================
# BACKEND SCRAPER
# ==================================================

def save_scrape():

    scraper = NewsScraper()

    with st.spinner("Fetching latest news headlines..."):

        result = scraper.run()

    st.cache_data.clear()

    return result


# ==================================================
# FETCH NEWS
# ==================================================

st.subheader("🚀 News Collection")

if st.button(
    "🔄 Fetch Latest Headlines",
    type="primary"
):

    try:

        result = save_scrape()

        st.success(
            f"Scraping completed! "
            f"Fetched: {result['fetched']} | "
            f"New: {result['added']} | "
            f"Duplicates: {result['duplicates']}"
        )

        if result.get("errors"):

            with st.expander("View Feed Warnings"):

                for error in result["errors"]:
                    st.warning(error)

        st.rerun()

    except Exception as error:

        st.error(f"Scraping failed: {error}")


# ==================================================
# READ CSV
# ==================================================

modified = (
    CSV_PATH.stat().st_mtime_ns
    if CSV_PATH.exists()
    else 0
)

df = load_data(str(CSV_PATH), modified)


# ==================================================
# EMPTY STATE
# ==================================================

if df.empty:

    st.info(
        "No news available yet. "
        "Click Fetch Latest Headlines to collect news."
    )

    st.stop()


# ==================================================
# DASHBOARD METRICS
# ==================================================

st.divider()

st.subheader("📊 Dashboard Overview")

col1, col2, col3, col4 = st.columns(4)

col1.metric(
    "Total Headlines",
    len(df)
)

col2.metric(
    "OTT Platform",
    int((df["category"] == "OTT Platform").sum())
)

col3.metric(
    "Studio",
    int((df["category"] == "Studio").sum())
)

col4.metric(
    "Other",
    int((df["category"] == "Other").sum())
)

st.divider()


# ==================================================
# SEARCH AND FILTERS
# ==================================================

st.subheader("🔎 Explore News")

left, right = st.columns([2, 1])

with left:

    search = st.text_input(
        "Search Headlines",
        placeholder="Enter a keyword to search..."
    )

with right:

    categories = [
        "All"
    ] + sorted(
        df["category"].dropna().unique().tolist()
    )

    selected_category = st.selectbox(
        "Filter by Category",
        categories
    )

sources = [
    "All"
] + sorted(
    df["source"].dropna().unique().tolist()
)

selected_source = st.selectbox(
    "Filter by News Source",
    sources
)


# ==================================================
# APPLY FILTERS
# ==================================================

filtered = df.copy()

if search:

    filtered = filtered[
        filtered["headline"].str.contains(
            search,
            case=False,
            na=False,
            regex=False
        )
    ]

if selected_category != "All":

    filtered = filtered[
        filtered["category"] == selected_category
    ]

if selected_source != "All":

    filtered = filtered[
        filtered["source"] == selected_source
    ]


# ==================================================
# DISPLAY HEADLINES
# ==================================================

st.divider()

st.subheader(
    f"📰 Latest Headlines ({len(filtered)})"
)

if filtered.empty:

    st.warning(
        "No headlines match your selected filters."
    )

else:

    for _, item in filtered.iterrows():

        headline = html.escape(
            str(item.get("headline", "Untitled"))
        )

        source = html.escape(
            str(item.get("source", "Unknown"))
        )

        published = html.escape(
            str(item.get("published", "Date unavailable"))
        )

        category = html.escape(
            str(item.get("category", "Other"))
        )

        link = str(
            item.get("link", "")
        ).strip()

        if link.startswith(("https://", "http://")):

            safe_link = html.escape(
                link,
                quote=True
            )

            title_html = (
                f'<a href="{safe_link}" target="_blank" '
                f'rel="noopener noreferrer">{headline}</a>'
            )

        else:

            title_html = headline

        st.markdown(
            f"""
            <div class="news-card">
                {title_html}
                <div class="small-muted">
                    {source} | {published} | {category}
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )


# ==================================================
# NEWS ANALYTICS
# ==================================================

st.divider()

st.subheader("📈 News Analytics")

counts = df["category"].value_counts()

if not counts.empty:

    st.bar_chart(counts)

else:

    st.info("No analytics data available.")


# ==================================================
# CSV DOWNLOAD
# ==================================================

st.divider()

st.subheader("📥 Download News Data")

download_col1, download_col2 = st.columns(2)

with download_col1:

    filtered_csv = filtered.to_csv(
        index=False
    ).encode("utf-8-sig")

    st.download_button(
        label="⬇️ Download Filtered News CSV",
        data=filtered_csv,
        file_name="newspulse_filtered_news.csv",
        mime="text/csv",
        use_container_width=True
    )

with download_col2:

    all_csv = df.to_csv(
        index=False
    ).encode("utf-8-sig")

    st.download_button(
        label="⬇️ Download All News CSV",
        data=all_csv,
        file_name="newspulse_all_news.csv",
        mime="text/csv",
        use_container_width=True
    )


# ==================================================
# FOOTER
# ==================================================

st.divider()

st.markdown("""
<div style="
    text-align:center;
    padding:15px;
    color:#94a3b8;
    font-size:13px;
">
    <strong style="color:#60a5fa;">NewsPulse</strong>
    <br>
    Built with Python | Streamlit | BeautifulSoup |
    Requests | Pandas
    <br><br>
    Collecting publicly available RSS news metadata.
    Visit publisher links to read full articles.
</div>
""", unsafe_allow_html=True)
