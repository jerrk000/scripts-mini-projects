# Repository Overview

This repo contains many little projects (mostly single file scripts) that are worth saving and re-using, but do not deserve an individual repo. This `README.md` explains the content of each folder and how each script is used.

# `web-scraping\` Folder

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

### What to watch out for and what may break in the future

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
# `whatsapp_text_analysis\` Folder

## WhatsApp Chat Analysis Script

`whatsapp_text_analysis.py`

## Overview

This script analyzes an exported WhatsApp chat text file and computes conversational metrics such as:
- message counts per person
- average message length
- average response time
- longest inactivity period
- response-time distributions
- activity by hour of day

It is designed for one-on-one WhatsApp chats exported as a `.txt` file and produces both **console output** and **matplotlib visualizations**.

---

## How to use

### 1. WhatsApp chat export

You must have a WhatsApp chat exported as a **plain text file**.

**How to export (mobile):**
- Open the chat in WhatsApp
- Tap the contact/group name
- Choose **Export chat**
- Export **without media**
- Transfer the resulting `.txt` file to your project directory
- The file must be in the **same directory** as the script
- Encoding must be **UTF-8**

If your file has a different name, update this line in the script:

```python
with open("WhatsApp-Chat_with_person.txt", "r", encoding="utf-8") as f:
```

---

### 2. Supported chat format (important)

The script assumes the WhatsApp export uses this line format:

```text
DD.MM.YY, HH:MM - Sender Name: Message text
```

Example:
```text
12.03.23, 18:42 - Alice: Hey, are you coming later?
```

This format is enforced by the regular expression:

```python
pattern = re.compile(
    r"^(\d{1,2}\.\d{1,2}\.\d{2,4}), (\d{1,2}:\d{2}) - (.*?): (.*)"
)
```

If your WhatsApp export uses a different date/time or separator format, you must adapt the regex and datetime parsing.

---

## Dependencies

Install required Python packages:

```bash
pip install pandas matplotlib numpy
```

---

## What the script does

1. Loads the WhatsApp chat file
2. Parses messages using a regex (supports multi-line messages)
3. Builds a pandas DataFrame with timestamps, sender, and message text
4. Computes metrics
6. Produces visualizations

---

## Output

### Console output
- Number of messages per person
- Average message length per person
- Average response time (minutes)
- Longest period without messages
- Sender and timestamp before the longest gap

### Visual output
- Histogram of response times per person
- Messages per hour of day per person

---

## Where to change things

### Input file
```python
with open("WhatsApp-Chat_with_person.txt", "r", encoding="utf-8") as f:
```


---


## Limitations

- Designed for one-on-one chats (group chats may distort response-time logic)
- Assumes a specific WhatsApp export format
- Media messages are treated as plain text
- No timezone normalization

---
# `instagram_follower_comparison\` Folder

## Instagram Followers vs Following Comparison Script

`compare_following_follower.py`

## Overview

This script compares **Instagram followers and followings** using the HTML files exported from Instagram.  
It extracts usernames from the exported HTML files and identifies:

- people who **follow you but you do not follow back**
- people you **follow but who do not follow you back**

The results are printed to the console in human-readable format.

---

## Prerequisites

### 1. Instagram data export

You must download your Instagram account data from Meta.

**How to download:**
1. Instagram -> Settings
2. Accounts Center -> Your information and permissions
3. Download your information
4. Request download (HTML format)
5. Extract the archive

You should find files similar to:

```text
followers_1.html
following.html
```

---

### 2. File locations

The script expects these files to be located in the **same directory** as the script:

```python
followers_file = "followers_1.html"
followings_file = "following.html"
```

Update these paths if your files differ.

---

### 3. Supported HTML structure

The script assumes usernames appear as text inside `<a>` tags:

```html
<a href="https://www.instagram.com/username/">username</a>
```

If Instagram changes the export format, the extraction logic must be adapted.

---

## Dependencies

Install required Python packages:

```bash
pip install beautifulsoup4
```

---

## What the script does

1. Reads the followers and following HTML files
2. Parses them using BeautifulSoup
3. Extracts usernames from all `<a>` tags
4. Compares followers vs followings
5. Prints:
   - total follower count
   - total following count
   - users not followed back
   - users not following back

---

## Output

### Console output

- Number of followers
- Number of followings
- Numbered lists for:
  - Followers you don’t follow back
  - Followings that don’t follow you back

---

## Where to change things

### Input files

```python
followers_file = "followers_1.html"
followings_file = "following.html"
```

---


