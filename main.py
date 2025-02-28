import uvicorn, argparse
import asyncio
from fastapi import FastAPI, WebSocket
from api_endpoints.endpoints import endpoints, auth_endpoints, home, filters
from utils import setup_database
from utils.redis import start_redis, stop_redis, check_redis_connection



async def app_lifespan(app: FastAPI):
    """ Lifespan event handler for FastAPI app startup and shutdown. """
    print("App is starting...")
    
    # Start Redis before app starts
    start_redis()
    check_redis_connection()

    # Startup logic
    # Populate API_SOURCE_DATA during startup of App (Server)
    await endpoints.fetch_source_data_from_api()  

    # # Start periodic task to fetch data every 15 minutes
    # app.state.periodic_task = asyncio.create_task(fetch_source_data.periodic_fetch_data())

    # Allows the app to start and wait for shutdown
    yield  

    # Shutdown logic (if needed)
    print("App is shutting down...")

    # Stop Redis server on FastAPI server stops
    # stop_redis()


# Pass the lifespan function to FastAPI
app = FastAPI(lifespan=app_lifespan)  


# Include routers
app.include_router(home.router)
app.include_router(endpoints.router, prefix="/api")
app.include_router(auth_endpoints.router, prefix="/auth")
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
        # setup_database.drop_database()
        # setup_database.create_tables()
    elif args.task == "server":
        uvicorn.run(app, host="0.0.0.0", port=8500)

