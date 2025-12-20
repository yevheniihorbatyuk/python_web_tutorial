# Event Hub API Endpoints

## Authentication

### Obtain JWT Token
```
POST /api/auth/token/
Content-Type: application/json

{
  "username": "admin",
  "password": "admin123"
}

Response:
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

### Refresh Token
```
POST /api/auth/token/refresh/
Content-Type: application/json

{
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}

Response:
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

## Users

### List Users
```
GET /api/users/
Query parameters: username, email, ordering (-date_joined, username)

Response: [
  {
    "id": 1,
    "username": "admin",
    "email": "admin@example.com",
    "full_name": "Admin User",
    "user_type": "admin",
    "avatar": null,
    "organization": ""
  }
]
```

### Get Current User
```
GET /api/users/me/
Authorization: Bearer {access_token}

Response: {
  "id": 1,
  "username": "admin",
  "email": "admin@example.com",
  "first_name": "Admin",
  "last_name": "User",
  "full_name": "Admin User",
  "user_type": "admin",
  "bio": "",
  "phone": "",
  "avatar": null,
  "website": "",
  "organization": "",
  "is_verified": false,
  "is_active": true,
  "is_organizer": true,
  "profile": { ... }
}
```

### Register New User
```
POST /api/users/
Content-Type: application/json

{
  "username": "newuser",
  "email": "newuser@example.com",
  "password": "secure_password",
  "password_confirm": "secure_password",
  "first_name": "John",
  "last_name": "Doe",
  "user_type": "attendee"
}

Response: {
  "id": 2,
  "username": "newuser",
  "email": "newuser@example.com",
  "first_name": "John",
  "last_name": "Doe",
  "full_name": "John Doe",
  "user_type": "attendee",
  ...
}
```

### Update Current User Profile
```
PUT/PATCH /api/users/me/
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "first_name": "John",
  "last_name": "Doe",
  "bio": "Software developer",
  "phone": "+1234567890",
  "website": "https://johndoe.com",
  "organization": "Tech Company"
}
```

### Update Profile Settings
```
PUT/PATCH /api/users/update_profile/
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "twitter": "https://twitter.com/johndoe",
  "linkedin": "https://linkedin.com/in/johndoe",
  "github": "https://github.com/johndoe",
  "facebook": "https://facebook.com/johndoe",
  "newsletter_subscribed": true,
  "notifications_enabled": true
}
```

### Get User's Organized Events
```
GET /api/users/{id}/events_organized/
Authorization: Bearer {access_token}
```

### Get User's Reviews
```
GET /api/users/{id}/reviews/
Authorization: Bearer {access_token}
```

## Events

### List Events
```
GET /api/events/
Query parameters:
  - category (workshop, webinar, conference, masterclass, meetup, training)
  - status (draft, published, ongoing, completed, cancelled)
  - is_online (true/false)
  - search (title, description, tags)
  - ordering (-start_date, created_at, price)

Response: [
  {
    "id": 1,
    "title": "Test Workshop",
    "category": "workshop",
    "organizer_name": "Admin User",
    "location": "Test Location",
    "is_online": false,
    "status": "published",
    "start_date": "2025-12-27T12:00:00Z",
    "end_date": "2025-12-27T14:00:00Z",
    "max_attendees": 50,
    "attendees_count": 0,
    "price": "0.00",
    "cover_image": null
  }
]
```

### Get Event Details
```
GET /api/events/{id}/
Authorization: Optional

Response: {
  "id": 1,
  "title": "Test Workshop",
  "description": "A test workshop",
  "category": "workshop",
  "organizer": 1,
  "organizer_name": "Admin User",
  "location": "Test Location",
  "is_online": false,
  "online_url": "",
  "status": "published",
  "start_date": "2025-12-27T12:00:00Z",
  "end_date": "2025-12-27T14:00:00Z",
  "registration_deadline": "2025-12-25T12:00:00Z",
  "max_attendees": 50,
  "attendees_count": 0,
  "available_spots": 50,
  "is_registration_open": true,
  "price": "0.00",
  "cover_image": null,
  "tags": "",
  "sessions": [],
  "created_at": "2025-12-20T12:00:00Z",
  "updated_at": "2025-12-20T12:00:00Z"
}
```

### Create Event (Organizers Only)
```
POST /api/events/
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "title": "Advanced Python Workshop",
  "description": "Learn advanced Python concepts",
  "category": "workshop",
  "location": "Virtual",
  "is_online": true,
  "online_url": "https://zoom.us/...",
  "start_date": "2025-12-27T14:00:00Z",
  "end_date": "2025-12-27T17:00:00Z",
  "registration_deadline": "2025-12-26T14:00:00Z",
  "max_attendees": 30,
  "price": "29.99",
  "tags": "python, programming, advanced"
}
```

### Update Event
```
PUT/PATCH /api/events/{id}/
Authorization: Bearer {access_token} (Organizer only)
Content-Type: application/json
```

### Publish Event
```
POST /api/events/{id}/publish/
Authorization: Bearer {access_token} (Organizer only)
```

### Cancel Event
```
POST /api/events/{id}/cancel/
Authorization: Bearer {access_token} (Organizer only)
```

### Get Event Attendees
```
GET /api/events/{id}/attendees/
Authorization: Optional
```

### Get Event Statistics
```
GET /api/events/{id}/statistics/
Authorization: Optional

Response: {
  "total_attendees": 0,
  "available_spots": 50,
  "waitlist_count": 0,
  "reviews_count": 0,
  "average_rating": 0,
  "total_revenue": 0.0
}
```

## Sessions

### List Sessions
```
GET /api/sessions/
Query parameters: event, speaker, ordering (start_time)

Response: [
  {
    "id": 1,
    "title": "Session Title",
    "description": "Session description",
    "start_time": "2025-12-27T14:00:00Z",
    "end_time": "2025-12-27T15:00:00Z",
    "speaker": 1,
    "speaker_name": "Speaker Name",
    "room_or_link": "Room A",
    "created_at": "2025-12-20T12:00:00Z",
    "updated_at": "2025-12-20T12:00:00Z"
  }
]
```

### Create Session
```
POST /api/sessions/
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "event": 1,
  "title": "Opening Keynote",
  "description": "Opening keynote speech",
  "start_time": "2025-12-27T14:00:00Z",
  "end_time": "2025-12-27T15:00:00Z",
  "speaker": 1,
  "room_or_link": "Main Hall"
}
```

## Bookings

### List User's Bookings
```
GET /api/bookings/
Authorization: Bearer {access_token}
Query parameters: event, status, ordering (-registered_at)

Response: [
  {
    "id": 1,
    "event": 1,
    "event_title": "Test Workshop",
    "user": 2,
    "user_name": "John Doe",
    "status": "confirmed",
    "number_of_tickets": 1,
    "total_price": "0.00",
    "special_requirements": "",
    "registered_at": "2025-12-20T12:00:00Z",
    "confirmed_at": "2025-12-20T12:00:01Z",
    "cancelled_at": null
  }
]
```

### Create Booking
```
POST /api/bookings/
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "event": 1,
  "number_of_tickets": 1,
  "special_requirements": "Need vegetarian meals"
}

Response: {
  "id": 1,
  "event": 1,
  "event_title": "Test Workshop",
  "user": 2,
  "user_name": "John Doe",
  "status": "pending",
  "number_of_tickets": 1,
  "total_price": "0.00",
  "special_requirements": "Need vegetarian meals",
  "registered_at": "2025-12-20T12:00:00Z",
  "confirmed_at": null,
  "cancelled_at": null
}
```

### Confirm Booking
```
POST /api/bookings/{id}/confirm/
Authorization: Bearer {access_token}
```

### Cancel Booking
```
POST /api/bookings/{id}/cancel/
Authorization: Bearer {access_token}
```

## Waitlist

### Get User's Waitlist Entries
```
GET /api/waitlist/
Authorization: Bearer {access_token}
Query parameters: event, ordering (position)
```

### Join Waitlist
```
POST /api/waitlist/
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "event": 1
}
```

### Leave Waitlist
```
POST /api/waitlist/{id}/leave/
Authorization: Bearer {access_token}
```

## Payments

### List User's Payments
```
GET /api/payments/
Authorization: Bearer {access_token}
Query parameters: status, method, ordering (-created_at)

Response: [
  {
    "id": 1,
    "booking": 1,
    "booking_event": "Test Workshop",
    "user": 2,
    "user_name": "John Doe",
    "amount": "0.00",
    "currency": "USD",
    "status": "pending",
    "method": "mock",
    "transaction_id": "EVH-ABCD1234EFGH",
    "reference_number": "",
    "created_at": "2025-12-20T12:00:00Z",
    "processed_at": null,
    "refunded_at": null
  }
]
```

### Create Payment
```
POST /api/payments/
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "booking": 1,
  "amount": "29.99",
  "method": "mock"
}
```

### Refund Payment
```
POST /api/payments/{id}/refund/
Authorization: Bearer {access_token}
```

### Get Payment Receipt
```
GET /api/payments/{id}/receipt/
Authorization: Bearer {access_token}
```

## Invoices

### List User's Invoices
```
GET /api/invoices/
Authorization: Bearer {access_token}
Query parameters: is_sent, search (invoice_number, transaction_id), ordering (-issued_at)
```

### Get Invoice Details
```
GET /api/invoices/{id}/
Authorization: Bearer {access_token}
```

### Mark Invoice as Sent
```
POST /api/invoices/{id}/mark_as_sent/
Authorization: Bearer {access_token}
```

## Notifications

### List User's Notifications
```
GET /api/notifications/
Authorization: Bearer {access_token}
Query parameters: notification_type, is_read, event, ordering (-created_at)

Response: [
  {
    "id": 1,
    "user": 2,
    "user_name": "John Doe",
    "event": 1,
    "event_title": "Test Workshop",
    "notification_type": "booking_confirmation",
    "title": "Booking Confirmation",
    "message": "Your booking has been confirmed",
    "is_read": false,
    "created_at": "2025-12-20T12:00:00Z",
    "read_at": null
  }
]
```

### Mark Notification as Read
```
POST /api/notifications/{id}/mark_as_read/
Authorization: Bearer {access_token}
```

### Mark All Notifications as Read
```
POST /api/notifications/mark_all_as_read/
Authorization: Bearer {access_token}
```

### Get Unread Count
```
GET /api/notifications/unread_count/
Authorization: Bearer {access_token}

Response: {
  "unread_count": 5
}
```

## Reviews

### List Event Reviews
```
GET /api/reviews/
Authorization: Optional
Query parameters: event, rating, search (event__title, title), ordering (-created_at)

Response: [
  {
    "id": 1,
    "event": 1,
    "event_title": "Test Workshop",
    "user": 2,
    "user_name": "John Doe",
    "rating": 5,
    "title": "Excellent workshop!",
    "review": "Very informative and well organized",
    "attended": true,
    "helpful_count": 5,
    "unhelpful_count": 0,
    "helpful_percentage": 100.0,
    "created_at": "2025-12-20T12:00:00Z",
    "updated_at": "2025-12-20T12:00:00Z"
  }
]
```

### Create Review
```
POST /api/reviews/
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "event": 1,
  "rating": 5,
  "title": "Excellent workshop!",
  "review": "Very informative and well organized",
  "attended": true
}
```

### Mark Review as Helpful
```
POST /api/reviews/{id}/mark_helpful/
Authorization: Bearer {access_token}
```

### Mark Review as Unhelpful
```
POST /api/reviews/{id}/mark_unhelpful/
Authorization: Bearer {access_token}
```

## Certificates

### List User's Certificates
```
GET /api/certificates/
Authorization: Bearer {access_token}
Query parameters: event, is_downloaded, search (certificate_number, event__title), ordering (-issued_date)

Response: [
  {
    "id": 1,
    "event": 1,
    "event_title": "Test Workshop",
    "user": 2,
    "user_name": "John Doe",
    "certificate_number": "CERT-1-2-ABC123",
    "hours_completed": 2.0,
    "skill_tags": "python, programming",
    "pdf_file": null,
    "is_downloaded": false,
    "issued_date": "2025-12-20T12:00:00Z",
    "downloaded_at": null
  }
]
```

### Mark Certificate as Downloaded
```
POST /api/certificates/{id}/mark_as_downloaded/
Authorization: Bearer {access_token}
```

## Error Responses

All endpoints return appropriate HTTP status codes:

- **200 OK**: Successful GET, PUT, PATCH
- **201 Created**: Successful POST (resource creation)
- **204 No Content**: Successful DELETE
- **400 Bad Request**: Invalid request data
- **401 Unauthorized**: Missing or invalid authentication
- **403 Forbidden**: Insufficient permissions
- **404 Not Found**: Resource not found
- **409 Conflict**: Duplicate entry or business logic conflict

Example error response:
```json
{
  "detail": "Not found.",
  "error": "The requested resource was not found."
}
```

## Testing with cURL

### Get JWT Token
```bash
curl -X POST http://localhost:8000/api/auth/token/ \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin123"}'
```

### List Events
```bash
curl -X GET http://localhost:8000/api/events/ \
  -H "Authorization: Bearer {access_token}"
```

### Create Event
```bash
curl -X POST http://localhost:8000/api/events/ \
  -H "Authorization: Bearer {access_token}" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "New Workshop",
    "description": "Workshop description",
    "category": "workshop",
    "location": "Virtual",
    "is_online": true,
    "online_url": "https://zoom.us/...",
    "start_date": "2025-12-27T14:00:00Z",
    "end_date": "2025-12-27T17:00:00Z",
    "registration_deadline": "2025-12-26T14:00:00Z",
    "max_attendees": 30,
    "price": "0.00"
  }'
```
