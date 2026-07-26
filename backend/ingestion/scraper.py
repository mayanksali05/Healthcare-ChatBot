import time
import threading

import requests
from bs4 import BeautifulSoup

from ingestion.cleaner import clean_text


# Several of the curated sources (Healthline, Medical News Today, Harvard,
# Sleep Foundation) reject the default "python-requests/x.y" agent with a 403,
# so we identify as a normal browser. No credentials or API keys are sent -
# every source in the registry is public, unauthenticated content.
DEFAULT_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
}

REQUEST_TIMEOUT = 25

MAX_ATTEMPTS = 3

RETRY_BACKOFF = 2

# Transient server / rate-limit responses worth a retry. 4xx client errors
# (404, 410) are permanent for our purposes and fail immediately.
RETRY_STATUS = {429, 500, 502, 503, 504}


def build_session():

    session = requests.Session()

    session.headers.update(DEFAULT_HEADERS)

    return session


# requests.Session is not thread safe, so each ingest worker thread gets its
# own. Reusing a session per thread still keeps connections pooled.
_local = threading.local()


def get_session():

    if not hasattr(_local, "session"):

        _local.session = build_session()

    return _local.session


def fetch_html(url, session=None):

    client = session or get_session()

    last_error = None

    for attempt in range(1, MAX_ATTEMPTS + 1):

        try:

            response = client.get(
                url,
                timeout=REQUEST_TIMEOUT,
                headers=DEFAULT_HEADERS,
                # verify stays at the default (True) so TLS certificates are
                # always validated - never disable this to work around a
                # failing source.
            )

            if response.status_code in RETRY_STATUS:

                last_error = f"HTTP {response.status_code}"

            else:

                response.raise_for_status()

                return response.text

        except requests.RequestException as error:

            last_error = str(error)

        if attempt < MAX_ATTEMPTS:

            time.sleep(RETRY_BACKOFF * attempt)

    raise RuntimeError(f"Failed to fetch after {MAX_ATTEMPTS} attempts: {last_error}")


def extract_text(html):

    soup = BeautifulSoup(html, "html.parser")

    # Drop non-article furniture before reading paragraphs
    for tag in soup(["script", "style", "noscript", "nav", "header", "footer", "aside"]):

        tag.decompose()

    # Get page title
    title = soup.title.text.strip() if soup.title else ""

    # Get paragraph text
    article = soup.find("article")

    if article:
        paragraphs = article.find_all("p")
    else:
        paragraphs = soup.find_all("p")

    content = " ".join([
        p.get_text(" ", strip=True)
        for p in paragraphs
    ])

    content = clean_text(content)

    return {
        "title": title,
        "content": content
    }


def scrape_article(url, session=None):

    html = fetch_html(url, session=session)

    return extract_text(html)


if __name__ == "__main__":

    url = "https://www.healthline.com/nutrition/11-proven-benefits-of-bananas"

    article = scrape_article(url)

    print("\nTITLE:\n")
    print(article["title"])

    print(f"\nCONTENT LENGTH: {len(article['content'])}")

    print("\nCONTENT SAMPLE:\n")
    print(article["content"][:2000])
