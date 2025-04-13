# Beyond Hunger API Documentation

## Authentication

Most API endpoints require authentication. The Beyond Hunger API uses token-based authentication.

### Obtaining a Token

**Endpoint**: `/api/login/`
**Method**: POST
**Description**: Authenticate and obtain a token

**Request Body**:
```json
{
  "username": "your_username",
  "password": "your_password"
}
```

**Response**:
```json
{
  "token": "your_auth_token",
  "user_id": 1,
  "username": "your_username"
}
```

### Using a Token

Include the token in the Authorization header of your requests:

```
Authorization: Token your_auth_token
```

## API Endpoints

### Statistics

**Endpoint**: `/api/statistics/`
**Method**: GET
**Authentication**: Required
**Description**: Get system-wide statistics

**Response**:
```json
{
  "total_donations": 24,
  "pending_donations": 5,
  "delivered_donations": 15,
  "total_volunteers": 8,
  "active_volunteers": 6,
  "total_users": 35
}
```

### Donations

#### List Donations

**Endpoint**: `/api/donations/`
**Method**: GET
**Authentication**: Required
**Description**: Get a list of all donations

**Response**:
```json
[
  {
    "id": 1,
    "donor": {
      "id": 2,
      "username": "donor1"
    },
    "food_type": "Fruits",
    "quantity": "5 kg",
    "expiry_date": "2025-04-20",
    "pickup_address": "123 Main St, City",
    "pickup_date": "2025-04-15",
    "status": "pending",
    "created_at": "2025-04-13T10:30:00Z"
  },
  // ... more donations
]
```

#### Update Donation Status

**Endpoint**: `/api/donations/<id>/update-status/`
**Method**: POST
**Authentication**: Required (Admin only)
**Description**: Update the status of a donation

**Request Body**:
```json
{
  "status": "accepted"
}
```

**Response**:
```json
{
  "id": 1,
  "status": "accepted",
  "message": "Donation status updated successfully"
}
```

#### Discard Donation

**Endpoint**: `/api/donations/<id>/discard/`
**Method**: POST
**Authentication**: Required (Admin or donor owner)
**Description**: Cancel a donation

**Response**:
```json
{
  "success": true,
  "message": "Donation cancelled successfully"
}
```

### Assignments

#### List Assignments

**Endpoint**: `/api/assignments/`
**Method**: GET
**Authentication**: Required
**Description**: Get a list of delivery assignments

**Response**:
```json
[
  {
    "id": 1,
    "donation": {
      "id": 1,
      "food_type": "Fruits",
      "quantity": "5 kg",
      "pickup_address": "123 Main St, City"
    },
    "volunteer": {
      "id": 3,
      "username": "volunteer1"
    },
    "status": "assigned",
    "pickup_time": "2025-04-15T14:00:00Z",
    "delivery_time": null,
    "created_at": "2025-04-13T11:30:00Z"
  },
  // ... more assignments
]
```

#### Update Assignment Status

**Endpoint**: `/api/assignments/<id>/update-status/`
**Method**: POST
**Authentication**: Required (Admin or assigned volunteer)
**Description**: Update the status of an assignment

**Request Body**:
```json
{
  "status": "picked_up"
}
```

**Response**:
```json
{
  "id": 1,
  "status": "picked_up",
  "message": "Assignment status updated successfully"
}
```

#### Discard Assignment

**Endpoint**: `/api/assignments/<id>/discard/`
**Method**: POST
**Authentication**: Required (Admin only)
**Description**: Cancel a delivery assignment

**Response**:
```json
{
  "success": true,
  "message": "Assignment cancelled successfully"
}
```

### Volunteers

#### List Volunteers

**Endpoint**: `/api/volunteers/`
**Method**: GET
**Authentication**: Required (Admin only)
**Description**: Get a list of all volunteers

**Response**:
```json
[
  {
    "id": 1,
    "user": {
      "id": 3,
      "username": "volunteer1"
    },
    "phone": "+1234567890",
    "vehicle_type": "Car",
    "service_area": "Downtown",
    "availability": true,
    "created_at": "2025-04-10T09:15:00Z"
  },
  // ... more volunteers
]
```

#### Assign Delivery

**Endpoint**: `/api/assign-delivery/`
**Method**: POST
**Authentication**: Required (Admin only)
**Description**: Assign a donation to a volunteer for delivery

**Request Body**:
```json
{
  "donation_id": 1,
  "volunteer_id": 3
}
```

**Response**:
```json
{
  "id": 1,
  "donation": 1,
  "volunteer": 3,
  "status": "assigned",
  "pickup_time": "2025-04-15T14:00:00Z",
  "created_at": "2025-04-13T12:45:00Z",
  "message": "Delivery assigned successfully"
}
```

### Users

#### List Users

**Endpoint**: `/api/users/`
**Method**: GET
**Authentication**: Required (Admin only)
**Description**: Get a list of all user profiles

**Response**:
```json
[
  {
    "id": 1,
    "user": {
      "id": 1,
      "username": "admin"
    },
    "phone": "+9876543210",
    "address": "456 Admin St, City",
    "is_donor": false,
    "is_volunteer": false,
    "created_at": "2025-04-01T00:00:00Z"
  },
  // ... more user profiles
]
```

## Error Handling

All errors follow a standard format:

```json
{
  "error": true,
  "status_code": 400,
  "message": "Error description",
  "details": {} // Optional additional details
}
```

Common error status codes:
- 400: Bad Request (invalid input)
- 401: Unauthorized (authentication failed)
- 403: Forbidden (insufficient permissions)
- 404: Not Found (resource doesn't exist)
- 500: Server Error (something went wrong on our end)

## Rate Limiting

API requests are limited to 100 requests per hour per user. If you exceed this limit, you'll receive a 429 (Too Many Requests) response.

## Support

For API support or to report issues, please contact:
- Email: api-support@beyondhunger.org 