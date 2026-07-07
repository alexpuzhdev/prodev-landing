import os
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from . import auth, content
from .models import Base
from .seed import seed_if_empty

BACKEND_DIR = Path(__file__).resolve().parent.parent


def create_app() -> FastAPI:
    db_path = Path(os.environ.get("DB_PATH", BACKEND_DIR / "data" / "content.db"))
    seed_path = Path(
        os.environ.get("SEED_PATH", BACKEND_DIR.parent / "shared" / "seed_content.json")
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
        yield

    app = FastAPI(title="prodev-landing", lifespan=lifespan)
    app.state.sessionmaker = sessionmaker(bind=engine)
    app.state.admin_password = os.environ.get("ADMIN_PASSWORD", "admin")
    app.state.secret_key = os.environ.get("SECRET_KEY", "dev-secret-change-me")

    app.include_router(content.router)
    app.include_router(auth.router)
    return app


app = create_app()
