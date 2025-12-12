# Nexus Planner

Nexus Planner is a tool designed to help development teams and product managers make informed planning decisions. It provides a holistic view of your organization's codebase and team expertise, enabling you to analyze the impact of new features, identify risks, and optimize resource allocation.

## Features

- **Repository Dashboard**: Get a quick overview of all your repositories, including activity levels, commit history, and contributor statistics.
- **Person Dashboard**: Understand the knowledge distribution within your team, identify expertise, and spot potential knowledge concentration risks.
- **Planning Assistant**: Describe a new feature in natural language and receive an AI-powered analysis that includes:
    - Impacted repositories
    - Recommended team members
    - Potential risks
    - A suggested implementation order

## Quickstart

### Prerequisites

- Python 3.11+
- [uv](https://github.com/astral-sh/uv) (Python package manager)
- Node.js 18+ with pnpm
- Git

### Backend Setup

1.  **Initialize Backend Project and Install Dependencies**
    ```bash
    cd backend
    uv init
    uv add fastapi uvicorn pydantic pydantic-settings loguru
    uv add --dev pytest pytest-cov httpx mypy ruff
    ```

2.  **Create Environment File**

    ```bash
    cat <<EOF > .env
    # Server Configuration
    HOST=0.0.0.0
    PORT=8000
    DEBUG=true

    # CORS Configuration
    CORS_ORIGINS=http://localhost:8080

    # API Configuration
    API_V1_PREFIX=/api/v1
    EOF
    ```

3.  **Run the Backend Server**
    ```bash
    cd backend
    uv run uvicorn src.nexus_api.main:app --reload --host 0.0.0.0 --port 8000
    ```
    The backend API will be available at `http://localhost:8000`.

### Frontend Setup

1.  **Create Environment File**

    Create a file named `.env` in the `frontend` directory with the following content:

    ```env
    VITE_API_URL=http://localhost:8000/api/v1
    ```

2.  **Install Dependencies**
    ```bash
    cd frontend
    pnpm install
    ```

3.  **Run the Frontend Development Server**
    ```bash
    cd frontend
    pnpm dev
    ```
    The frontend will be available at `http://localhost:8080`.

## API Endpoints

The API provides the following endpoints, with mocked data for the initial prototype.

| Method | Endpoint                    | Description                                     |
| :----- | :-------------------------- | :---------------------------------------------- |
| `GET`  | `/api/v1/repositories`      | Retrieves a list of all repositories.           |
| `GET`  | `/api/v1/repositories/{id}` | Retrieves details for a specific repository.    |
| `GET`  | `/api/v1/people`            | Retrieves a list of all people.                 |
| `GET`  | `/api/v1/people/{id}`       | Retrieves details for a specific person.        |
| `POST` | `/api/v1/analysis`          | Analyzes a feature description (mocked response). |

You can explore the interactive API documentation (Swagger UI) at `http://localhost:8000/docs`.

## Running Tests and Code Quality Checks

### Backend

Navigate to the `backend` directory to run these commands.

-   **Run all tests:**
    ```bash
    uv run pytest
    ```
-   **Run tests with coverage report:**
    ```bash
    uv run pytest --cov=src/nexus_api --cov-report=term-missing
    ```
-   **Type-checking with mypy:**
    ```bash
    uv run mypy src/
    ```
-   **Linting with Ruff:**
    ```bash
    uv run ruff check src/
    ```
-   **Formatting with Ruff:**
    ```bash
    uv run ruff format src/
    ```