# API Documentation

## Overview

This API is built using Django REST Framework and provides a RESTful interface for [brief description of what the API does].

## Authentication

The API uses JWT (JSON Web Token) Authentication. This is implemented using the rest_framework_simplejwt library.

## API Schema & Interactive Documentation

The API provides interactive documentation that can be accessed at:

- API Documentation: `/docs/`
- API Schema: `/schema/`

## Making Requests

### HTTP Methods

The API supports the following HTTP methods:

- GET: Retrieve resources
- POST: Create new resources
- PUT/PATCH: Update existing resources
- DELETE: Remove resources

### Request Format

API requests should include:

- Content-Type: `application/json`
- Authentication headers (if required)

### Response Format

Responses are returned in JSON format with appropriate HTTP status codes.

## Models

### Course

- **Fields**:
  - title (CharField): Course title
  - description (TextField): Course description
  - start_date (DateField): Course start date
  - end_date (DateField): Course end date
  - instructor (ForeignKey): Reference to Instructor model

### Instructor

- **Fields**:
  - user (OneToOneField): Reference to Django User model
  - bio (TextField): Instructor biography

### Enrollment

- **Fields**:
  - student (ForeignKey): Reference to User model
  - course (ForeignKey): Reference to Course model
  - enrollment_date (DateField): Auto-set enrollment date
- **Constraints**:
  - Unique together: student and course

### Grade

- **Fields**:
  - enrollment (ForeignKey): Reference to Enrollment model
  - grade (FloatField): Numeric grade value
  - date_received (DateField): Auto-set date

## Endpoints

### Documentation Endpoints

#### Get API Documentation

- **URL**: `/docs/`
- **Method**: GET
- **Description**: Returns interactive HTML documentation for the entire API
- **Response Format**: HTML documentation page
- **Authentication**: Optional

#### Get API Schema

- **URL**: `/schema/`
- **Method**: GET
- **Description**: Returns the OpenAPI/CoreAPI schema definition
- **Response Format**: JSON schema
- **Authentication**: Optional

#### Get Schema JavaScript

- **URL**: `/schema.js`
- **Method**: GET
- **Description**: Returns JavaScript file containing the API schema
- **Response Format**: JavaScript file
- **Authentication**: Optional

### Authentication Endpoints

#### Register User

- **URL**: `/api/auth/register/`
- **Method**: POST
- **Description**: Create a new user account (student or instructor)
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
- **Response**: Returns JWT tokens on successful registration
  ```json
  {
    "refresh": "string",
    "access": "string",
    "user_type": "string"
  }
  ```

#### Login

- **URL**: `/api/auth/login/`
- **Method**: POST
- **Description**: Authenticate user and receive JWT tokens
- **Request Body**:
  ```json
  {
    "username": "string",
    "password": "string"
  }
  ```
- **Response**: Returns JWT tokens
  ```json
  {
    "refresh": "string",
    "access": "string"
  }
  ```

### Course Management

#### List/Create Courses

- **URL**: `/api/courses/`
- **Methods**: GET, POST
- **Authentication**: JWT Authentication
- **Permissions**:
  - GET: Any user can view
  - POST: Instructor only
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
- **Authentication**: JWT Authentication
- **Permissions**:
  - GET: Any user can view
  - PUT/PATCH/DELETE: Course instructor only

#### Course Enrollments

- **URL**: `/api/courses/{id}/enrollments/`
- **Method**: GET
- **Authentication**: JWT Authentication
- **Description**: Get list of enrollments for a specific course
- **Response**: Includes course details with enrolled students

#### Enroll in Course

- **URL**: `/api/courses/{id}/enroll/`
- **Method**: POST
- **Authentication**: JWT Authentication
- **Permission**: Authenticated users only

### Enrollment Management

#### List Enrollments

- **URL**: `/api/enrollments/`
- **Method**: GET
- **Description**: Get list of user's enrolled courses
- **Response Format**: JSON
- **Authentication**: Required

## Examples

### Using cURL
