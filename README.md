# web-scraping

## Basic Willhaben Marketplace Scraper

`willhaben_scraper.py`

### Overview

This script performs a basic scrape of Willhaben marketplace search results using **Selenium (Chrome)** and **BeautifulSoup**.  
It loads JavaScript-rendered pages, extracts listing titles and URLs, automatically navigates through result pages, de-duplicates entries, and writes the results to **JSON and CSV** files.

---

### What it does

- Opens a Willhaben marketplace search page in a real browser (headless Chrome)
- Waits for dynamic content to finish rendering
- Extracts listings by analyzing link structure instead of fragile CSS class names
- Automatically paginates through search results
- De-duplicates listings by URL
- Exports structured data to:
  - JSON
  - CSV

---

### Output

After execution, the script generates:

- `willhaben_yugioh.json`  
  A JSON array of listing objects:
  ```json
  { "title": "...", "url": "..." }
  ```

- `willhaben_yugioh.csv`  
  A CSV file with columns:
  - `title`
  - `url`

---

### How to run

1. Install Python dependencies (I recommend creating a virtual environment first):
   ```bash
   pip install selenium beautifulsoup4
   ```

2. Install **Google Chrome**

3. Install **ChromeDriver**
   - Must match your installed Chrome version
   - Must be available on your system `PATH`

### Execution

Run the script normally:
```bash
python scrape_willhaben.py
```

---

### What to watch out for

**ChromeDriver compatibility**
- ChromeDriver must match your Chrome version, else it will cause Chrome to fail on startup.

**Headless mode**
- Some websites behave differently in headless mode.
- If content does not load correctly, disable headless mode:
  ```python
  HEADLESS = False
  ```

**Pagination behavior**
- Pagination relies on detecting common “next page” controls.
- If Willhaben changes its pagination UI, scraping may stop after the first page.

**Selector drift**
- The script avoids auto-generated CSS classes.
- It still depends on:
  - semantic attributes (`aria-label`, `rel="next"`)
  - URL structure heuristics
- DOM or routing changes may require selector updates.

**Anti-bot measures**
- Rapid or repeated execution may trigger blocking.
- Respect `POLITE_DELAY_SEC` and avoid aggressive scraping.

---

### Where to change things

Update the search term by modifying:
```python
START_URL = "https://www.willhaben.at/iad/kaufen-und-verkaufen/marktplatz?keyword=Windsurfboard"
```

Replace `Windsurfboard` with your desired keyword  
(URL-encode spaces as `%20`).


---

**Output filenames**

```python
write_json(listings, "willhaben_yugioh.json")
write_csv(listings, "willhaben_yugioh.csv")
```
