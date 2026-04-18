# Resume Screening System

A FastAPI-based Resume Screening System with JWT authentication, role-based access, multi-job-description screening

## What This Project Does

This project currently focuses on the backend API for a resume screening workflow:

- Users can sign up and log in
- Authenticated users can upload resumes in `PDF` or `DOCX` format
- Admin users can upload job descriptions
- Admin users can list uploaded job descriptions
- Admin users can run screening for a selected job description
- The system ranks resumes using:
  - sentence-embedding similarity
  - role-aware skill extraction
  - weighted skill matching

The repository also includes evaluation artifacts and datasets used for experimentation.

## Current Project Structure

```text
Resume Screening/
|-- backend/
|   |-- admin.py
|   |-- evaluation.py
|   |-- evaluation_results.csv
|   |-- README.md
|   |-- UpdatedResumeDataSet.csv
|   |-- resume_dataset.csv
|   |-- requirements.txt
|   `-- app/
|       |-- __init__.py
|       |-- database.py
|       |-- main.py
|       |-- models.py
|       |-- schemas.py
|       |-- routers/
|       |   |-- __init__.py
|       |   |-- auth_routes.py
|       |   |-- hr_routes.py
|       |   `-- user_routes.py
|       `-- services/
|           |-- __init__.py
|           |-- embedding.py
|           |-- filter.py
|           |-- filter_engine.py
|           |-- jd_parser.py
|           |-- resume_parser.py
|           |-- similarity.py
|           |-- skill_extractor.py
|           `-- text_extractor.py
|-- env/
|-- .gitignore
|-- PROJECT_IMPLEMENTATION_EXPLAINED.md
|-- PROJECT_KNOWLEDGE.md
|-- README.md
`-- requirements.txt
```

## Backend Overview

### Authentication and Authorization

Authentication is implemented in [auth_routes.py](/c:/Users/aabha/OneDrive/Desktop/Resume%20Screening/backend/app/routers/auth_routes.py:1).

- Passwords are hashed with `passlib` and `bcrypt`
- JWT tokens are generated with `python-jose`
- Access tokens expire after 60 minutes
- Protected routes use `OAuth2PasswordBearer`
- Signup creates accounts with role `user` by default
- Admin-only routes are protected through `require_admin`

### Data Model

The main SQLAlchemy models are defined in [models.py](/c:/Users/aabha/OneDrive/Desktop/Resume%20Screening/backend/app/models.py:1).

- `User`
  - `email`
  - `password`
  - `role`
- `JobDescription`
  - `file_path`
  - `min_cgpa`
  - `text`
  - `jd_skills`
- `Resume`
  - `file_path`
  - `extracted_text`
  - `cgpa`
  - `matched_skills`
  - `score`
  - `eligible`
  - `jd_id`

### File Handling

Resume and JD uploads currently:

- are stored under `backend/uploads/` when the server is run from the `backend` directory
- accept extracted text from `.pdf` and `.docx` files
- enforce a maximum upload size of `2 MB`

Text extraction is implemented in [text_extractor.py](/c:/Users/aabha/OneDrive/Desktop/Resume%20Screening/backend/app/services/text_extractor.py:1) using:

- `pdfplumber` for PDF files
- `python-docx` for DOCX files

## Screening Logic

The main screening route is implemented in [hr_routes.py](/c:/Users/aabha/OneDrive/Desktop/Resume%20Screening/backend/app/routers/hr_routes.py:1).

Current flow:

1. Admin selects a job description by `jd_id`
2. The system loads that JD and all uploaded resumes
3. The JD text is used to detect a likely role:
   - `software_engineer`
   - `product_manager`
   - `data_scientist`
4. Skills are extracted from the JD and each resume
5. JD and resume text are cleaned
6. Semantic similarity is computed with `all-MiniLM-L6-v2`
7. Weighted skill overlap is calculated
8. A final score is computed
9. Each resume is marked as `Eligible` or `Rejected`
10. Results are returned in descending score order

### Current Scoring Formula

The active scoring logic inside the screening route is:

```text
final_score = (0.6 * semantic_similarity) + (0.4 * skill_score)
```

Eligibility is currently based on screening reasons, including:

- semantic similarity below `0.5`
- missing JD skills

### Important Implementation Note

Although the project extracts `CGPA` from resumes and `min_cgpa` from job descriptions, the current `/hr/screen/{jd_id}` route does not use CGPA in the final score or rejection logic. That data is stored, but it is not actively applied in the final screening decision in the live route.

### Skill Extraction Notes

Role-aware skill extraction is implemented in [skill_extractor.py](/c:/Users/aabha/OneDrive/Desktop/Resume%20Screening/backend/app/services/skill_extractor.py:1).

- Skills are normalized before matching
- Some roles assign higher weights to more important skills
- Generic skills such as `python`, `java`, and `c` are intentionally ignored in extracted skill results
- Role detection defaults to `software_engineer` unless JD text indicates another supported role

## API Endpoints

### Auth

#### `POST /auth/signup`

Request body:

```json
{
  "email": "user@example.com",
  "password": "your-password"
}
```

Response:

- user id
- email
- role

#### `POST /auth/login`

Uses form data, not JSON.

Fields:

- `username`: user email
- `password`

Response:

```json
{
  "access_token": "<jwt>",
  "token_type": "bearer"
}
```

#### `GET /auth/test`

Simple test route to confirm auth router is active.

### User

#### `POST /user/upload-resume`

- requires a valid bearer token
- available to any authenticated user
- accepts a resume file upload
- extracts text
- extracts CGPA when present
- stores the resume in the database

Success response:

```json
{
  "message": "Resume uploaded successfully",
  "uploaded_by": "user@example.com"
}
```

### HR/Admin

#### `POST /hr/upload-jd`

- admin only
- uploads a JD file
- extracts text
- extracts minimum CGPA from the JD
- stores the job description

#### `GET /hr/jds`

### User View

- Upload Resume

### Admin View

- Upload JD
- View JD dropdown
- Select a JD
- Run screening
- View results table


## Installation

### 1. Create and activate virtual environment

Windows PowerShell:

```powershell
python -m venv env
.\env\Scripts\Activate.ps1
```

### 2. Install dependencies

From the project root:

```powershell
pip install -r requirements.txt
```

### 3. Configure PostgreSQL

The database connection is currently hardcoded in [database.py](/c:/Users/aabha/OneDrive/Desktop/Resume%20Screening/backend/app/database.py:1):

```python
DATABASE_URL = "postgresql://postgres:1234@localhost:5432/postgres"
```

Make sure:

- PostgreSQL is running
- the `postgres` database exists
- the username and password match your local PostgreSQL setup

### 4. Install any missing NLP/model dependencies if needed

The project depends on packages such as:

- `fastapi`
- `uvicorn`
- `sqlalchemy`
- `psycopg2-binary`
- `python-multipart`
- `sentence-transformers`
- `torch`
- `transformers`
- `spacy`
- `passlib[bcrypt]`
- `python-jose[cryptography]`

## Running the Backend

From the project root:

```powershell
cd backend
uvicorn app.main:app --reload
```

The app creates tables on startup through `Base.metadata.create_all(bind=engine)`.

Useful URLs:

- API base URL: `http://127.0.0.1:8000`
- Swagger UI: `http://127.0.0.1:8000/docs`
- ReDoc: `http://127.0.0.1:8000/redoc`

## Creating an Admin User

## Usage Flow

### Normal user

1. Sign up with `/auth/signup`
2. Log in with `/auth/login`
3. Upload a resume with `/user/upload-resume`

### Admin

1. Create or log in to an admin account
2. Upload one or more job descriptions with `/hr/upload-jd`
3. List available JDs with `/hr/jds`
4. Run screening with `/hr/screen/{jd_id}`
5. Review ranked results

## Evaluation and Dataset Files

The `backend/` directory also contains project experimentation files:

- [evaluation.py](/c:/Users/aabha/OneDrive/Desktop/Resume%20Screening/backend/evaluation.py:1)
- `evaluation_results.csv`
- `resume_dataset.csv`
- `UpdatedResumeDataSet.csv`

These support evaluation and offline analysis, but they are separate from the live API routes.

## Current Limitations

- Signup creates only normal users by default
- Admin users must currently be created or updated manually in the database
- Database migrations are not set up yet; tables are created using `Base.metadata.create_all()`



## Tech Stack

- FastAPI
- SQLAlchemy
- PostgreSQL
- JWT authentication
- Passlib + bcrypt
- python-jose
- pdfplumber
- python-docx
- sentence-transformers
- scikit-learn
- NumPy
- PyTorch
- Transformers
- spaCy

## Additional Documentation

- Internal knowledge notes: [PROJECT_KNOWLEDGE.md](/c:/Users/aabha/OneDrive/Desktop/Resume%20Screening/PROJECT_KNOWLEDGE.md:1)
- Implementation walkthrough: [PROJECT_IMPLEMENTATION_EXPLAINED.md](/c:/Users/aabha/OneDrive/Desktop/Resume%20Screening/PROJECT_IMPLEMENTATION_EXPLAINED.md:1)
