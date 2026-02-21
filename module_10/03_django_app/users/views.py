"""
User management views.

CRUD views for Country, City, and User models.
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.views import generic
from django.urls import reverse_lazy
from django.contrib import messages
from django.db.models import Q, Count
from django.core.paginator import Paginator

from .models import Country, City, User
from .forms import CountryForm, CityForm, UserForm, UserSearchForm


# ============================================================================
# COUNTRY VIEWS
# ============================================================================

class CountryListView(generic.ListView):
    """List all countries."""

    model = Country
    template_name = 'users/country_list.html'
    context_object_name = 'countries'
    paginate_by = 20

    def get_queryset(self):
        """Get countries with city count annotation.

        annotate(city_count=...) → один SQL з COUNT замість N окремих запитів.
        prefetch_related('city_set') → якщо шаблон звертається до city_set,
        Django виконає 1 окремий SELECT IN (...) замість N запитів (N+1 fix).
        """
        return Country.objects.prefetch_related('city_set').annotate(
            city_count=Count('city')
        ).order_by('name')

    def get_context_data(self, **kwargs):
        """Add extra context."""
        context = super().get_context_data(**kwargs)
        context['total_count'] = Country.objects.count()
        return context


class CountryDetailView(generic.DetailView):
    """Display single country with its cities."""

    model = Country
    template_name = 'users/country_detail.html'
    context_object_name = 'country'

    def get_context_data(self, **kwargs):
        """Add related cities to context."""
        context = super().get_context_data(**kwargs)
        # prefetch_related уникає N+1: без нього кожне місто у шаблоні → окремий SELECT.
        # .all().order_by() безпечно — Django виконає один запит з ORDER BY.
        # Альтернатива: оголосити queryset = Country.objects.prefetch_related('city_set')
        # на рівні класу, тоді Django prefetch автоматично.
        context['cities'] = self.object.city_set.all().order_by('name')
        context['user_count'] = self.object.user_count()
        return context


class CountryCreateView(generic.CreateView):
    """Create new country."""

    model = Country
    form_class = CountryForm
    template_name = 'users/country_form.html'
    success_url = reverse_lazy('users:country-list')

    def form_valid(self, form):
        """Handle successful form submission."""
        response = super().form_valid(form)
        messages.success(
            self.request,
            f'Country "{self.object.name}" created successfully!'
        )
        return response

    def get_context_data(self, **kwargs):
        """Add title to context."""
        context = super().get_context_data(**kwargs)
        context['title'] = 'Create Country'
        return context


class CountryUpdateView(generic.UpdateView):
    """Update existing country."""

    model = Country
    form_class = CountryForm
    template_name = 'users/country_form.html'

    def get_success_url(self):
        """Redirect to country detail after update."""
        return reverse_lazy('users:country-detail', kwargs={'pk': self.object.pk})

    def form_valid(self, form):
        """Handle successful form submission."""
        response = super().form_valid(form)
        messages.success(
            self.request,
            f'Country "{self.object.name}" updated successfully!'
        )
        return response

    def get_context_data(self, **kwargs):
        """Add title to context."""
        context = super().get_context_data(**kwargs)
        context['title'] = 'Edit Country'
        return context


class CountryDeleteView(generic.DeleteView):
    """Delete country and associated cities/users."""

    model = Country
    template_name = 'users/country_confirm_delete.html'
    success_url = reverse_lazy('users:country-list')

    def delete(self, request, *args, **kwargs):
        """Delete and show message."""
        country = self.get_object()
        messages.success(
            request,
            f'Country "{country.name}" deleted along with {country.city_set.count()} cities!'
        )
        return super().delete(request, *args, **kwargs)


# ============================================================================
# CITY VIEWS
# ============================================================================

class CityListView(generic.ListView):
    """List all cities with optional filtering."""

    model = City
    template_name = 'users/city_list.html'
    context_object_name = 'cities'
    paginate_by = 20

    def get_queryset(self):
        """Filter and sort cities."""
        queryset = City.objects.select_related('country').annotate(
            user_count=Count('user')
        )

        # Filter by country
        country_id = self.request.GET.get('country')
        if country_id:
            queryset = queryset.filter(country_id=country_id)

        # Filter by capital
        is_capital = self.request.GET.get('is_capital')
        if is_capital == 'true':
            queryset = queryset.filter(is_capital=True)
        elif is_capital == 'false':
            queryset = queryset.filter(is_capital=False)

        # Search by name
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) |
                Q(country__name__icontains=search)
            )

        # Sort
        sort_by = self.request.GET.get('sort_by', '-created_at')
        if sort_by in ['name', '-name', 'population', '-population', 'created_at', '-created_at']:
            queryset = queryset.order_by(sort_by)

        return queryset

    def get_context_data(self, **kwargs):
        """Add extra context for filters."""
        context = super().get_context_data(**kwargs)
        context['countries'] = Country.objects.all().order_by('name')
        context['total_count'] = City.objects.count()
        context['search'] = self.request.GET.get('search', '')
        context['country_id'] = self.request.GET.get('country', '')
        context['is_capital'] = self.request.GET.get('is_capital', '')
        context['sort_by'] = self.request.GET.get('sort_by', '-created_at')
        return context


class CityDetailView(generic.DetailView):
    """Display single city with its users."""

    model = City
    template_name = 'users/city_detail.html'
    context_object_name = 'city'

    def get_context_data(self, **kwargs):
        """Add related users to context."""
        context = super().get_context_data(**kwargs)
        context['users'] = self.object.user_set.filter(is_active=True).order_by('first_name')
        return context


class CityCreateView(generic.CreateView):
    """Create new city."""

    model = City
    form_class = CityForm
    template_name = 'users/city_form.html'
    success_url = reverse_lazy('users:city-list')

    def form_valid(self, form):
        """Handle successful form submission."""
        response = super().form_valid(form)
        messages.success(
            self.request,
            f'City "{self.object.name}" created successfully!'
        )
        return response

    def get_context_data(self, **kwargs):
        """Add title to context."""
        context = super().get_context_data(**kwargs)
        context['title'] = 'Create City'
        return context


class CityUpdateView(generic.UpdateView):
    """Update existing city."""

    model = City
    form_class = CityForm
    template_name = 'users/city_form.html'

    def get_success_url(self):
        """Redirect to city detail after update."""
        return reverse_lazy('users:city-detail', kwargs={'pk': self.object.pk})

    def form_valid(self, form):
        """Handle successful form submission."""
        response = super().form_valid(form)
        messages.success(
            self.request,
            f'City "{self.object.name}" updated successfully!'
        )
        return response

    def get_context_data(self, **kwargs):
        """Add title to context."""
        context = super().get_context_data(**kwargs)
        context['title'] = 'Edit City'
        return context


class CityDeleteView(generic.DeleteView):
    """Delete city."""

    model = City
    template_name = 'users/city_confirm_delete.html'
    success_url = reverse_lazy('users:city-list')

    def delete(self, request, *args, **kwargs):
        """Delete and show message."""
        city = self.get_object()
        messages.success(
            request,
            f'City "{city.name}" deleted!'
        )
        return super().delete(request, *args, **kwargs)


# ============================================================================
# USER VIEWS
# ============================================================================

class UserListView(generic.ListView):
    """List all users with advanced filtering and search."""

    model = User
    template_name = 'users/user_list.html'
    context_object_name = 'users'
    paginate_by = 10

    def get_queryset(self):
        """Filter, search, and sort users."""
        queryset = User.objects.select_related('city__country')

        # Search by name or email
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(first_name__icontains=search) |
                Q(last_name__icontains=search) |
                Q(email__icontains=search)
            )

        # Filter by city
        city_id = self.request.GET.get('city')
        if city_id:
            queryset = queryset.filter(city_id=city_id)

        # Filter by active status
        is_active = self.request.GET.get('is_active')
        if is_active == 'true':
            queryset = queryset.filter(is_active=True)
        elif is_active == 'false':
            queryset = queryset.filter(is_active=False)

        # Sort
        sort_by = self.request.GET.get('sort_by', '-created_at')
        if sort_by in ['first_name', '-first_name', 'email', 'created_at', '-created_at']:
            queryset = queryset.order_by(sort_by)
        else:
            queryset = queryset.order_by('-created_at')

        return queryset

    def get_context_data(self, **kwargs):
        """Add filters and search form to context."""
        context = super().get_context_data(**kwargs)
        context['form'] = UserSearchForm(self.request.GET)
        context['cities'] = City.objects.all().order_by('name')
        context['total_count'] = User.objects.count()
        context['active_count'] = User.objects.filter(is_active=True).count()
        return context


class UserDetailView(generic.DetailView):
    """Display single user profile."""

    model = User
    template_name = 'users/user_detail.html'
    context_object_name = 'user'

    def get_context_data(self, **kwargs):
        """Add additional context."""
        context = super().get_context_data(**kwargs)
        context['location'] = self.object.get_location_string()
        return context


class UserCreateView(generic.CreateView):
    """Create new user."""

    model = User
    form_class = UserForm
    template_name = 'users/user_form.html'
    success_url = reverse_lazy('users:user-list')

    def form_valid(self, form):
        """Handle successful form submission."""
        response = super().form_valid(form)
        messages.success(
            self.request,
            f'User "{self.object.full_name()}" created successfully!'
        )
        return response

    def get_context_data(self, **kwargs):
        """Add title to context."""
        context = super().get_context_data(**kwargs)
        context['title'] = 'Create User'
        return context


class UserUpdateView(generic.UpdateView):
    """Update existing user."""

    model = User
    form_class = UserForm
    template_name = 'users/user_form.html'

    def get_success_url(self):
        """Redirect to user detail after update."""
        return reverse_lazy('users:user-detail', kwargs={'pk': self.object.pk})

    def form_valid(self, form):
        """Handle successful form submission."""
        response = super().form_valid(form)
        messages.success(
            self.request,
            f'User "{self.object.full_name()}" updated successfully!'
        )
        return response

    def get_context_data(self, **kwargs):
        """Add title to context."""
        context = super().get_context_data(**kwargs)
        context['title'] = 'Edit User'
        return context


class UserDeleteView(generic.DeleteView):
    """Delete user."""

    model = User
    template_name = 'users/user_confirm_delete.html'
    success_url = reverse_lazy('users:user-list')

    def delete(self, request, *args, **kwargs):
        """Delete and show message."""
        user = self.get_object()
        messages.success(
            request,
            f'User "{user.full_name()}" deleted!'
        )
        return super().delete(request, *args, **kwargs)
