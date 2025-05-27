from .server import serve


def main():
    """MCP Check Server - CVE search and reporting functionality for MCP"""
    import asyncio
    asyncio.run(serve())


if __name__ == "__main__":
    main()
