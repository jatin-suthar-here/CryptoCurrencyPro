import uvicorn
from fastapi import FastAPI

app = FastAPI()


# Include routers
# .....


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8500)
