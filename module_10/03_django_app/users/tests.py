"""
Unit tests for users app models, forms, and views.

Tests cover:
- Model creation and validation
- ForeignKey relationships
- Form validation
- View functionality
- Query optimization
"""

from django.test import TestCase, Client
from django.urls import reverse
from django.core.exceptions import ValidationError
from .models import Country, City, User
from .forms import CountryForm, CityForm, UserForm, UserSearchForm


class CountryModelTests(TestCase):
    """Tests for Country model."""

    def setUp(self):
        """Create test data."""
        self.country = Country.objects.create(
            name="Ukraine",
            code="UA",
            population=41000000
        )

    def test_country_creation(self):
        """Test Country model can be created."""
        self.assertEqual(self.country.name, "Ukraine")
        self.assertEqual(self.country.code, "UA")
        self.assertEqual(self.country.population, 41000000)

    def test_country_string_representation(self):
        """Test Country __str__ method."""
        self.assertEqual(str(self.country), "Ukraine")

    def test_country_code_unique(self):
        """Test Country code field is unique."""
        with self.assertRaises(Exception):
            Country.objects.create(name="Poland", code="UA")

    def test_country_name_unique(self):
        """Test Country name field is unique."""
        with self.assertRaises(Exception):
            Country.objects.create(name="Ukraine", code="PL")

    def test_country_code_indexed(self):
        """Test that code field is indexed for performance."""
        # Check that code field has db_index=True
        code_field = Country._meta.get_field('code')
        self.assertTrue(code_field.unique)

    def test_country_city_count(self):
        """Test city_count method."""
        self.assertEqual(self.country.city_count(), 0)

        City.objects.create(
            name="Kyiv",
            country=self.country,
            is_capital=True
        )
        City.objects.create(
            name="Lviv",
            country=self.country
        )

        self.assertEqual(self.country.city_count(), 2)

    def test_country_user_count(self):
        """Test user_count method."""
        self.assertEqual(self.country.user_count(), 0)

        city = City.objects.create(
            name="Kyiv",
            country=self.country,
            is_capital=True
        )

        User.objects.create(
            first_name="John",
            last_name="Doe",
            email="john@example.com",
            city=city
        )
        User.objects.create(
            first_name="Jane",
            last_name="Smith",
            email="jane@example.com",
            city=city
        )

        self.assertEqual(self.country.user_count(), 2)


class CityModelTests(TestCase):
    """Tests for City model."""

    def setUp(self):
        """Create test data."""
        self.country = Country.objects.create(
            name="Ukraine",
            code="UA"
        )
        self.city = City.objects.create(
            name="Kyiv",
            country=self.country,
            is_capital=True,
            population=2900000,
            founded_year=1200
        )

    def test_city_creation(self):
        """Test City model can be created."""
        self.assertEqual(self.city.name, "Kyiv")
        self.assertEqual(self.city.country, self.country)
        self.assertTrue(self.city.is_capital)

    def test_city_string_representation(self):
        """Test City __str__ method includes country."""
        self.assertEqual(str(self.city), "Kyiv, Ukraine")

    def test_city_unique_together(self):
        """Test city name must be unique per country."""
        with self.assertRaises(Exception):
            City.objects.create(
                name="Kyiv",
                country=self.country
            )

    def test_city_same_name_different_country(self):
        """Test same city name can exist in different countries."""
        another_country = Country.objects.create(
            name="Poland",
            code="PL"
        )

        city2 = City.objects.create(
            name="Kyiv",
            country=another_country
        )

        self.assertNotEqual(city2.country, self.country)
        self.assertEqual(City.objects.filter(name="Kyiv").count(), 2)

    def test_city_founded_year_validation(self):
        """Test founded_year validator."""
        from django.utils import timezone
        import datetime

        future_year = timezone.now().year + 10

        with self.assertRaises(ValidationError):
            city = City(
                name="Future City",
                country=self.country,
                founded_year=future_year
            )
            city.full_clean()

    def test_city_user_count(self):
        """Test user_count method."""
        self.assertEqual(self.city.user_count(), 0)

        User.objects.create(
            first_name="John",
            last_name="Doe",
            email="john@example.com",
            city=self.city
        )

        self.assertEqual(self.city.user_count(), 1)


class UserModelTests(TestCase):
    """Tests for User model."""

    def setUp(self):
        """Create test data."""
        self.country = Country.objects.create(
            name="Ukraine",
            code="UA"
        )
        self.city = City.objects.create(
            name="Kyiv",
            country=self.country,
            is_capital=True
        )
        self.user = User.objects.create(
            first_name="John",
            last_name="Doe",
            email="john@example.com",
            phone="+380123456789",
            city=self.city,
            bio="Test user",
            is_active=True
        )

    def test_user_creation(self):
        """Test User model can be created."""
        self.assertEqual(self.user.first_name, "John")
        self.assertEqual(self.user.last_name, "Doe")
        self.assertEqual(self.user.email, "john@example.com")
        self.assertTrue(self.user.is_active)

    def test_user_string_representation(self):
        """Test User __str__ method."""
        self.assertEqual(str(self.user), "John Doe")

    def test_user_email_unique(self):
        """Test User email field is unique."""
        with self.assertRaises(Exception):
            User.objects.create(
                first_name="Jane",
                last_name="Doe",
                email="john@example.com"
            )

    def test_user_full_name_method(self):
        """Test full_name method."""
        self.assertEqual(self.user.full_name(), "John Doe")

    def test_user_get_city_name(self):
        """Test get_city_name method."""
        self.assertEqual(self.user.get_city_name(), "Kyiv")

        user_no_city = User.objects.create(
            first_name="Jane",
            last_name="Smith",
            email="jane@example.com"
        )
        self.assertEqual(user_no_city.get_city_name(), "No city")

    def test_user_get_country_name(self):
        """Test get_country_name method."""
        self.assertEqual(self.user.get_country_name(), "Ukraine")

        user_no_city = User.objects.create(
            first_name="Jane",
            last_name="Smith",
            email="jane@example.com"
        )
        self.assertEqual(user_no_city.get_country_name(), "No country")

    def test_user_get_location_string(self):
        """Test get_location_string method."""
        self.assertEqual(self.user.get_location_string(), "Kyiv, Ukraine")

        user_no_city = User.objects.create(
            first_name="Jane",
            last_name="Smith",
            email="jane@example.com"
        )
        self.assertEqual(user_no_city.get_location_string(), "Location not specified")

    def test_user_city_optional(self):
        """Test User can be created without city."""
        user = User.objects.create(
            first_name="Jane",
            last_name="Smith",
            email="jane@example.com"
        )
        self.assertIsNone(user.city)

    def test_user_city_set_null_on_delete(self):
        """Test User.city becomes NULL if city is deleted."""
        self.assertEqual(self.user.city, self.city)

        self.city.delete()
        self.user.refresh_from_db()

        self.assertIsNone(self.user.city)


class CountryFormTests(TestCase):
    """Tests for CountryForm."""

    def test_country_form_valid(self):
        """Test CountryForm with valid data."""
        form = CountryForm(data={
            'name': 'Poland',
            'code': 'PL',
            'population': 38000000
        })
        self.assertTrue(form.is_valid())

    def test_country_form_code_validation(self):
        """Test CountryForm validates code format."""
        form = CountryForm(data={
            'name': 'Poland',
            'code': 'PLX',
            'population': 38000000
        })
        self.assertFalse(form.is_valid())
        self.assertIn('code', form.errors)

    def test_country_form_code_uppercase(self):
        """Test CountryForm converts code to uppercase."""
        form = CountryForm(data={
            'name': 'Poland',
            'code': 'pl',
            'population': 38000000
        })
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data['code'], 'PL')

    def test_country_form_name_validation(self):
        """Test CountryForm validates name length."""
        form = CountryForm(data={
            'name': 'X',
            'code': 'PL'
        })
        self.assertFalse(form.is_valid())

    def test_country_form_code_alpha_only(self):
        """Test CountryForm code must be alphabetic."""
        form = CountryForm(data={
            'name': 'Poland',
            'code': 'P1',
            'population': 38000000
        })
        self.assertFalse(form.is_valid())
        self.assertIn('code', form.errors)


class CityFormTests(TestCase):
    """Tests for CityForm."""

    def setUp(self):
        """Create test data."""
        self.country = Country.objects.create(
            name="Ukraine",
            code="UA"
        )

    def test_city_form_valid(self):
        """Test CityForm with valid data."""
        form = CityForm(data={
            'name': 'Kyiv',
            'country': self.country.id,
            'is_capital': True
        })
        self.assertTrue(form.is_valid())

    def test_city_form_duplicate_validation(self):
        """Test CityForm prevents duplicate city in same country."""
        City.objects.create(name='Kyiv', country=self.country)

        form = CityForm(data={
            'name': 'Kyiv',
            'country': self.country.id
        })
        self.assertFalse(form.is_valid())

    def test_city_form_future_year_validation(self):
        """Test CityForm rejects future founded year."""
        from django.utils import timezone
        future_year = timezone.now().year + 10

        form = CityForm(data={
            'name': 'New City',
            'country': self.country.id,
            'founded_year': future_year
        })
        self.assertFalse(form.is_valid())

    def test_city_form_allows_same_name_different_country(self):
        """Test CityForm allows same name in different countries."""
        another_country = Country.objects.create(
            name="Poland",
            code="PL"
        )
        City.objects.create(name='Kyiv', country=self.country)

        form = CityForm(data={
            'name': 'Kyiv',
            'country': another_country.id
        })
        self.assertTrue(form.is_valid())


class UserFormTests(TestCase):
    """Tests for UserForm."""

    def test_user_form_valid(self):
        """Test UserForm with valid data."""
        form = UserForm(data={
            'first_name': 'John',
            'last_name': 'Doe',
            'email': 'john@example.com',
            'phone': '+380123456789'
        })
        self.assertTrue(form.is_valid())

    def test_user_form_name_validation(self):
        """Test UserForm validates name length."""
        form = UserForm(data={
            'first_name': 'X',
            'last_name': 'Doe',
            'email': 'john@example.com'
        })
        self.assertFalse(form.is_valid())

    def test_user_form_email_unique_validation(self):
        """Test UserForm validates email is unique."""
        User.objects.create(
            first_name='John',
            last_name='Doe',
            email='john@example.com'
        )

        form = UserForm(data={
            'first_name': 'Jane',
            'last_name': 'Smith',
            'email': 'john@example.com'
        })
        self.assertFalse(form.is_valid())

    def test_user_form_phone_validation(self):
        """Test UserForm validates phone number format."""
        form = UserForm(data={
            'first_name': 'John',
            'last_name': 'Doe',
            'email': 'john@example.com',
            'phone': 'abc'
        })
        self.assertFalse(form.is_valid())

    def test_user_form_same_first_last_name_validation(self):
        """Test UserForm prevents same first and last name."""
        form = UserForm(data={
            'first_name': 'John',
            'last_name': 'John',
            'email': 'john@example.com'
        })
        self.assertFalse(form.is_valid())

    def test_user_form_optional_fields(self):
        """Test UserForm allows optional fields."""
        form = UserForm(data={
            'first_name': 'John',
            'last_name': 'Doe',
            'email': 'john@example.com'
        })
        self.assertTrue(form.is_valid())

    def test_user_form_edit_preserves_email(self):
        """Test UserForm allows editing user with same email."""
        user = User.objects.create(
            first_name='John',
            last_name='Doe',
            email='john@example.com'
        )

        form = UserForm(
            data={
                'first_name': 'Johnny',
                'last_name': 'Doe',
                'email': 'john@example.com'
            },
            instance=user
        )
        self.assertTrue(form.is_valid())


class UserSearchFormTests(TestCase):
    """Tests for UserSearchForm."""

    def test_search_form_valid_empty(self):
        """Test UserSearchForm with no filters."""
        form = UserSearchForm(data={})
        self.assertTrue(form.is_valid())

    def test_search_form_with_search_term(self):
        """Test UserSearchForm with search term."""
        form = UserSearchForm(data={
            'search': 'john'
        })
        self.assertTrue(form.is_valid())

    def test_search_form_with_all_fields(self):
        """Test UserSearchForm with all fields filled."""
        country = Country.objects.create(name='Ukraine', code='UA')
        city = City.objects.create(name='Kyiv', country=country)

        form = UserSearchForm(data={
            'search': 'john',
            'city': city.id,
            'is_active': 'true',
            'sort_by': '-created_at'
        })
        self.assertTrue(form.is_valid())


class UserListViewTests(TestCase):
    """Tests for User list view."""

    def setUp(self):
        """Create test data."""
        self.client = Client()
        self.country = Country.objects.create(
            name="Ukraine",
            code="UA"
        )
        self.city = City.objects.create(
            name="Kyiv",
            country=self.country
        )
        self.user1 = User.objects.create(
            first_name="John",
            last_name="Doe",
            email="john@example.com",
            city=self.city
        )
        self.user2 = User.objects.create(
            first_name="Jane",
            last_name="Smith",
            email="jane@example.com"
        )

    def test_user_list_view_accessible(self):
        """Test user list view returns 200 status."""
        response = self.client.get(reverse('users:user-list'))
        self.assertEqual(response.status_code, 200)

    def test_user_list_view_shows_users(self):
        """Test user list view displays users."""
        response = self.client.get(reverse('users:user-list'))
        self.assertContains(response, 'John Doe')
        self.assertContains(response, 'Jane Smith')

    def test_user_list_view_uses_template(self):
        """Test user list view uses correct template."""
        response = self.client.get(reverse('users:user-list'))
        self.assertTemplateUsed(response, 'users/user_list.html')
