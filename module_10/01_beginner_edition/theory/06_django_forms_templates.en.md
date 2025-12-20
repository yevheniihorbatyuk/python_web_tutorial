# Lesson 6: Django Forms & Templates

## Introduction: User Interaction

**Forms** handle user input, validation, and processing. **Templates** are responsible for rendering the HTML that the user sees. Together, they allow you to create interactive web pages.

---

## Part 1: Django Forms

Django's form handling uses `Form` classes.

### `ModelForm`

A `ModelForm` is a helper class that lets you create a `Form` class from a Django model. It's a huge time-saver for creating forms that map directly to database models.

```python
# quotes/forms.py
from django import forms
from .models import Quote

class QuoteForm(forms.ModelForm):
    class Meta:
        model = Quote
        fields = ['text', 'author', 'tags']
```
- `model`: The model to base the form on.
- `fields`: The fields from the model to include in the form.

### Using a Form in a View

Here's how you use a `Form` in a view to handle both displaying the form (a `GET` request) and processing the submitted data (a `POST` request).

```python
# quotes/views.py
from .forms import QuoteForm

def add_quote(request):
    if request.method == 'POST':
        # Create a form instance and populate it with data from the request
        form = QuoteForm(request.POST)
        # Check if the form is valid
        if form.is_valid():
            form.save() # Save the new quote to the database
            return redirect('quotes:quote_list')
    else:
        # If a GET request, create a blank form
        form = QuoteForm()
        
    return render(request, 'quotes/add_quote.html', {'form': form})
```

### Form Validation

Validation is automatic for `ModelForm` based on your model definition (e.g., `max_length`). You can also add custom validation methods to your form class.

```python
class MyForm(forms.Form):
    name = forms.CharField()

    def clean_name(self):
        """A custom validation method for a specific field."""
        name = self.cleaned_data['name']
        if len(name) < 3:
            raise forms.ValidationError("Name must be at least 3 characters long.")
        return name
```

---

## Part 2: Django Templates

Templates are text files that can generate any text-based format (HTML, XML, CSV).

### Template Syntax

- **`{{ variable }}`**: Variables are replaced with their value from the context.
- **`{% tag %}`**: Tags provide logic, like loops or conditionals.

### Template Inheritance

This is a powerful feature that allows you to build a base "skeleton" template that contains all the common elements of your site and defines **blocks** that child templates can override.

**`base.html`**
```html
<!DOCTYPE html>
<html>
<head>
    <title>{% block title %}My Site{% endblock %}</title>
</head>
<body>
    <main>
        {% block content %}{% endblock %}
    </main>
</body>
</html>
```

**`quote_list.html`**
```html
{% extends "base.html" %}

{% block title %}List of Quotes{% endblock %}

{% block content %}
    <h1>Quotes</h1>
    ...
{% endblock %}
```

### Rendering a Form in a Template

```html
<form method="post">
    {% csrf_token %}  <!-- Crucial for security! -->
    
    {{ form.as_p }}   <!-- Render form fields as <p> tags -->
    
    <button type="submit">Save</button>
</form>
```
- `{% csrf_token %}`: Protects against Cross-Site Request Forgery attacks. **Always** include it in forms that use `POST`.

### Template Filters

Filters modify variables for display.
- `{{ quote.text|truncatewords:10 }}`: Truncates the text.
- `{{ quote.created_at|date:"F j, Y" }}`: Formats a date.
- `{{ author.name|upper }}`: Converts to uppercase.

---
## Additional Resources

- [Django Forms Documentation](https://docs.djangoproject.com/en/stable/topics/forms/)
- [The Django Template Language](https://docs.djangoproject.com/en/stable/ref/templates/language/)
- [Built-in Template Tags and Filters](https://docs.djangoproject.com/en/stable/ref/templates/builtins/)
