"""
Урок 5: Django Views для CRUD операцій

Цей файл містить робочі приклади Django views, які реалізують
Create, Read, Update, Delete (CRUD) операції для моделі Quote.
"""
from django.shortcuts import render, redirect, get_object_or_404
from .models import Quote
from .forms import QuoteForm

def quote_list(request):
    """
    (Read) Відображає список усіх цитат.
    """
    quotes = Quote.objects.select_related('author').prefetch_related('tags').all()
    return render(request, 'quotes/quote_list.html', {'quotes': quotes})

def quote_detail(request, quote_id):
    """
    (Read) Відображає одну цитату за її ID.
    """
    quote = get_object_or_404(Quote, pk=quote_id)
    return render(request, 'quotes/quote_detail.html', {'quote': quote})

def add_quote(request):
    """
    (Create) Створює нову цитату на основі даних з форми.
    """
    if request.method == 'POST':
        form = QuoteForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect(to='quotes:quote_list')
    else:
        form = QuoteForm()
    
    return render(request, 'quotes/add_quote.html', {'form': form})

def edit_quote(request, quote_id):
    """
    (Update) Редагує існуючу цитату.
    """
    quote = get_object_or_404(Quote, pk=quote_id)
    if request.method == 'POST':
        form = QuoteForm(request.POST, instance=quote)
        if form.is_valid():
            form.save()
            return redirect(to='quotes:quote_list')
    else:
        form = QuoteForm(instance=quote)
        
    return render(request, 'quotes/edit_quote.html', {'form': form, 'quote': quote})

def delete_quote(request, quote_id):
    """
    (Delete) Видаляє цитату.
    """
    quote = get_object_or_404(Quote, pk=quote_id)
    if request.method == 'POST':
        quote.delete()
        return redirect(to='quotes:quote_list')
        
    return render(request, 'quotes/delete_quote.html', {'quote': quote})
