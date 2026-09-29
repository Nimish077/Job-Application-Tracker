# API Endpoints Specification

## Authentication (`/auth`)
- `POST /auth/register`: Register a new user. Validates email uniqueness and hashes password.
- `POST /auth/login`: Authenticate user and return a JWT access token.

## Job Applications (`/jobs` - All routes protected)
- `GET /jobs/`: Retrieve all job applications belonging *only* to the authenticated user. Support optional query filters (e.g., status).
- `POST /jobs/`: Create a new job application tied automatically to the authenticated `user_id`.
- `GET /jobs/{id}`: Retrieve a single application by ID (ensure it belongs to the current user).
- `PUT /jobs/{id}`: Update an existing application (ensure ownership).
- `DELETE /jobs/{id}`: Delete an application (ensure ownership).