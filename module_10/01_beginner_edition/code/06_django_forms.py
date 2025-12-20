"""
Урок 6: Django Forms

Цей файл містить робочий приклад Django ModelForm, який використовується
для створення та оновлення об'єктів моделі Quote.
"""
from django import forms
from .models import Quote, Author, Tag

class QuoteForm(forms.ModelForm):
    """
    Форма для створення та редагування цитат.
    Автоматично генерується на основі моделі Quote.
    """
    class Meta:
        model = Quote
        fields = ['text', 'author', 'tags']
        
        # Додаємо CSS класи для кращого вигляду з Bootstrap
        widgets = {
            'text': forms.Textarea(attrs={'class': 'form-control', 'rows': 5}),
            'author': forms.Select(attrs={'class': 'form-control'}),
            'tags': forms.SelectMultiple(attrs={'class': 'form-control'}),
        }

class AuthorForm(forms.ModelForm):
    """Форма для створення та редагування авторів."""
    class Meta:
        model = Author
        fields = ['name', 'born_date', 'born_location', 'description']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'born_date': forms.TextInput(attrs={'class': 'form-control'}),
            'born_location': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 5}),
        }
