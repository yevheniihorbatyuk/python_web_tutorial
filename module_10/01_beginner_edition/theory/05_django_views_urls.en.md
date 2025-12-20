# Lesson 5: Django Views & URLs

## Introduction: Connecting URLs to Logic

A **View** is a Python function or class that takes a web request and returns a web response. A **URL** maps a specific URL path to a view.

**The Request-Response Cycle:**
1.  A user navigates to a URL (e.g., `/quotes/`).
2.  Django's URL dispatcher checks your `urls.py` files to find a matching pattern.
3.  The corresponding view function is called, receiving the request details.
4.  The view performs some logic (e.g., fetches data from the database).
5.  The view returns a response, often by rendering an HTML template.

---

## Part 1: Function-Based Views (FBVs)

An FBV is a simple Python function that takes `request` as its first argument.

```python
# quotes/views.py
from django.shortcuts import render
from .models import Quote

def quote_list(request):
    """A view to display all quotes."""
    quotes = Quote.objects.all()
    context = {'quotes': quotes}
    return render(request, 'quotes/quote_list.html', context)
```
- `render()`: A shortcut function that combines a template with a context dictionary and returns an `HttpResponse` object.

---

## Part 2: URL Routing

You need to map a URL to your view. This is done in `urls.py`.

1.  **Project `urls.py` (`config/urls.py`)**: This is the root URLconf. It's best to include the URLs from your app.
    ```python
    from django.urls import path, include

    urlpatterns = [
        path('admin/', admin.site.urls),
        path('', include('quotes.urls')), # Include your app's URLs
    ]
    ```

2.  **App `urls.py` (`quotes/urls.py`)**: Create this file to hold your app-specific URLs.
    ```python
    from django.urls import path
    from . import views

    app_name = 'quotes' # Namespace for URLs

    urlpatterns = [
        path('', views.quote_list, name='quote_list'),
        # Example with a parameter:
        # path('author/<int:author_id>/', views.author_detail, name='author_detail'),
    ]
    ```
- `name='quote_list'`: Naming your URL lets you refer to it unambiguously from elsewhere in Django, especially templates.

---

## Part 3: Dynamic URLs

Often, you need URLs that capture a value from the path.

```python
# quotes/urls.py
path('quote/<int:quote_id>/', views.quote_detail, name='quote_detail'),

# quotes/views.py
from django.shortcuts import get_object_or_404

def quote_detail(request, quote_id):
    quote = get_object_or_404(Quote, pk=quote_id)
    return render(request, 'quotes/quote_detail.html', {'quote': quote})
```
- `<int:quote_id>`: This is a path converter. It matches an integer and passes its value to the view as the `quote_id` argument.
- `get_object_or_404()`: A common shortcut to get an object or raise a 404 (Not Found) error if it doesn't exist.

---

## Part 4: Class-Based Views (CBVs)

For common patterns like displaying a list of objects or a detail page, Django provides generic **Class-Based Views**. They save you from writing repetitive code.

### `ListView`

Displays a list of objects.

```python
# quotes/views.py
from django.views.generic import ListView
from .models import Quote

class QuoteListView(ListView):
    model = Quote
    template_name = 'quotes/quote_list.html' # Optional, defaults to quotes/quote_list.html
    context_object_name = 'quotes'           # Name of the list in the template context
    paginate_by = 10                         # Optional: enable pagination
```

### `DetailView`

Displays a single object.

```python
# quotes/views.py
from django.views.generic import DetailView

class QuoteDetailView(DetailView):
    model = Quote
    template_name = 'quotes/quote_detail.html'
    context_object_name = 'quote'
```

### Using CBVs in `urls.py`

You must call the `.as_view()` method.

```python
# quotes/urls.py
from .views import QuoteListView, QuoteDetailView

urlpatterns = [
    path('', QuoteListView.as_view(), name='quote_list'),
    path('quote/<int:pk>/', QuoteDetailView.as_view(), name='quote_detail'),
]
```
- Note that `DetailView` expects the captured URL parameter to be named `pk` (Primary Key) by default.

---
## Additional Resources

- [Django Views Documentation](https://docs.djangoproject.com/en/stable/topics/http/views/)
- [URL Dispatcher Documentation](https://docs.djangoproject.com/en/stable/topics/http/urls/)
- [Built-in Class-Based Generic Views](https://docs.djangoproject.com/en/stable/ref/class-based-views/)
