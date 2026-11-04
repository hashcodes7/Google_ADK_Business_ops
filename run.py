
import argparse
import uvicorn
from dotenv import load_dotenv

parser = argparse.ArgumentParser()

parser.add_argument(
    "--env",
    choices=["dev", "prod"],
    default="dev"
)

args = parser.parse_args()

load_dotenv(f"environments/.env.{args.env}", override=True)

if __name__ == "__main__":
    print(f"\n⚡ Starting Business Operations Backend ({args.env})")
    print("backend URL is : http://127.0.0.1:8000\n")
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=args.env == "dev"
    )
