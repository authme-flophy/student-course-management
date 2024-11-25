# API Documentation

## Overview

This API is built using Django REST Framework and provides a RESTful interface for managing courses, instructors, enrollments, and grades in an educational system.

## Authentication

The API uses JWT (JSON Web Token) Authentication implemented via `rest_framework_simplejwt`. All authenticated endpoints require a valid JWT token in the Authorization header:

```http
Authorization: Bearer <your_jwt_token>
```

### Getting Started

1. Register a new account
2. Login to receive your JWT tokens
3. Include the access token in subsequent requests

## Interactive Documentation

The API provides interactive documentation that can be accessed at:

- API Documentation: `/docs/`
- API Schema: `/schema/`
- OpenAPI Schema: `/schema.yaml`

## Core Models

### Course

- **Fields**:
  - `title` (string): Course title
  - `description` (text): Course description
  - `start_date` (date): Course start date
  - `end_date` (date): Course end date
  - `instructor` (foreign key): Reference to Instructor model

### Instructor

- **Fields**:
  - `user` (one-to-one): Reference to Django User model
  - `bio` (text): Instructor biography

### Enrollment

- **Fields**:
  - `student` (foreign key): Reference to User model
  - `course` (foreign key): Reference to Course model
  - `enrollment_date` (date): Auto-set enrollment date
- **Constraints**:
  - Unique together: student and course

### Grade

- **Fields**:
  - `enrollment` (foreign key): Reference to Enrollment model
  - `grade` (float): Numeric grade value
  - `date_received` (date): Auto-set date

## API Endpoints

### Authentication

#### Register User

- **URL**: `/api/auth/register/`
- **Method**: POST
- **Description**: Create a new user account
- **Request Body**:
  ```json
  {
    "username": "string",
    "email": "string",
    "password": "string",
    "user_type": "student|instructor",
    "first_name": "string (optional)",
    "last_name": "string (optional)"
  }
  ```
- **Response**: JWT tokens and user type

#### Login

- **URL**: `/api/auth/login/`
- **Method**: POST
- **Description**: Authenticate and receive JWT tokens
- **Request Body**:
  ```json
  {
    "username": "string",
    "password": "string"
  }
  ```
- **Response**: JWT access and refresh tokens

### Course Management

#### List/Create Courses

- **URL**: `/api/courses/`
- **Methods**: GET, POST
- **Authentication**: Required
- **Permissions**:
  - GET: Any authenticated user
  - POST: Instructors only
- **Request Body (POST)**:
  ```json
  {
    "title": "string",
    "description": "string",
    "start_date": "YYYY-MM-DD",
    "end_date": "YYYY-MM-DD"
  }
  ```

#### Course Detail

- **URL**: `/api/courses/{id}/`
- **Methods**: GET, PUT, PATCH, DELETE
- **Authentication**: Required
- **Permissions**:
  - GET: Any authenticated user
  - PUT/PATCH/DELETE: Course instructor only

### Enrollment Management

#### Enroll in Course

- **URL**: `/api/courses/{id}/enroll/`
- **Method**: POST
- **Authentication**: Required
- **Permission**: Students only

#### List User Enrollments

- **URL**: `/api/enrollments/`
- **Method**: GET
- **Authentication**: Required
- **Description**: Get list of authenticated user's enrolled courses

## Error Handling

The API uses standard HTTP status codes and returns error responses in the following format:

```json
{
  "error": "Error message",
  "code": "error_code",
  "details": {}
}
```

Common status codes:

- 200: Success
- 201: Created
- 400: Bad Request
- 401: Unauthorized
- 403: Forbidden
- 404: Not Found
- 500: Internal Server Error
