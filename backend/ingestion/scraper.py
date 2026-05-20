import requests
from bs4 import BeautifulSoup
from ingestion.cleaner import clean_text

def scrape_article(url):

    response = requests.get(url)

    soup = BeautifulSoup(response.text, "html.parser")

    # Get page title
    title = soup.title.text.strip()

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


if __name__ == "__main__":

    url = "https://www.healthline.com/nutrition/11-proven-benefits-of-bananas"

    article = scrape_article(url)

    print("\nTITLE:\n")
    print(article["title"])

    print("\nCONTENT SAMPLE:\n")
    print(article["content"][:5000])