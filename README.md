
# Job Application Tracker API

A REST API to manage job applications, track their progress, and keep your job search organized.

Built with **FastAPI, PostgreSQL, and SQLAlchemy**, this project focuses on secure authentication and reliable application management.

## Features

- **Authentication:** User registration and login using JWT.
- **Application Management:** Create, view, update, and delete job applications.
- **Status Tracking:** Track applications through Applied, Interviewing, Offer, and Rejected.
- **Filtering:** Filter applications by status.
- **Application Details:** Store company names, job titles, salary ranges, job links, and notes.
- **Data Isolation:** Users can access only their own applications.
- **Database Migrations:** Manage schema changes with Alembic.
- **API Documentation:** Explore endpoints using Swagger UI.

## Tech Stack

- Python
- FastAPI
- PostgreSQL
- SQLAlchemy 2
- Pydantic v2
- Alembic
- JWT, Passlib, and bcrypt
- Uvicorn

## Getting Started

### Prerequisites

- Python 3.10+
- PostgreSQL
- Git

### 1. Clone the Repository

```bash
git clone https://github.com/Nimish077/Job-Application-Tracker.git
cd Job-Application-Tracker
```

### 2. Create a Virtual Environment

```bash
python -m venv .venv
```

Activate it on Windows:

```powershell
.venv\Scripts\Activate.ps1
```

On Linux or macOS:

```bash
source .venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Copy `.env.example` to `.env` and configure your PostgreSQL connection and JWT secret.

```env
DATABASE_URL=postgresql://USER:PASSWORD@HOST:5432/DATABASE_NAME
SECRET_KEY=your-generated-secret
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
ENV=development
DEBUG=False
CORS_ORIGINS=http://localhost:3000,http://localhost:5173
```

Generate a secure secret key:

```bash
python -c "import secrets; print(secrets.token_urlsafe(48))"
```

Replace the database placeholders with your actual credentials. Never commit your \`.env\` file or expose your secret key.

### 5. Apply Database Migrations

Make sure your PostgreSQL database exists, then run:

```bash
alembic upgrade head
```

### 6. Start the Server

```bash
uvicorn app.main:app --reload
```

The API will be available at:

- **Swagger UI:** http://127.0.0.1:8000/docs
- **ReDoc:** http://127.0.0.1:8000/redoc
- **Health Check:** http://127.0.0.1:8000/health

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| POST | \`/auth/register\` | Register a user |
| POST | \`/auth/login\` | Log in and receive a JWT |
| GET | \`/jobs/\` | List your applications |
| POST | \`/jobs/\` | Create an application |
| GET | \`/jobs/{job_id}\` | Retrieve an application |
| PUT | \`/jobs/{job_id}\` | Update an application |
| DELETE | \`/jobs/{job_id}\` | Delete an application |

All `/jobs` endpoints require a valid bearer token.

Filter applications by status using:

`GET /jobs/?status=Interviewing`

Supported statuses are `Applied`, `Interviewing`, `Offer`, and `Rejected`.

## Project Structure

```text
Job-Application-Tracker/
├── app/
│   ├── api/        # Authentication and job endpoints
│   ├── core/       # Configuration, database, and security
│   ├── models/     # SQLAlchemy models
│   ├── schemas/    # Pydantic schemas
│   └── main.py     # FastAPI entry point
├── alembic/        # Database migrations
├── specs/          # Project specifications
├── .env.example
├── alembic.ini
└── requirements.txt
```

## License

No license has been added yet.

EOF
