# SQR Voting System - Project Report

## Project Overview

The SQR Voting System is a web-based platform designed for creating, managing, and participating in surveys and polls. The system allows users to register, log in, create polls with single or multiple-choice answers, vote in polls, and view survey results. Authorized users can also close polls at any time or set a specific closing date for a poll.

## Team Members

* **Egor Hiskich** - Team Leader, Backend Developer
* **Almaz Gayazov** - Backend Developer, Tester
* **Renata Latypova** - Backend Developer, Tester
* **Artemij Volkonitin** - Tester
* **Julia Martynova** - Frontend Developer

## Project Setup and Installation

### Prerequisites

* Python 3.11+
* Poetry
* SQLite

### Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/Fridorovich/voting.git
   ```

2. Install dependencies:

   ```bash
   poetry install
   ```

3. Create a `.env` file with the following content:

   ```env
   DATABASE_URL=sqlite:///./sqr_voting.db
   SECRET_KEY=your-secret-key
   ALGORITHM=HS256
   ACCESS_TOKEN_EXPIRE_MINUTES=30
   REFRESH_TOKEN_EXPIRE_DAYS=7
   ```

4. Apply database migrations:

   ```bash
   alembic upgrade head
   ```

5. Run the server:

   ```bash
   uvicorn app.main:app --reload
   ```

6. Access documentation at:

   ```
   http://127.0.0.1:8000/docs
   ```

## Technical Stack

* **Python 3.11**
* **FastAPI** - Web framework
* **SQLite** - Database
* **Poetry** - Dependency management
* **Alembic** - Database migrations
* **JWT** - Authentication
* **Pytest** - Testing framework
* **Flake8, Bandit** - Code quality and security analysis
* **Streamlit** - Frontend

## Implementation Details

### Modules

* **Authentication Module:** User registration, login, token generation, and refresh mechanisms.
* **Voting Module:** Poll creation, voting, and result viewing.
* **Administration Module:** Poll management, closing polls, and setting poll expiration dates.

### Key Features

* User registration and authentication using JWT tokens.
* Poll creation with single/multiple choice options.
* Voting functionality with single-use voting and the ability to change votes.
* Poll closing by the creator or automatically based on set dates.
* Poll result viewing with real-time updates.
* Robust error handling and logging for all actions.

### Quality Requirements

* **Code Coverage:** 89% (exceeding the minimum requirement of 80%)
* **Maintainability Index:** 82
* **Compliance with PEP8:** 97%
* **Recovery Time (MTTR):** ≤ 15 minutes after critical failure
* **Performance:**

  * Poll creation: ≤ 500 ms
  * Voting: ≤ 300 ms
  * Result retrieval: ≤ 1 second
* **Security:**

  * Passwords are hashed using JWT and bcrypt.
  * Protection against SQL Injection and XSS.
  * All actions are logged for accountability.

## Testing

* **Test Coverage:** 89%
* **Unit Testing:** Pytest
* **Static Analysis:** Flake8, Bandit
* **Performance Testing:** Locust
* **Integration Testing:** Testing of all key API endpoints and services

## Lessons Learned

* Streamlining the development workflow using CI/CD pipelines.
* Implementing effective test coverage to ensure code reliability.
* Identifying and mitigating security vulnerabilities through automated scans.

## Future Improvements

* Implementing additional voting analytics.
* Adding email notifications for poll creators and voters.
* Enhancing the frontend with more interactive components.

## References

* [FastAPI Documentation](https://fastapi.tiangolo.com/)
* [Pytest Documentation](https://docs.pytest.org/)
* [SQLite Documentation](https://sqlite.org/docs.html)
