# Lesson 1: Beautiful Soup Web Scraping Concepts

## Introduction: Why Web Scraping?

Web scraping is the automated process of extracting data from websites. It's a powerful technique for gathering information for price monitoring, news aggregation, market research, and much more.

**The Problem:** Data on the web is embedded in complex HTML. Manually copying this data is slow and inefficient.

**The Solution:** We use libraries like **Beautiful Soup** to parse the HTML and extract the exact data we need, programmatically.

---

## Part 1: HTML & CSS Selectors Fundamentals

To scrape a website, you need to understand its structure.

### HTML as a Tree

Every HTML document is a nested tree of tags.

```html
<div class="quote">
    <span class="text">"The world as we have created it..."</span>
    by <small class="author">Albert Einstein</small>
</div>
```

- **Tags:** `<div>`, `<span>`, `<small>`
- **Attributes:** `class="quote"`, `class="text"`
- **Content:** The text inside the tags.

### Finding Elements with CSS Selectors

CSS selectors are patterns used to select elements.

- `div`: Selects all `<div>` tags.
- `.quote`: Selects all tags with `class="quote"`.
- `div.quote`: Selects `<div>` tags that have `class="quote"`.
- `span.text`: Selects `<span>` tags with `class="text"`.

---

## Part 2: The Scraping Process

The process involves two main libraries:

1.  **Requests**: To download the HTML content of a web page.
2.  **Beautiful Soup**: To parse the HTML and find the data.

### Step-by-Step Workflow

1.  **Install libraries**: `pip install requests beautifulsoup4`
2.  **Fetch the page**: Use `requests.get(url)` to get the HTML.
3.  **Create a Soup object**: `soup = BeautifulSoup(html_content, 'html.parser')`
4.  **Find elements**: Use `soup.find()` or `soup.find_all()` with CSS selectors.
5.  **Extract data**: Get text with `.get_text()` or attribute values with `['attribute_name']`.

---

## Part 3: Key Beautiful Soup Methods

- **`soup.find('tag', class_='name')`**: Finds the *first* matching element.
- **`soup.find_all('tag', class_='name')`**: Finds *all* matching elements and returns them as a list.
- **`element.get_text()`**: Extracts the text content from an element.
- **`element.get('href')`**: Extracts the value of an attribute (e.g., the URL from a link).

---

## Part 4: Scraping Ethics

- **Check `robots.txt`**: Always check `website.com/robots.txt` to see which parts of the site you are allowed to scrape.
- **Be respectful**: Don't send too many requests in a short period. Add delays (`time.sleep()`) between requests.
- **Identify yourself**: Set a `User-Agent` in your request headers to identify your script.

---
## Additional Resources

- [Beautiful Soup Official Documentation](https://www.crummy.com/software/BeautifulSoup/bs4/doc/)
- [Requests Library Documentation](https://requests.readthedocs.io/en/latest/)
- [W3Schools CSS Selectors Reference](https://www.w3schools.com/cssref/css_selectors.php)
