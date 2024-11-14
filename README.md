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

### Generating a Project (not implemented yet)

1. Select a project template from the available options.
2. Customize the project settings such as Python version, database, Docker setup, etc.
3. Generate the project.
4. Download the generated project as a zip file.
5. Extract the downloaded zip file and follow the project-specific instructions in its README to set up and run the generated FastAPI project.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Acknowledgements

- [FastAPI](https://fastapi.tiangolo.com/)
- [Pydantic](https://pydantic-docs.helpmanual.io/)
- [Poetry](https://python-poetry.org/)
- [Jinja2](https://jinja.palletsprojects.com/)
