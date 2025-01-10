import uvicorn, argparse
from fastapi import FastAPI
from api_endpoints.endpoints import home, fetch_source_data, filters
from utils import setup_database


app = FastAPI()


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

