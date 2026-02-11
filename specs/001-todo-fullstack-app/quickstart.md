# Quickstart Guide: Todo Full-Stack Web Application

**Feature**: 001-todo-fullstack-app
**Date**: 2026-02-06
**Purpose**: Step-by-step setup instructions for local development

## Overview

This guide walks you through setting up the Todo Full-Stack Web Application locally. The application consists of two separate services:
- **Frontend**: Next.js 16+ (port 3000)
- **Backend**: FastAPI (port 8000)

**Estimated Setup Time**: 15-20 minutes

---

## Prerequisites

Before starting, ensure you have the following installed:

- **Node.js**: v18+ (for Next.js frontend)
- **npm** or **yarn**: Latest version
- **Python**: 3.11+ (for FastAPI backend)
- **pip**: Latest version
- **Git**: For cloning the repository
- **Neon Account**: Free account at [neon.tech](https://neon.tech)

---

## Step 1: Clone the Repository

```bash
git clone <repository-url>
cd hackathon_2_phase_2
git checkout 001-todo-fullstack-app
```

---

## Step 2: Set Up Neon PostgreSQL Database

### 2.1 Create Neon Project

1. Go to [neon.tech](https://neon.tech) and sign in
2. Click "Create Project"
3. Choose a project name (e.g., "todo-app")
4. Select a region closest to you
5. Click "Create Project"

### 2.2 Get Database Connection String

1. In your Neon dashboard, click on your project
2. Navigate to "Connection Details"
3. Copy the connection string (it looks like):
   ```
   postgresql://user:password@ep-xxx.region.aws.neon.tech/dbname?sslmode=require
   ```
4. Save this for Step 4

### 2.3 Create Database Tables

Run the following SQL in the Neon SQL Editor:

```sql
-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Create users table
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email VARCHAR(255) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE UNIQUE INDEX idx_user_email ON users(email);

-- Create tasks table
CREATE TABLE tasks (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    title VARCHAR(200) NOT NULL,
    description TEXT,
    is_completed BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_task_user_id ON tasks(user_id);
CREATE INDEX idx_task_user_created ON tasks(user_id, created_at DESC);
```

---

## Step 3: Generate JWT Secret

Generate a secure JWT secret key (minimum 32 characters):

```bash
# On Linux/Mac
openssl rand -hex 32

# On Windows (PowerShell)
[Convert]::ToBase64String((1..32 | ForEach-Object { Get-Random -Maximum 256 }))
```

**Save this secret** - you'll need it for both frontend and backend configuration.

---

## Step 4: Configure Backend Environment

### 4.1 Navigate to Backend Directory

```bash
cd backend
```

### 4.2 Create Virtual Environment

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Linux/Mac:
source venv/bin/activate

# On Windows:
venv\Scripts\activate
```

### 4.3 Install Dependencies

```bash
pip install -r requirements.txt
```

### 4.4 Create Environment File

Create `backend/.env` file:

```bash
# Copy example file
cp .env.example .env

# Edit .env file with your values
```

**backend/.env** contents:

```env
# Database Configuration
DATABASE_URL=postgresql+asyncpg://user:password@ep-xxx.region.aws.neon.tech/dbname?sslmode=require

# JWT Configuration
JWT_SECRET=<your-generated-secret-from-step-3>
JWT_ALGORITHM=HS256
JWT_EXPIRATION_HOURS=24

# CORS Configuration
FRONTEND_URL=http://localhost:3000

# Server Configuration
HOST=0.0.0.0
PORT=8000
```

**Important**: Replace `<your-generated-secret-from-step-3>` with the secret you generated in Step 3.

---

## Step 5: Configure Frontend Environment

### 5.1 Navigate to Frontend Directory

```bash
cd ../frontend
```

### 5.2 Install Dependencies

```bash
npm install
# or
yarn install
```

### 5.3 Create Environment File

Create `frontend/.env.local` file:

```bash
# Copy example file
cp .env.local.example .env.local

# Edit .env.local file with your values
```

**frontend/.env.local** contents:

```env
# API Configuration
NEXT_PUBLIC_API_URL=http://localhost:8000

# Better Auth Configuration
BETTER_AUTH_SECRET=<your-generated-secret-from-step-3>
BETTER_AUTH_URL=http://localhost:3000
```

**Critical**: The `BETTER_AUTH_SECRET` MUST be identical to the `JWT_SECRET` in the backend `.env` file.

---

## Step 6: Start the Application

### 6.1 Start Backend Server

In the `backend/` directory (with virtual environment activated):

```bash
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

You should see:
```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started reloader process
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

**Backend is now running at**: http://localhost:8000

### 6.2 Start Frontend Server

Open a **new terminal**, navigate to `frontend/` directory:

```bash
cd frontend
npm run dev
# or
yarn dev
```

You should see:
```
▲ Next.js 16.x.x
- Local:        http://localhost:3000
- Ready in X.Xs
```

**Frontend is now running at**: http://localhost:3000

---

## Step 7: Verify Installation

### 7.1 Check Backend Health

Open your browser and visit:
- **API Docs**: http://localhost:8000/docs
- You should see the FastAPI Swagger UI with all endpoints

### 7.2 Test Frontend

Open your browser and visit:
- **Frontend**: http://localhost:3000
- You should see the landing page

### 7.3 Test Authentication Flow

1. Click "Sign Up" on the landing page
2. Enter email: `test@example.com`
3. Enter password: `password123`
4. Click "Create Account"
5. You should be redirected to the dashboard

### 7.4 Test Task Creation

1. On the dashboard, click "Add Task"
2. Enter title: "Test Task"
3. Enter description: "This is a test"
4. Click "Save"
5. The task should appear in your task list

---

## Troubleshooting

### Backend Issues

**Problem**: `ModuleNotFoundError: No module named 'fastapi'`
- **Solution**: Ensure virtual environment is activated and dependencies are installed:
  ```bash
  source venv/bin/activate  # or venv\Scripts\activate on Windows
  pip install -r requirements.txt
  ```

**Problem**: `sqlalchemy.exc.OperationalError: could not connect to server`
- **Solution**: Check your `DATABASE_URL` in `backend/.env`:
  - Ensure the connection string is correct
  - Verify Neon database is running
  - Check SSL mode is set to `require`

**Problem**: `401 Unauthorized` on all API requests
- **Solution**: JWT secret mismatch between frontend and backend:
  - Verify `JWT_SECRET` in `backend/.env` matches `BETTER_AUTH_SECRET` in `frontend/.env.local`
  - Restart both servers after changing environment variables

### Frontend Issues

**Problem**: `Error: Cannot find module 'next'`
- **Solution**: Install dependencies:
  ```bash
  npm install
  # or
  yarn install
  ```

**Problem**: CORS errors in browser console
- **Solution**: Check `FRONTEND_URL` in `backend/.env` matches your frontend URL:
  - Should be `http://localhost:3000` for local development
  - Restart backend server after changing

**Problem**: "Network Error" when calling API
- **Solution**: Ensure backend is running and `NEXT_PUBLIC_API_URL` in `frontend/.env.local` is correct:
  - Should be `http://localhost:8000`
  - Check backend terminal for errors

### Database Issues

**Problem**: Tables don't exist
- **Solution**: Run the SQL migration script from Step 2.3 in Neon SQL Editor

**Problem**: "relation 'users' does not exist"
- **Solution**: Ensure you're connected to the correct database in Neon and tables were created successfully

---

## Development Workflow

### Making Changes

1. **Backend Changes**:
   - Edit files in `backend/src/`
   - FastAPI auto-reloads on file changes
   - Check terminal for errors

2. **Frontend Changes**:
   - Edit files in `frontend/src/`
   - Next.js auto-reloads on file changes
   - Check browser console for errors

### Testing

**Backend API Testing**:
```bash
cd backend
pytest
```

**Manual Testing**:
- Use FastAPI Swagger UI at http://localhost:8000/docs
- Test endpoints with different JWT tokens
- Verify user data isolation

### Stopping the Application

1. Press `CTRL+C` in the backend terminal
2. Press `CTRL+C` in the frontend terminal
3. Deactivate Python virtual environment:
   ```bash
   deactivate
   ```

---

## Environment Variables Reference

### Backend (.env)

| Variable | Description | Example |
|----------|-------------|---------|
| `DATABASE_URL` | Neon PostgreSQL connection string | `postgresql+asyncpg://...` |
| `JWT_SECRET` | Secret key for JWT signing | `abc123...` (32+ chars) |
| `JWT_ALGORITHM` | JWT signing algorithm | `HS256` |
| `JWT_EXPIRATION_HOURS` | Token expiration time | `24` |
| `FRONTEND_URL` | Frontend origin for CORS | `http://localhost:3000` |
| `HOST` | Backend server host | `0.0.0.0` |
| `PORT` | Backend server port | `8000` |

### Frontend (.env.local)

| Variable | Description | Example |
|----------|-------------|---------|
| `NEXT_PUBLIC_API_URL` | Backend API base URL | `http://localhost:8000` |
| `BETTER_AUTH_SECRET` | JWT secret (must match backend) | `abc123...` (32+ chars) |
| `BETTER_AUTH_URL` | Frontend base URL | `http://localhost:3000` |

---

## Next Steps

After successful setup:

1. **Review the codebase**:
   - Backend: `backend/src/`
   - Frontend: `frontend/src/`

2. **Read the documentation**:
   - [spec.md](./spec.md) - Feature specification
   - [plan.md](./plan.md) - Implementation plan
   - [data-model.md](./data-model.md) - Database schema
   - [contracts/](./contracts/) - API specifications

3. **Start implementing**:
   - Run `/sp.tasks` to generate implementation tasks
   - Follow the task breakdown for systematic development

4. **Test thoroughly**:
   - Test authentication flow
   - Test CRUD operations
   - Test user data isolation
   - Test error handling

---

## Support

If you encounter issues not covered in this guide:

1. Check the [spec.md](./spec.md) for requirements clarification
2. Review [research.md](./research.md) for technology decisions
3. Consult the API documentation at http://localhost:8000/docs
4. Check the browser console and backend terminal for error messages

---

## Security Checklist

Before deploying to production:

- [ ] Change JWT secret to a strong, randomly generated value
- [ ] Use HTTPS for all connections
- [ ] Update `FRONTEND_URL` and `BETTER_AUTH_URL` to production domains
- [ ] Enable Neon connection pooling
- [ ] Review CORS configuration
- [ ] Verify user data isolation in production
- [ ] Set up proper logging and monitoring
- [ ] Configure environment-specific `.env` files
