# Configuration, Environment, and Deployment

## Environment Variables (`.env.example`)
Create a `.env.example` file with blank/dummy placeholder values for the following:
```env
DATABASE_URL=postgresql://user:password@localhost:5432/dbname
SECRET_KEY=your_super_secret_key_here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30