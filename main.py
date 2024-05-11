from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routers import base_api_router
from database.dbInit import connect, disconnect

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 允许的源
    allow_credentials=True,  # 允许跨域请求携带cookies
    allow_methods=["*"],  # 允许的请求方法
    allow_headers=["*"],  # 允许的请求头
)


@app.on_event("startup")
async def startup_event():
    await connect()


@app.on_event("shutdown")
async def shutdown_event():
    await disconnect()


app.include_router(base_api_router)
