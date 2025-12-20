"""
User management forms.

ModelForms with custom validation and Bootstrap styling.
"""

from django import forms
from django.core.exceptions import ValidationError
from .models import User, City, Country


class CountryForm(forms.ModelForm):
    """Form for creating/editing countries."""

    class Meta:
        model = Country
        fields = ['name', 'code', 'population']
        labels = {
            'name': 'Country Name *',
            'code': 'Country Code (ISO-2) *',
            'population': 'Population',
        }
        help_texts = {
            'code': 'Two-letter ISO code (e.g., UA for Ukraine)',
            'population': 'Optional: Total population',
        }
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., Ukraine',
                'autofocus': True,
            }),
            'code': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., UA',
                'maxlength': 2,
                'style': 'text-transform: uppercase;',
            }),
            'population': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Optional',
            }),
        }

    def clean_code(self):
        """Validate code is uppercase 2-letter format."""
        code = self.cleaned_data.get('code')

        if code:
            code = code.upper()
            if len(code) != 2:
                raise ValidationError('Code must be exactly 2 characters')
            if not code.isalpha():
                raise ValidationError('Code must contain only letters')

        return code

    def clean_name(self):
        """Validate name is not too short."""
        name = self.cleaned_data.get('name')

        if name and len(name) < 2:
            raise ValidationError('Name must be at least 2 characters')

        return name


class CityForm(forms.ModelForm):
    """Form for creating/editing cities."""

    class Meta:
        model = City
        fields = ['name', 'country', 'population', 'founded_year', 'is_capital']
        labels = {
            'name': 'City Name *',
            'country': 'Country *',
            'population': 'Population',
            'founded_year': 'Founded Year',
            'is_capital': 'Is Capital?',
        }
        help_texts = {
            'population': 'Optional: City population',
            'founded_year': 'Optional: Year city was founded',
        }
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., Kyiv',
                'autofocus': True,
            }),
            'country': forms.Select(attrs={
                'class': 'form-select',
            }),
            'population': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Optional',
            }),
            'founded_year': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': f'1000-{2024}',
                'min': 1,
            }),
            'is_capital': forms.CheckboxInput(attrs={
                'class': 'form-check-input',
            }),
        }

    def clean(self):
        """Validate form data."""
        cleaned_data = super().clean()
        name = cleaned_data.get('name')
        country = cleaned_data.get('country')
        founded_year = cleaned_data.get('founded_year')

        # Check for duplicate city in same country
        if name and country:
            existing = City.objects.filter(
                name=name,
                country=country
            ).exclude(pk=self.instance.pk)

            if existing.exists():
                raise ValidationError(
                    f"City '{name}' already exists in {country.name}"
                )

        # Validate founded year
        if founded_year:
            import datetime
            current_year = datetime.datetime.now().year
            if founded_year > current_year:
                raise ValidationError('Founded year cannot be in the future')

        return cleaned_data


class UserForm(forms.ModelForm):
    """Form for creating/editing users."""

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'phone', 'city', 'bio', 'is_active']
        labels = {
            'first_name': 'First Name *',
            'last_name': 'Last Name *',
            'email': 'Email Address *',
            'phone': 'Phone Number',
            'city': 'City',
            'bio': 'Biography',
            'is_active': 'Active?',
        }
        help_texts = {
            'email': 'Must be unique. We never share your email.',
            'phone': 'Optional: Include country code if international',
            'bio': 'Optional: Tell us about yourself',
        }
        widgets = {
            'first_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., John',
                'autofocus': True,
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., Doe',
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'john@example.com',
                'type': 'email',
            }),
            'phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Optional: +1 (555) 123-4567',
            }),
            'city': forms.Select(attrs={
                'class': 'form-select',
            }),
            'bio': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Optional: Your biography',
                'rows': 4,
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'form-check-input',
            }),
        }

    def clean_first_name(self):
        """Validate first name."""
        first_name = self.cleaned_data.get('first_name')

        if first_name and len(first_name) < 2:
            raise ValidationError('First name must be at least 2 characters')

        if first_name and len(first_name) > 100:
            raise ValidationError('First name is too long')

        return first_name

    def clean_last_name(self):
        """Validate last name."""
        last_name = self.cleaned_data.get('last_name')

        if last_name and len(last_name) < 2:
            raise ValidationError('Last name must be at least 2 characters')

        return last_name

    def clean_email(self):
        """Validate email is unique."""
        email = self.cleaned_data.get('email')

        if email:
            # If editing, exclude current user
            if self.instance.pk:
                existing = User.objects.filter(
                    email=email
                ).exclude(pk=self.instance.pk)
            else:
                existing = User.objects.filter(email=email)

            if existing.exists():
                raise ValidationError(
                    'This email is already registered. Please use another email.'
                )

        return email

    def clean_phone(self):
        """Validate phone number format if provided."""
        phone = self.cleaned_data.get('phone')

        if phone:
            # Remove common formatting characters
            clean_phone = phone.replace(' ', '').replace('-', '').replace('(', '').replace(')', '')

            if not any(char.isdigit() for char in clean_phone):
                raise ValidationError('Phone number must contain at least one digit')

            if len(clean_phone) < 7:
                raise ValidationError('Phone number is too short')

        return phone

    def clean(self):
        """Validate form as a whole."""
        cleaned_data = super().clean()
        first_name = cleaned_data.get('first_name')
        last_name = cleaned_data.get('last_name')

        # Check first and last name are different
        if first_name and last_name:
            if first_name.lower() == last_name.lower():
                raise ValidationError(
                    'First and last name cannot be the same'
                )

        return cleaned_data


class UserSearchForm(forms.Form):
    """Form for searching and filtering users."""

    search = forms.CharField(
        max_length=100,
        required=False,
        label='Search',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Search by name or email...',
        })
    )

    city = forms.ModelChoiceField(
        queryset=City.objects.all(),
        required=False,
        label='Filter by City',
        empty_label='All Cities',
        widget=forms.Select(attrs={
            'class': 'form-select',
        })
    )

    is_active = forms.ChoiceField(
        choices=[
            ('', 'All Users'),
            ('true', 'Active Only'),
            ('false', 'Inactive Only'),
        ],
        required=False,
        label='Status',
        widget=forms.Select(attrs={
            'class': 'form-select',
        })
    )

    sort_by = forms.ChoiceField(
        choices=[
            ('-created_at', 'Newest First'),
            ('created_at', 'Oldest First'),
            ('first_name', 'Name (A-Z)'),
            ('-first_name', 'Name (Z-A)'),
            ('email', 'Email (A-Z)'),
        ],
        required=False,
        initial='-created_at',
        label='Sort By',
        widget=forms.Select(attrs={
            'class': 'form-select',
        })
    )
