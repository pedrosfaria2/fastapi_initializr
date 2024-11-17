# FastAPI Initializr

FastAPI Initializr is a tool to quickly generate and bootstrap new FastAPI projects. It aims to simplify the setup process by providing customizable project templates with common configurations and best practices.

## Features

- Generate FastAPI project structure
- Choose from different project templates
- Customize Python version, database, and other project settings
- Include optional features like Docker setup and database migrations
- Download generated project as a zip file

## Technologies Used

- **FastAPI**: Web framework for building APIs with Python
- **Pydantic**: Data validation and settings management using Python type annotations
- **Poetry**: Dependency management and packaging
- **Loguru**: Library for flexible logging
- **Jinja2**: Template engine for generating project files
- **Pytest**: Testing framework for Python
- **Docker**: Containerization platform
- **Docker Compose**: Tool for defining and running multi-container Docker applications

## Getting Started

### Prerequisites

- Python 3.10+
- Poetry
- Docker
- Docker Compose
- Make

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

Open your web browser and visit `http://localhost:8000/docs` to access the FastAPI Initializr Swagger.

### Other Commands

The `Makefile` provides additional commands for various tasks:

- `make test`: Run tests
- `make test-coverage`: Run tests and generate coverage report
- `make clean`: Clean the project

Refer to the `Makefile` for more details on each command.

### Generating a Project

1. Access the API at `/generator/create` endpoint
2. Provide a minimal configuration:
   ```json
   {
     "project_name": "my_fastapi_app",
     "description": "My FastAPI Application",
     "template_type": "minimal",
     "python_version": "3.10",
     "author": "Your Name",
     "fastapi_version": "0.100.0",
     "uvicorn_version": "0.22.0"
   }
   ```
3. You'll receive a ZIP file containing a minimal FastAPI project structure with:
   - main.py with basic endpoints
   - requirements.txt
   - README.md
   - .gitignore

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Acknowledgements

- [FastAPI](https://fastapi.tiangolo.com/)
- [Pydantic](https://pydantic-docs.helpmanual.io/)
- [Poetry](https://python-poetry.org/)
- [Jinja2](https://jinja.palletsprojects.com/)
