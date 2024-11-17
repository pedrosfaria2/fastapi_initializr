from pathlib import Path
import io
from zipfile import ZipFile
from loguru import logger
from src.domain.entities.project import Project
from src.domain.services.project_generator import ProjectGenerator
from src.domain.repositories.template_repository import TemplateRepository


class JinjaProjectGenerator(ProjectGenerator):
    def __init__(self, template_repository: TemplateRepository):
        self.template_repository = template_repository

    def generate(self, project: Project, output_path: Path) -> bytes:
        try:
            template_files = self.template_repository.get_template_files(
                project.template_type
            )
            if not template_files:
                raise ValueError(
                    f"No templates found for type: {project.template_type}"
                )

            if project.include_dockerfile:
                template_files["docker/Dockerfile"] = "docker/Dockerfile.jinja"

            if project.include_docker_compose:
                template_files["docker/docker-compose.yml"] = (
                    "docker/docker-compose.yml.jinja"
                )

            template_files["README.md"] = "readme/README.md.jinja"

            context = {
                "project_name": project.name,
                "description": project.description,
                "python_version": project.python_version,
                "author": project.author,
                "fastapi_version": project.dependencies["fastapi"],
                "uvicorn_version": project.dependencies["uvicorn"],
                "include_dockerfile": project.include_dockerfile,
                "include_docker_compose": project.include_docker_compose,
            }

            zip_buffer = io.BytesIO()
            with ZipFile(zip_buffer, "w") as zip_file:
                for dest_path, template_path in template_files.items():
                    try:
                        template = self.template_repository.get_template_content(
                            template_path
                        )
                        content = template.render(**context)

                        zip_file.writestr(dest_path, content)
                    except Exception as e:
                        logger.error(
                            f"Failed to process template {template_path}: {str(e)}"
                        )
                        raise ValueError(f"Failed to process template {template_path}")

            zip_buffer.seek(0)
            return zip_buffer.getvalue()

        except Exception as e:
            logger.error(f"Project generation failed: {str(e)}")
            raise RuntimeError(f"Failed to generate project: {str(e)}")
