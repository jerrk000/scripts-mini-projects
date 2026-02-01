import csv
import json
import re
import time
from dataclasses import dataclass, asdict
from urllib.parse import urljoin, urlparse

from bs4 import BeautifulSoup

from selenium import webdriver
from selenium.common.exceptions import TimeoutException, StaleElementReferenceException, ElementClickInterceptedException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Probably also works for EBAY, but didnt test it yet. Only Willhaben for now
START_URL = "https://www.willhaben.at/iad/kaufen-und-verkaufen/marktplatz?keyword=Windsurfboard"

# ---- Tuning  ----
MAX_PAGES = 30              # hard stop to avoid infinite loops
POLITE_DELAY_SEC = 1.0      # small delay between pages (be polite)
WAIT_SEC = 15               # render / navigation timeout
HEADLESS = True

# ---- Selectors ----
# Use stable attributes if available (data-testid/aria-label/rel etc.)
# If these do not match the site, you can adjsut here.
SELECTORS = {
    # A selector that indicates the results area is present (used for waits)
    "results_ready_css": "main, body",

    # Pagination "next" button candidates (try in order)
    "next_button_css_candidates": [
        'a[rel="next"]',
        'button[aria-label*="Weiter" i]',
        'a[aria-label*="Weiter" i]',
        'button[aria-label*="Next" i]',
        'a[aria-label*="Next" i]',
    ],
}

# Listing URL heuristic: listing pages usually contain "/iad/" and an ID-ish segment.
LISTING_HREF_RE = re.compile(r"/iad/.*\d+")


@dataclass
class Listing:
    title: str
    url: str


def make_driver() -> webdriver.Chrome:
    opts = webdriver.ChromeOptions()
    if HEADLESS:
        # "new" headless behaves closer to real Chrome in recent versions
        opts.add_argument("--headless=new")
    opts.add_argument("--no-sandbox")
    opts.add_argument("--disable-dev-shm-usage")
    # Optional: reduce easy headless fingerprinting
    opts.add_argument("--disable-blink-features=AutomationControlled")
    opts.add_argument("--window-size=1365,768")

    driver = webdriver.Chrome(options=opts)
    driver.set_page_load_timeout(WAIT_SEC)
    return driver


def wait_until_ready(driver: webdriver.Chrome) -> None:
    WebDriverWait(driver, WAIT_SEC).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, SELECTORS["results_ready_css"]))
    )


def extract_listings_from_html(html: str, base_url: str) -> list[Listing]:
    soup = BeautifulSoup(html, "html.parser")

    # Heuristic: gather candidate anchors that look like listing links.
    # Then derive title from:
    # 1) anchor text
    # 2) nearby heading
    candidates: list[Listing] = []
    seen_urls: set[str] = set()

    for a in soup.find_all("a", href=True):
        href = a["href"]
        if not href.startswith("/"):
            continue
        if not LISTING_HREF_RE.search(href):
            continue

        full_url = urljoin(base_url, href)
        if full_url in seen_urls:
            continue

        text = " ".join(a.get_text(" ", strip=True).split())
        title = text

        # If anchor text is empty/short, try to find a nearby heading
        if not title or len(title) < 5:
            h = a.find(["h1", "h2", "h3"])
            if h:
                title = " ".join(h.get_text(" ", strip=True).split())

        # Still empty? skip
        if not title:
            continue

        seen_urls.add(full_url)
        candidates.append(Listing(title=title, url=full_url))

    return candidates


def find_next_button(driver: webdriver.Chrome):
    for css in SELECTORS["next_button_css_candidates"]:
        els = driver.find_elements(By.CSS_SELECTOR, css)
        if not els:
            continue
        # prefer visible+enabled element
        for el in els:
            if el.is_displayed() and el.is_enabled():
                return el
    return None


def click_next(driver: webdriver.Chrome) -> bool:
    """
    Returns True if it likely navigated to the next page, False if no next button.
    """
    btn = find_next_button(driver)
    if not btn:
        return False

    try:
        # Try native click first
        btn.click()
    except (ElementClickInterceptedException, StaleElementReferenceException):
        # Fallback to JS click
        driver.execute_script("arguments[0].click();", btn)

    return True


def current_url_key(url: str) -> str:
    """
    A simplified key of URL to detect page changes.
    """
    p = urlparse(url)
    return f"{p.scheme}://{p.netloc}{p.path}?{p.query}"


def scrape(start_url: str) -> list[Listing]:
    driver = make_driver()
    all_listings: dict[str, Listing] = {}  # keyed by url to dedupe

    try:
        driver.get(start_url)
        wait_until_ready(driver)

        prev_page_key = None

        for page in range(1, MAX_PAGES + 1):
            html = driver.page_source
            page_listings = extract_listings_from_html(html, base_url=start_url)

            for lst in page_listings:
                all_listings.setdefault(lst.url, lst)

            print(f"[page {page}] total unique listings: {len(all_listings)}")

            # Detect if we are stuck
            page_key = current_url_key(driver.current_url)
            if prev_page_key == page_key and page > 1:
                # If URL does not change, still may be client-side pagination.
                # We will use a content hash check: store a snippet.
                pass
            prev_page_key = page_key

            time.sleep(POLITE_DELAY_SEC)

            # Try paginate
            if not click_next(driver):
                print("No next button found; stopping.")
                break

            # Wait for navigation or content refresh
            try:
                WebDriverWait(driver, WAIT_SEC).until(
                    lambda d: current_url_key(d.current_url) != page_key
                    or d.execute_script("return document.readyState") == "complete"
                )
                wait_until_ready(driver)
            except TimeoutException:
                # If "Next" exists but page didn’t change, stop to avoid infinite loop.
                print("Timed out waiting for next page; stopping.")
                break

    finally:
        driver.quit()

    return list(all_listings.values())


def write_json(listings: list[Listing], path: str) -> None:
    with open(path, "w", encoding="utf-8") as f:
        json.dump([asdict(x) for x in listings], f, ensure_ascii=False, indent=2)


def write_csv(listings: list[Listing], path: str) -> None:
    with open(path, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["title", "url"])
        w.writeheader()
        for x in listings:
            w.writerow(asdict(x))


if __name__ == "__main__":
    listings = scrape(START_URL)
    write_json(listings, "willhaben_windsurf.json")
    write_csv(listings, "willhaben_windsurf.csv")
    print("Wrote willhaben_windsurf.json and willhaben_windsurf.csv")
