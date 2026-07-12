from contextlib import asynccontextmanager
from fastapi import FastAPI
from scalar_fastapi import get_scalar_api_reference
from app.database.session import create_table
from app.api.routers.base import router


async def lifespan_handler(app: FastAPI):
    await create_table()
    yield


app = FastAPI(lifespan=lifespan_handler)

app.include_router(router)

@app.get("/scalars", include_in_schema=False)
async def get_scalar_docs():
    return get_scalar_api_reference(
        openapi_url=app.openapi_url,
        title="Scalars API"
    )
