"""
URL routing for users app.
"""

from django.urls import path
from . import views

app_name = 'users'

urlpatterns = [
    # User URLs
    path('', views.UserListView.as_view(), name='user-list'),
    path('<int:pk>/', views.UserDetailView.as_view(), name='user-detail'),
    path('create/', views.UserCreateView.as_view(), name='user-create'),
    path('<int:pk>/edit/', views.UserUpdateView.as_view(), name='user-update'),
    path('<int:pk>/delete/', views.UserDeleteView.as_view(), name='user-delete'),

    # City URLs
    path('cities/', views.CityListView.as_view(), name='city-list'),
    path('cities/<int:pk>/', views.CityDetailView.as_view(), name='city-detail'),
    path('cities/create/', views.CityCreateView.as_view(), name='city-create'),
    path('cities/<int:pk>/edit/', views.CityUpdateView.as_view(), name='city-update'),
    path('cities/<int:pk>/delete/', views.CityDeleteView.as_view(), name='city-delete'),

    # Country URLs
    path('countries/', views.CountryListView.as_view(), name='country-list'),
    path('countries/<int:pk>/', views.CountryDetailView.as_view(), name='country-detail'),
    path('countries/create/', views.CountryCreateView.as_view(), name='country-create'),
    path('countries/<int:pk>/edit/', views.CountryUpdateView.as_view(), name='country-update'),
    path('countries/<int:pk>/delete/', views.CountryDeleteView.as_view(), name='country-delete'),
]
