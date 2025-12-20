# Tutorial: Your First Scraper with Beautiful Soup

This tutorial will guide you through creating a simple but functional web scraper. We will scrape quotes from [quotes.toscrape.com](http://quotes.toscrape.com).

**Goal:** Extract the text, author, and tags for each quote on the first page.

---

## Step 1: Setup

Make sure you have the necessary libraries installed. If not, open your terminal and run:
```bash
pip install requests beautifulsoup4
```

---

## Step 2: Fetch the Web Page

Create a Python file (e.g., `scraper.py`) and add the following code to download the page content.

```python
import requests

url = "http://quotes.toscrape.com"
try:
    response = requests.get(url)
    response.raise_for_status()  # Raise an exception for bad status codes (4xx or 5xx)
    html_content = response.text
    print("Page downloaded successfully!")
except requests.RequestException as e:
    print(f"Error downloading page: {e}")
    html_content = None
```

---

## Step 3: Parse HTML with Beautiful Soup

Now, let's parse the downloaded HTML.

```python
from bs4 import BeautifulSoup

# Assuming html_content is available from the previous step
if html_content:
    soup = BeautifulSoup(html_content, 'html.parser')
    print("HTML parsed successfully!")
```

---

## Step 4: Find the Quotes

Inspect the website's HTML. You'll notice each quote is contained within a `<div class="quote">`. We can use this to find all quotes.

```python
# ... inside the `if html_content:` block
quotes = soup.find_all('div', class_='quote')
print(f"Found {len(quotes)} quotes on the page.")
```

---

## Step 5: Extract Data from Each Quote

Now, loop through the `quotes` list and extract the text, author, and tags from each one.

```python
# ... inside the `if html_content:` block
all_quotes_data = []
for quote in quotes:
    # Extract text
    text = quote.find('span', class_='text').get_text(strip=True)
    
    # Extract author
    author = quote.find('small', class_='author').get_text(strip=True)
    
    # Extract tags
    tags_div = quote.find('div', class_='tags')
    tags = [tag.get_text(strip=True) for tag in tags_div.find_all('a', class_='tag')]
    
    all_quotes_data.append({
        'text': text,
        'author': author,
        'tags': tags
    })

# Print the first quote to verify
if all_quotes_data:
    import json
    print("\nFirst quote extracted:")
    print(json.dumps(all_quotes_data[0], indent=2))
```

---

## Step 6: Putting It All Together

Here is the complete, runnable script.

```python
import requests
from bs4 import BeautifulSoup
import json

def scrape_quotes():
    """
    Scrapes quotes from the first page of quotes.toscrape.com.
    Returns a list of dictionaries, where each dictionary represents a quote.
    """
    url = "http://quotes.toscrape.com"
    
    try:
        response = requests.get(url)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"Error downloading page: {e}")
        return []

    soup = BeautifulSoup(response.text, 'html.parser')
    quotes = soup.find_all('div', class_='quote')
    
    if not quotes:
        print("No quotes found. The website structure might have changed.")
        return []
        
    all_quotes_data = []
    for quote in quotes:
        try:
            text = quote.find('span', class_='text').get_text(strip=True)
            author = quote.find('small', class_='author').get_text(strip=True)
            tags_div = quote.find('div', class_='tags')
            tags = [tag.get_text(strip=True) for tag in tags_div.find_all('a', class_='tag')]
            
            all_quotes_data.append({
                'text': text,
                'author': author,
                'tags': tags
            })
        except AttributeError:
            # Skip a quote if its structure is unexpected
            print("Warning: Could not parse a quote. Skipping.")
            continue
            
    return all_quotes_data

if __name__ == '__main__':
    scraped_data = scrape_quotes()
    if scraped_data:
        print(f"Successfully scraped {len(scraped_data)} quotes.")
        
        # Save to a JSON file
        with open('quotes.json', 'w', encoding='utf-8') as f:
            json.dump(scraped_data, f, indent=2, ensure_ascii=False)
        print("Data saved to quotes.json")
```

Now, run your `scraper.py` file. It will print the number of scraped quotes and save them to a `quotes.json` file in the same directory. Congratulations, you've built your first web scraper!
