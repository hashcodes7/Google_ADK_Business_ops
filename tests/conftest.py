import os
from pathlib import Path
import pytest
from dotenv import load_dotenv


def pytest_addoption(parser):
    """Register custom CLI options for pytest."""
    parser.addoption(
        "--env-file",
        action="store",
        default=None,
        help="Path to environment file (e.g. environments/.env.dev, environments/.env.prod, or 'dev', 'prod')",
    )


def pytest_configure(config):
    """
    Called before test collection starts.
    Loads the specified environment file so that Settings and modules
    initialize with the desired environment credentials.
    """
    env_opt = config.getoption("--env-file")

    env_path = None
    if env_opt:
        if env_opt in ("dev", "prod", "example"):
            candidate = Path(f"environments/.env.{env_opt}")
        else:
            candidate = Path(env_opt)
        env_path = candidate
    elif os.getenv("ENV_FILE"):
        env_path = Path(os.getenv("ENV_FILE"))
    elif Path("environments/.env.dev").exists():
        env_path = Path("environments/.env.dev")
    elif Path("environments/.env.example").exists():
        env_path = Path("environments/.env.example")

    if env_path and env_path.exists():
        load_dotenv(dotenv_path=env_path, override=True)
        # Normalize environment variable aliases across dev/prod:
        if os.getenv("Gemini_API_KEY") and not os.getenv("GOOGLE_API_KEY"):
            os.environ["GOOGLE_API_KEY"] = os.getenv("Gemini_API_KEY")
        if os.getenv("GOOGLE_API_KEY") and not os.getenv("Gemini_API_KEY"):
            os.environ["Gemini_API_KEY"] = os.getenv("GOOGLE_API_KEY")
        if os.getenv("ECOMMERCE_API_BASE_URL") and not os.getenv("ECOMMERCE_API_URL"):
            os.environ["ECOMMERCE_API_URL"] = os.getenv("ECOMMERCE_API_BASE_URL")
        # Suppress verbose background app logs during test execution:
        os.environ["LOG_LEVEL"] = "WARNING"
    elif env_opt:
        print(f"\n[pytest] WARNING: Requested env file '{env_opt}' not found.")
