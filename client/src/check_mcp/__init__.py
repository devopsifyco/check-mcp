from .server import serve
import os


def main():
    """MCP Check Server - Check CVE functionality for MCP
    The API key is read from the CHECK_API_KEY environment variable by default.
    """
    import argparse
    import asyncio

    parser = argparse.ArgumentParser(
        description="give a model the ability to make web requests"
    )
    parser.add_argument("--apikey", type=str, default=os.getenv("CHECK_API_KEY"), help="API key to use for requests")

    args = parser.parse_args()
    if not args.apikey:
        raise RuntimeError("API key must be provided via --apikey or CHECK_API_KEY environment variable.")
    asyncio.run(serve(args.apikey))


if __name__ == "__main__":
    main()
