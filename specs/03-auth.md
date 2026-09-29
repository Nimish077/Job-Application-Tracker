# Authentication & Security Requirements

1. **Password Hashing:** Use `passlib` with `bcrypt` to hash user passwords before storing them.
2. **JWT Generation:** Implement an endpoint (`POST /auth/login` and `POST /auth/register`) that returns a JSON Web Token upon successful credentials verification.
3. **Protected Routes:** Create a FastAPI dependency (`get_current_user`) that:
   - Extracts the Bearer token from the `Authorization` header.
   - Decodes and verifies the JWT.
   - Queries the database to ensure the user exists.
   - Injects the current user object into protected route handlers.