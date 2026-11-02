import argparse
import os
import uvicorn


def main():
    parser = argparse.ArgumentParser(description="Multi-Agent Platform Local Development Runner")
    parser.add_argument(
        "-e",
        "--env",
        choices=["dev", "prod", "staging", "test"],
        default=os.getenv("APP_ENV", "dev"),
        help="Target execution environment (default: $APP_ENV or 'dev')",
    )

    args = parser.parse_args()
    os.environ["APP_ENV"] = args.env

    # Import settings after environment variable is established
    from src.config import get_settings

    settings = get_settings()
    is_dev = settings.APP_ENV == "dev"
    host_display = "localhost" if settings.HOST in ("0.0.0.0", "127.0.0.1") else settings.HOST

    print(f"[run.py] Starting local Uvicorn server in {settings.APP_ENV.upper()} mode...")
    print(f"[run.py] Network Bind    : http://{settings.HOST}:{settings.PORT}")
    print(f"[run.py] Local Access    : http://{host_display}:{settings.PORT}")
    print(f"[run.py] Swagger UI Docs : http://{host_display}:{settings.PORT}/docs")
    uvicorn.run(
        "src.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=is_dev,
        log_level="info",
    )


if __name__ == "__main__":
    main()
