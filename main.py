import uvicorn, argparse
import asyncio
from fastapi import FastAPI, WebSocket
from api_endpoints.endpoints import home, fetch_source_data, filters
from utils import setup_database


async def app_lifespan(app: FastAPI):
    """ Lifespan event handler for FastAPI app startup and shutdown. """
    print("App is starting...")
    
    # Startup logic
    # Populate API_SOURCE_DATA during startup of App (Server)
    await fetch_source_data.fetch_source_data_from_api()  

    # # Start periodic task to fetch data every 15 minutes
    # app.state.periodic_task = asyncio.create_task(fetch_source_data.periodic_fetch_data())

    # Allows the app to start and wait for shutdown
    yield  

    # Shutdown logic (if needed)
    print("App is shutting down...")


# Pass the lifespan function to FastAPI
app = FastAPI(lifespan=app_lifespan)  


# Include routers
app.include_router(home.router)
app.include_router(fetch_source_data.router, prefix="/api")
app.include_router(filters.router, prefix="/api")


if __name__ == "__main__":
    # Create the argument parser
    parser = argparse.ArgumentParser(description="Run setup-db or start the server.")

    # Add arguments
    parser.add_argument(
        "--task",
        choices=["setup", "server"],
        required=True,
        help="Choose 'setup' to setup the database or 'serve' to start the fastapi server.",
    )

    # Parse arguments
    args = parser.parse_args()

    # Run based on the provided argument
    if args.task == "setup":
        setup_database.reset_database()
    elif args.task == "server":
        uvicorn.run(app, host="0.0.0.0", port=8500)

