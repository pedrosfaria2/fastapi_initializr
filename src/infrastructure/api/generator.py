from fastapi import APIRouter, HTTPException, Response, FastAPI
from src.infrastructure.schemas.project import ProjectSchema
from src.application.services.project_service import ProjectService
from src.infrastructure.generators.jinja_project_generator import JinjaProjectGenerator
from src.infrastructure.repositories.jinja_template_repository import (
    JinjaTemplateRepository,
)


class GeneratorAPI:
    API_NAME = "generator"
    API_TAGS = ["Generator"]
    API_PREFIX = "/generator"

    def __init__(self, app: FastAPI):
        self.app = app
        self.router = APIRouter()

        template_repository = JinjaTemplateRepository()
        project_generator = JinjaProjectGenerator(template_repository)
        self.project_service = ProjectService(project_generator)

        self._register_routes()

    def _register_routes(self):
        self.router.add_api_route(
            path="/create",
            endpoint=self.create_project,
            methods=["POST"],
            summary="Generate a new FastAPI project",
            response_class=Response,
            response_description="ZIP file containing the generated project",
        )

        self.app.include_router(self.router, prefix=self.API_PREFIX, tags=self.API_TAGS)

    async def create_project(self, project_config: ProjectSchema):
        try:
            zip_content = await self.project_service.create_project(project_config)

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
