from fastapi import APIRouter, HTTPException, Response
from src.infrastructure.schemas.project import ProjectSchema
from src.application.services.project_service import ProjectService
from src.infrastructure.services.jinja_project_generator import JinjaProjectGenerator
from src.infrastructure.repositories.jinja_template_repository import (
    JinjaTemplateRepository,
)


class GeneratorAPI:
    def __init__(self, app):
        self.router = APIRouter(prefix="/generator", tags=["Generator"])

        template_repository = JinjaTemplateRepository()
        project_generator = JinjaProjectGenerator(template_repository)
        self.project_service = ProjectService(project_generator)

        self._configure_routes()
        app.include_router(self.router)

    def _configure_routes(self):
        @self.router.post("/create")
        async def create_project(project_config: ProjectSchema):
            try:
                zip_content = self.project_service.create_project(project_config)

                return Response(
                    content=zip_content,
                    media_type="application/zip",
                    headers={
                        "Content-Disposition": f'attachment; filename="{project_config.project_name}.zip"'
                    },
                )

            except Exception as e:
                raise HTTPException(
                    status_code=500, detail=f"Failed to generate project: {str(e)}"
                )
