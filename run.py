
import pathlib
import argparse
import uvicorn
from dotenv import load_dotenv

parser = argparse.ArgumentParser()
parser.add_argument("--env", choices=["dev", "prod"], default="dev")
parser.add_argument("--host", default="0.0.0.0")
parser.add_argument("--port", type=int, default=8000)
args = parser.parse_args()

load_dotenv(f"environments/.env.{args.env}", override=True)

if __name__ == "__main__":
    frontend_uri = pathlib.Path("frontend/index.html").resolve().as_uri()
    display_host = "127.0.0.1" if args.host == "0.0.0.0" else args.host

    print(f"\n Starting Business Operations Backend ({args.env})")
    print(f"backend URL is : \033[1mhttp://{display_host}:{args.port}\033[0m")
    print(f"frontend URL is : \033[1m{frontend_uri}\033[0m\n")

    uvicorn.run("app.main:app", host=args.host, port=args.port, reload=args.env == "dev")
