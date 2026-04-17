# Resume Screening System

A FastAPI-based Resume Screening System with JWT authentication, role-based access, multi-job-description screening, and a lightweight browser frontend.

## Features

- User signup and login with JWT authentication
- Role-based access:
  - `user` can upload resumes
  - `admin` can upload job descriptions and run screening
- Resume upload and text extraction
- Job description upload and storage
- Support for multiple job descriptions
- Resume screening against a selected JD
- Screening based on:
  - CGPA filtering
  - skill matching
  - semantic similarity using sentence embeddings
- Simple frontend for login, uploads, JD selection, and result viewing

## Project Structure

```text
Resume Screening/
├── backend/
│   └── app/
│       ├── main.py
│       ├── database.py
│       ├── models.py
│       ├── schemas.py
│       ├── routers/
│       │   ├── auth_routes.py
│       │   ├── hr_routes.py
│       │   └── user_routes.py
│       └── services/
├── frontend/
│   ├── index.html
│   ├── app.js
│   ├── style.css
│   └── src/
│       ├── App.js
│       ├── pages/
│       ├── components/
│       └── services/
├── requirements.txt
├── PROJECT_KNOWLEDGE.md
└── README.md
```

## Backend Overview

### Authentication

Authentication is implemented in `backend/app/routers/auth_routes.py`.

- Password hashing uses `passlib` with `bcrypt`
- JWT token generation and verification uses `python-jose`
- Token expiry is set to 1 hour
- `OAuth2PasswordBearer` is used for protected endpoints

### Roles

- `user`
  - can access `/user/upload-resume`
- `admin`
  - can access `/hr/upload-jd`
  - can access `/hr/jds`
  - can access `/hr/screen/{jd_id}`

Note:
- Signup currently creates users with role `user` by default
- To test admin features, at least one account must have `role = "admin"` in the database

### Resume Screening Logic

The screening flow is implemented in `backend/app/routers/hr_routes.py` and uses existing service functions without changing the scoring logic.

Main steps:

1. Select a job description by `jd_id`
2. Load all resumes from the database
3. Clean JD and resume text
4. Apply rule-based filters
5. Compute semantic similarity
6. Calculate final score
7. Return sorted results

## API Endpoints

### Auth

- `POST /auth/signup`
  - request body: JSON
  - fields:
    - `email`
    - `password`

- `POST /auth/login`
  - request body: form data
  - fields:
    - `username` = user email
    - `password`
  - response:
    - `access_token`
    - `token_type`

### User

- `POST /user/upload-resume`
  - protected
  - requires `Authorization: Bearer <token>`
  - upload a PDF or DOCX resume

### HR/Admin

- `POST /hr/upload-jd`
  - admin only
  - upload a JD file

- `GET /hr/jds`
  - admin only
  - returns all uploaded JDs

- `GET /hr/screen/{jd_id}`
  - admin only
  - screens all resumes against the selected JD

## Frontend Overview

The frontend is a simple browser-based app inside the existing `frontend/` folder.

Main flow:

1. Open `frontend/index.html`
2. Login using email and password
3. Token is stored in `localStorage`
4. UI changes based on role

### User View

- Upload Resume

### Admin View

- Upload JD
- View JD dropdown
- Select a JD
- Run screening
- View results table

## Frontend Files

- `frontend/index.html`
  - app entry page

- `frontend/app.js`
  - bootstraps the frontend

- `frontend/src/App.js`
  - chooses login or dashboard view

- `frontend/src/pages/Login.js`
  - handles login form

- `frontend/src/pages/Dashboard.js`
  - renders role-based dashboard

- `frontend/src/components/UploadResume.js`
  - resume upload UI

- `frontend/src/components/UploadJD.js`
  - JD upload UI

- `frontend/src/components/JDSelector.js`
  - fetches all JDs and shows dropdown

- `frontend/src/components/ResultsTable.js`
  - fetches and renders screening results

- `frontend/src/services/api.js`
  - stores token, builds auth headers, and makes API calls

## Installation

### 1. Create and activate virtual environment

Windows PowerShell:

```powershell
python -m venv env
.\env\Scripts\Activate.ps1
```

### 2. Install dependencies

```powershell
pip install -r requirements.txt
```

If your auth packages are not installed yet, also install:

```powershell
pip install passlib[bcrypt] python-jose[cryptography]
```

### 3. Configure database

The current database URL is defined in [backend/app/database.py](/c:/Users/aabha/OneDrive/Desktop/Resume%20Screening/backend/app/database.py:1):

```python
DATABASE_URL = "postgresql://postgres:1234@localhost:5432/postgres"
```

Make sure:

- PostgreSQL is running
- the database exists
- the username/password match your local setup

## Running the Backend

From the project root:

```powershell
cd backend
uvicorn app.main:app --reload
```

Backend base URL:

```text
http://127.0.0.1:8000
```

Swagger docs:

```text
http://127.0.0.1:8000/docs
```

## Running the Frontend

The frontend is plain HTML, CSS, and JavaScript modules.

Simplest option:

1. Open [frontend/index.html](/c:/Users/aabha/OneDrive/Desktop/Resume%20Screening/frontend/index.html:1) in a browser

Better option using a local static server:

```powershell
cd frontend
python -m http.server 5500
```

Then open:

```text
http://127.0.0.1:5500
```

## Usage Flow

### Normal user

1. Sign up or log in
2. Upload resume

### Admin

1. Log in with an admin account
2. Upload one or more job descriptions
3. Select a JD from the dropdown
4. Click `Run Screening`
5. Review the ranked results

## Important Notes

- Job descriptions are now screened by `jd_id`, so admins can manage multiple JDs
- The screening logic itself was kept unchanged
- Uploaded files are stored in the `uploads/` folder
- Login currently expects form data, not JSON
- Role is read from the JWT payload in the frontend

## Current Limitations

- Signup creates only normal users by default
- Admin users must currently be created or updated manually in the database
- Frontend is intentionally simple and focused on working flow, not advanced styling
- Database migrations are not set up yet; tables are created using `Base.metadata.create_all()`

## Documentation

- Detailed internal explanation: [PROJECT_KNOWLEDGE.md](/c:/Users/aabha/OneDrive/Desktop/Resume%20Screening/PROJECT_KNOWLEDGE.md:1)

## Tech Stack

- FastAPI
- SQLAlchemy
- PostgreSQL
- JWT
- Passlib + bcrypt
- python-jose
- pdfplumber
- python-docx
- sentence-transformers
- HTML
- CSS
- JavaScript
