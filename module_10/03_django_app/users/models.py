"""
User management models.

Defines Country, City, and User models with relationships.
"""

from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone


class Country(models.Model):
    """
    Represents a country.

    Fields:
    - name: Country name (unique)
    - code: ISO 3166-1 alpha-2 code (e.g., 'UA')
    - population: Total population (optional)
    - created_at: When record was created
    """

    name = models.CharField(
        max_length=100,
        unique=True,
        db_index=True,
        help_text="Country name"
    )
    code = models.CharField(
        max_length=2,
        unique=True,
        help_text="ISO 3166-1 alpha-2 code"
    )
    population = models.BigIntegerField(
        null=True,
        blank=True,
        help_text="Total population"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Country"
        verbose_name_plural = "Countries"
        ordering = ['name']
        indexes = [
            models.Index(fields=['code']),
            models.Index(fields=['name']),
        ]

    def __str__(self):
        return self.name

    def city_count(self):
        """Get number of cities in this country."""
        return self.city_set.count()

    def user_count(self):
        """Get number of users in this country."""
        return self.city_set.aggregate(
            count=models.Count('user')
        )['count'] or 0


class City(models.Model):
    """
    Represents a city in a country.

    Fields:
    - name: City name
    - country: Foreign key to Country
    - population: City population (optional)
    - founded_year: Year city was founded (optional)
    - is_capital: Is this the capital? (default: False)
    - created_at: When record was created
    """

    name = models.CharField(
        max_length=100,
        db_index=True,
        help_text="City name"
    )
    country = models.ForeignKey(
        Country,
        on_delete=models.CASCADE,
        help_text="Country where city is located"
    )
    population = models.IntegerField(
        null=True,
        blank=True,
        help_text="City population"
    )
    founded_year = models.IntegerField(
        null=True,
        blank=True,
        validators=[
            MinValueValidator(1),
            MaxValueValidator(timezone.now().year)
        ],
        help_text="Year city was founded"
    )
    is_capital = models.BooleanField(
        default=False,
        help_text="Is this the capital?"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "City"
        verbose_name_plural = "Cities"
        ordering = ['country', 'name']
        unique_together = ('name', 'country')
        indexes = [
            models.Index(fields=['country', 'name']),
            models.Index(fields=['is_capital']),
        ]

    def __str__(self):
        return f"{self.name}, {self.country.name}"

    def user_count(self):
        """Get number of users in this city."""
        return self.user_set.count()


class User(models.Model):
    """
    Represents a user/contact.

    Fields:
    - first_name: User first name
    - last_name: User last name
    - email: Email address (unique)
    - phone: Phone number (optional)
    - city: Foreign key to City (optional)
    - bio: User biography (optional)
    - is_active: Is user active?
    - created_at: When record was created
    - updated_at: Last update time
    """

    first_name = models.CharField(
        max_length=100,
        help_text="User first name"
    )
    last_name = models.CharField(
        max_length=100,
        help_text="User last name"
    )
    email = models.EmailField(
        unique=True,
        db_index=True,
        help_text="User email address"
    )
    phone = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        help_text="Phone number"
    )
    city = models.ForeignKey(
        City,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text="User's city"
    )
    bio = models.TextField(
        blank=True,
        help_text="User biography"
    )
    is_active = models.BooleanField(
        default=True,
        help_text="Is user active?"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "User"
        verbose_name_plural = "Users"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['email']),
            models.Index(fields=['city']),
            models.Index(fields=['is_active']),
            models.Index(fields=['-created_at']),
        ]

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    def full_name(self):
        """Return user's full name."""
        return f"{self.first_name} {self.last_name}"

    def get_city_name(self):
        """Get city name or 'No city' if not set."""
        if self.city:
            return self.city.name
        return "No city"

    def get_country_name(self):
        """Get country name or 'No country' if city not set."""
        if self.city and self.city.country:
            return self.city.country.name
        return "No country"

    def get_location_string(self):
        """Get full location string."""
        if self.city:
            return str(self.city)
        return "Location not specified"
