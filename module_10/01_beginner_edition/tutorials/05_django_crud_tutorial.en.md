# Tutorial: Django Views & URLs

This tutorial will guide you through creating views and URL patterns to display the data from your models.

**Goal:** Create a page to list all quotes and a detail page for a single quote.

---

## Step 1: Create a View Function

Let's start with a simple function-based view to display a list of all quotes.

Open `quotes/views.py` and add the following code:
```python
from django.shortcuts import render
from .models import Quote

def quote_list(request):
    """
    This view retrieves all Quote objects from the database
    and passes them to a template.
    """
    quotes = Quote.objects.all()
    return render(request, 'quotes/quote_list.html', {'quotes': quotes})
```

---

## Step 2: Create a Template

Django views need templates to render HTML.

1.  Create the necessary directories:
    ```bash
    mkdir -p quotes/templates/quotes
    ```
2.  Create a new file `quotes/templates/quotes/quote_list.html`:
    ```html
    <!DOCTYPE html>
    <html>
    <head>
        <title>Quotes</title>
    </head>
    <body>
        <h1>Quotes</h1>
        <ul>
            {% for quote in quotes %}
                <li>
                    "{{ quote.text }}" - <em>{{ quote.author.name }}</em>
                </li>
            {% empty %}
                <li>No quotes found.</li>
            {% endfor %}
        </ul>
    </body>
    </html>
    ```
    - `{% for quote in quotes %}`: This is a Django template tag for looping.
    - `{{ quote.text }}`: This is a template variable that displays the data.

---

## Step 3: Configure URLs

Now, we need to connect a URL to our `quote_list` view.

1.  **Create `quotes/urls.py`**:
    ```python
    from django.urls import path
    from . import views

    app_name = 'quotes'

    urlpatterns = [
        path('', views.quote_list, name='quote_list'),
    ]
    ```

2.  **Include the app's URLs in the main project's `urls.py`**:
    ```python
    # config/urls.py
    from django.contrib import admin
    from django.urls import path, include

    urlpatterns = [
        path('admin/', admin.site.urls),
        path('', include('quotes.urls')),
    ]
    ```

---

## Step 4: Test Your List View

1.  **Run the development server:**
    ```bash
    python manage.py runserver
    ```
2.  **Open your browser** and go to `http://127.0.0.1:8000/`.

You should see a page listing all the quotes you have in your database.

---

## Step 5: Create a Detail View and URL

Let's create a page to show the details of a single quote.

1.  **Add the detail view to `quotes/views.py`**:
    ```python
    from django.shortcuts import get_object_or_404

    def quote_detail(request, quote_id):
        quote = get_object_or_404(Quote, pk=quote_id)
        return render(request, 'quotes/quote_detail.html', {'quote': quote})
    ```

2.  **Add the URL pattern to `quotes/urls.py`**:
    ```python
    urlpatterns = [
        path('', views.quote_list, name='quote_list'),
        path('quote/<int:quote_id>/', views.quote_detail, name='quote_detail'),
    ]
    ```

3.  **Create the detail template `quotes/templates/quotes/quote_detail.html`**:
    ```html
    <!DOCTYPE html>
    <html>
    <head>
        <title>Quote Detail</title>
    </head>
    <body>
        <h1>Quote</h1>
        <blockquote>
            <p>"{{ quote.text }}"</p>
            <footer>- {{ quote.author.name }}</footer>
        </blockquote>
        
        <strong>Tags:</strong>
        <ul>
        {% for tag in quote.tags.all %}
            <li>{{ tag.name }}</li>
        {% endfor %}
        </ul>

        <a href="{% url 'quotes:quote_list' %}">Back to list</a>
    </body>
    </html>
    ```
    - `{% url 'quotes:quote_list' %}`: This template tag generates a URL by reversing the URL name, which is more robust than hardcoding URLs.

4.  **Update the list template** to link to the detail page:
    ```html
    <!-- Inside the for loop in quote_list.html -->
    <li>
        <a href="{% url 'quotes:quote_detail' quote.id %}">
            "{{ quote.text }}"
        </a> - <em>{{ quote.author.name }}</em>
    </li>
    ```

Now, go back to the quote list page, and you should be able to click on each quote to see its detail page.
