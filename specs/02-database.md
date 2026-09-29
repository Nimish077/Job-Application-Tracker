# Database Schema & Models

## 1. User Table (`users`)
- `id`: Integer (Primary Key, Auto-increment)
- `email`: String (Unique, Indexed, Non-nullable)
- `hashed_password`: String (Non-nullable)
- `created_at`: DateTime (Default: UTC now)

## 2. Job Application Table (`job_applications`)
- `id`: Integer (Primary Key, Auto-increment)
- `user_id`: Integer (Foreign Key referencing `users.id`, Non-nullable, Indexed for user isolation)
- `company_name`: String (Non-nullable)
- `position_title`: String (Non-nullable)
- `status`: Enum or String (Options: Applied, Interviewing, Offer, Rejected; Default: Applied)
- `salary_range`: String (Nullable)
- `job_url`: String (Nullable)
- `notes`: Text (Nullable)
- `created_at`: DateTime (Default: UTC now)
- `updated_at`: DateTime (Auto-updates on change)