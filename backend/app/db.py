from fastapi import Request


def get_db(request: Request):
    session = request.app.state.sessionmaker()
    try:
        yield session
    finally:
        session.close()
