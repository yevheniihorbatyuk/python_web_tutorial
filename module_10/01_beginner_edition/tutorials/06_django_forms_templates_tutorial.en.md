# Tutorial: Django Forms & Templates

This tutorial will guide you through creating a form to add new quotes and the templates needed to display it.

**Goal:** Create a page with a form for adding new quotes and integrate it into the project.

---

## Step 1: Create a Form Class

First, we need to create a `ModelForm` for our `Quote` model.

Create a new file `quotes/forms.py` and add the following:
```python
from django import forms
from .models import Quote

class QuoteForm(forms.ModelForm):
    class Meta:
        model = Quote
        fields = ['text', 'author', 'tags']
        # Add widgets to apply Bootstrap classes to the form fields
        widgets = {
            'text': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'author': forms.Select(attrs={'class': 'form-control'}),
            'tags': forms.SelectMultiple(attrs={'class': 'form-control'}),
        }
```

---

## Step 2: Create the View

Now, create a view to handle the form.

Open `quotes/views.py` and add the `add_quote` view:
```python
from django.shortcuts import render, redirect
from .forms import QuoteForm

# ... (your existing views) ...

def add_quote(request):
    if request.method == 'POST':
        form = QuoteForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect(to='quotes:quote_list')
    else:
        form = QuoteForm()
    
    return render(request, 'quotes/add_quote.html', {'form': form})
```

---

## Step 3: Add the URL

Add a URL pattern for the new view in `quotes/urls.py`:
```python
urlpatterns = [
    path('', views.quote_list, name='quote_list'),
    path('quote/<int:quote_id>/', views.quote_detail, name='quote_detail'),
    path('add/', views.add_quote, name='add_quote'), # <-- Add this line
]
```

---

## Step 4: Create the Templates

We need a base template and a template for our form.

1.  **Create `quotes/templates/quotes/base.html`**:
    ```html
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>{% block title %}Quote App{% endblock %}</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    </head>
    <body>
        <div class="container mt-4">
            <nav class="navbar navbar-expand-lg navbar-light bg-light mb-4">
                <a class="navbar-brand" href="{% url 'quotes:quote_list' %}">QuoteApp</a>
                <a class="nav-link" href="{% url 'quotes:add_quote' %}">Add Quote</a>
            </nav>
            {% block content %}{% endblock %}
        </div>
    </body>
    </html>
    ```

2.  **Create `quotes/templates/quotes/add_quote.html`**:
    ```html
    {% extends 'quotes/base.html' %}

    {% block title %}Add Quote{% endblock %}

    {% block content %}
        <h1 class="mb-4">Add a New Quote</h1>
        <form method="post">
            {% csrf_token %}
            
            <div class="mb-3">
                <label class="form-label">Quote Text</label>
                {{ form.text }}
            </div>
            <div class="mb-3">
                <label class="form-label">Author</label>
                {{ form.author }}
            </div>
            <div class="mb-3">
                <label class="form-label">Tags</label>
                {{ form.tags }}
            </div>
            
            <button type="submit" class="btn btn-primary">Save Quote</button>
        </form>
    {% endblock %}
    ```

3.  **Update `quote_list.html`** to extend the base template:
    ```html
    {% extends 'quotes/base.html' %}

    {% block title %}Quotes{% endblock %}

    {% block content %}
        <h1>Quotes</h1>
        ... (the rest of your list template) ...
    {% endblock %}
    ```

---

## Step 5: Test the Form

1.  Run the server: `python manage.py runserver`.
2.  Go to `http://127.0.0.1:8000/add/`.
3.  You should see a form to add a new quote.
4.  Fill out the form and submit it. If successful, you should be redirected to the quote list, and your new quote should appear.

You have now successfully created a full CRUD (Create, Read) cycle for your quotes! The same principles apply for building Update and Delete functionality.
