import os
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from . import auth, content, terminal
from .access import allowed_ips, client_ip, ip_allowed, is_admin_request
from .migrations import run_migrations
from .models import Base
from .seed import seed_if_empty, seed_terminal_if_empty

BACKEND_DIR = Path(__file__).resolve().parent.parent


def create_app() -> FastAPI:
    db_path = Path(os.environ.get("DB_PATH", BACKEND_DIR / "data" / "content.db"))
    seed_path = Path(
        os.environ.get("SEED_PATH", BACKEND_DIR.parent / "shared" / "seed_content.json")
    )
    terminal_seed_path = Path(
        os.environ.get(
            "SEED_TERMINAL_PATH", BACKEND_DIR.parent / "shared" / "seed_terminal.json"
        )
    )

    db_path.parent.mkdir(parents=True, exist_ok=True)
    engine = create_engine(
        f"sqlite:///{db_path}", connect_args={"check_same_thread": False}
    )
    Base.metadata.create_all(engine)

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        with app.state.sessionmaker() as session:
            seed_if_empty(session, seed_path)
            run_migrations(session)
            seed_terminal_if_empty(session, terminal_seed_path)
        yield

    app = FastAPI(
        title="atrice-landing",
        lifespan=lifespan,
        docs_url=None,
        redoc_url=None,
        openapi_url=None,
    )
    app.state.sessionmaker = sessionmaker(bind=engine)
    app.state.admin_password = os.environ.get("ADMIN_PASSWORD", "admin")
    app.state.secret_key = os.environ.get("SECRET_KEY", "dev-secret-change-me")

    app.include_router(content.router)
    app.include_router(auth.router)
    app.include_router(terminal.router)

    allowed = allowed_ips()
    if allowed:

        @app.middleware("http")
        async def admin_gate(request: Request, call_next):
            if is_admin_request(request) and not ip_allowed(client_ip(request), allowed):
                return JSONResponse({"detail": "Not Found"}, status_code=404)
            return await call_next(request)

    static_dir = os.environ.get("STATIC_DIR", "")
    if static_dir and Path(static_dir).is_dir():
        static_root = Path(static_dir).resolve()
        app.mount("/assets", StaticFiles(directory=static_root / "assets"), name="assets")

        @app.get("/{path:path}", include_in_schema=False)
        def spa(path: str):
            if path:
                candidate = (static_root / path).resolve()
                try:
                    candidate.relative_to(static_root)
                except ValueError:
                    return FileResponse(static_root / "index.html")
                if candidate.is_file():
                    return FileResponse(candidate)
            return FileResponse(static_root / "index.html")

    return app


app = create_app()
