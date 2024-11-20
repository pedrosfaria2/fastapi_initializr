# FastAPI Initializr

FastAPI Initializr is a tool to quickly generate and bootstrap new FastAPI projects. It aims to simplify the setup process by providing customizable project templates with common configurations and best practices.

## Features

- Generate FastAPI project structure
- Choose from different project templates
- Customize Python version, database, and other project settings
- Include optional features like Docker setup and database migrations
- Support for both `pip` and `Poetry` as dependency managers
- Pre-configured utilities like `black`, `flake8`, `pre-commit`, and `commitizen`
- Download generated project as a zip file

## Technologies Used

- **FastAPI**: Web framework for building APIs with Python
- **Pydantic**: Data validation and settings management using Python type annotations
- **Poetry**: Dependency management and packaging
- **pip**: Standard Python package installer
- **Loguru**: Library for flexible logging
- **Jinja2**: Template engine for generating project files
- **Pytest**: Testing framework for Python
- **Docker**: Containerization platform
- **Docker Compose**: Tool for defining and running multi-container Docker applications

## Getting Started

### Prerequisites

- Python 3.10+
- `pip` or `Poetry`
- Docker (optional)
- Docker Compose (optional)
- Make (optional)

### Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/pedrosfaria2/fastapi_initializr.git
   cd fastapi_initializr
   ```

2. Install dependencies and set up the environment:

   ```bash
   make setup
   ```

## Usage

### Running the Application

To start the FastAPI server, use one of the following commands:

- Run the application directly:

  ```bash
  make run
  ```

- Run the application using Docker:

  ```bash
  make run-docker
  ```

- Run the application using Docker Compose (for development):

  ```bash
  make run-compose
  ```

Open your web browser and visit `http://localhost:8001/docs` to access the FastAPI Initializr Swagger.

### Generating a Project

1. Access the API at `/generator/create` endpoint.
2. Provide a configuration payload. Example:
   ```json
   {
     "project_name": "my_fastapi_app",
     "description": "My FastAPI Application",
     "template_type": "minimal",
     "python_version": "3.10",
     "author": "Your Name",
     "fastapi_version": "0.100.0",
     "uvicorn_version": "0.22.0",
     "dependency_manager": "poetry",
     "include_dockerfile": false,
     "include_docker_compose": false,
     "include_black": true,
     "include_flake8": true,
     "include_pre_commit": true,
     "include_conventional_commit": true
   }
   ```
3. The generated ZIP file will include a structured FastAPI project with:
   - `main.py` with basic endpoints
   - `requirements.txt` or `pyproject.toml`
   - `README.md`
   - `.gitignore`
   - Optional Dockerfile and/or docker-compose.yml
   - Pre-configured utilities

## Dependency Management

FastAPI Initializr supports both `pip` and `Poetry` for managing dependencies. The choice of manager is specified in the configuration (`dependency_manager`).

### Using `pip`

If `pip` is selected:
- A `requirements.txt` file will be generated.
- Install dependencies with:
  ```bash
  pip install -r requirements.txt
  ```

### Using `Poetry`

If `Poetry` is selected:
- A `pyproject.toml` file will be generated.
- Install dependencies with:
  ```bash
  poetry install
  ```

## Utilities

This tool provides pre-configured utilities to help maintain code quality and enforce standards:

- **Black**: Code formatter. Run:
  ```bash
  black .
  ```

- **Flake8**: Linter for Python. Run:
  ```bash
  flake8 .
  ```

- **Pre-Commit**: Runs checks before commits. Install hooks:
  ```bash
  pre-commit install
  ```

- **Commitizen**: For conventional commits. Make a commit:
  ```bash
  cz commit
  ```

These utilities are included in the generated project if enabled in the configuration.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Acknowledgements

- [FastAPI](https://fastapi.tiangolo.com/)
- [Pydantic](https://pydantic-docs.helpmanual.io/)
- [Poetry](https://python-poetry.org/)
- [Jinja2](https://jinja.palletsprojects.com/)
- [Black](https://github.com/psf/black)
- [Flake8](https://flake8.pycqa.org/)
- [Pre-Commit](https://pre-commit.com/)
- [Commitizen](https://commitizen-tools.github.io/commitizen/)
