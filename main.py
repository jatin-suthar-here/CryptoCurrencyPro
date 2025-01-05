import uvicorn
from fastapi import FastAPI
from endpoints import home, fetch_source_data


app = FastAPI()


# Include routers
app.include_router(home.router)
app.include_router(fetch_source_data.router, prefix="/api")


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8500)
