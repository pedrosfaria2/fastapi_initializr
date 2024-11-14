from fastapi import APIRouter


class GeneratorAPI:
    def __init__(self, app):
        self.router = APIRouter(prefix="/generator", tags=["Generator"])
        self._configure_routes()
        app.include_router(self.router)

    def _configure_routes(self):
        @self.router.post("/create")
        async def create_project():
            return {"message": "Project creation endpoint (not implemented yet)"}
