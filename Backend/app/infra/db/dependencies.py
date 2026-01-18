from fastapi import Request

# Dependency to get DB session
async def get_db(request: Request):
    async with request.app.state.session() as db:
        yield db
