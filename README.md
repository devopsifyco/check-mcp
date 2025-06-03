# Check MCP: Model Context Protocol Server & Client

[![Build & Deploy MCP Artifacts](https://github.com/devopsifyco/check-mcp/actions/workflows/main.yml/badge.svg)](../../actions/workflows/main.yml)

A comprehensive implementation of the [Model Context Protocol (MCP)](https://modelcontextprotocol.io) for CVE checking and DevOps automation, featuring both a client (Stdio) and server (SSE) component. Integrates with [DevOpsify](https://opsify.dev) and supports flexible deployment and integration scenarios.

---

## Features

- **CVE Search & Filtering**: Query CVEs by ID, title, state, priority, severity, score, product, version, vendor, and date range.
- **Release Search**: Search product releases with vendor, product, and date filters.
- **Version CVEs**: Retrieve CVEs for a specific product version (with optional vendor filter).
- **Get Versions**: Retrieve all versions for comprehensive context (server feature).
- **Flexible Transports**: Supports both Stdio (client) and SSE (server) transports.
- **Docker & Python Support**: Run via Docker, `uv`, or pip.
- **VS Code Integration**: One-click install and configuration for VS Code.

## Project Structure
- **client/**: Contains the MCP client, which communicates via stdio and provides tools for CVE and release queries. Includes its own Dockerfile and Python packaging.
- **server/**: Contains the MCP server, which exposes an SSE API for integration with MCP clients. Includes core logic for CVE, version, and product queries, as well as Docker and Compose files.

```
├── client/           # Stdio-based MCP client
│   ├── src/check_mcp/   # Client source code (CVE, release, config, etc.)
│   ├── Dockerfile       # Dockerfile for client container
│   ├── pyproject.toml   # Python project metadata for client
│   └── ...
├── server/           # SSE-based MCP server implementation
│   ├── src/main.py       # Server entry point
│   ├── src/core/         # Core server logic (CVE, version, product, etc.)
│   ├── Dockerfile        # Dockerfile for server container
│   ├── docker-compose.yml# Docker Compose for server
│   ├── pyproject.toml    # Python project metadata for server
│   └── ...
├── .github/          # GitHub Actions workflows and configuration
│   └── workflows/main.yml # CI/CD pipeline
├── LICENSE           # Project license
├── README.md         # Project documentation (this file)
└── ...
```
---

## Prerequisites

- Python 3.12+
- [uv](https://docs.astral.sh/uv/) (recommended) or pip
- Docker (optional, for containerized deployment)

---

## Installation

### Using uv (Recommended)

```bash
pip install uv
uvx check-mcp
```

### Using pip

```bash
pip install check-mcp
python -m check_mcp
```

### Using Docker

```bash
docker build -t opsify/mcp -f ./server/Dockerfile ./server
# or pull prebuilt image
docker run --env-file .env -p 8050:8050 opsify/mcp
```

---

## Configuration

### Environment Variables (`.env`)

| Variable    | Description                                 | Example                |
|-------------|---------------------------------------------|------------------------|
| TRANSPORT   | Transport protocol (`sse` or `stdio`)       | `sse`                  |
| HOST        | Host to bind to (SSE only)                  | `0.0.0.0`              |
| PORT        | Port to listen on (SSE only)                | `8050`                 |

---

## Usage

### As a Python Module

```bash
python -m check_mcp
```

### As a CLI

```bash
check-mcp
```

### Example Tool Call

```json
{
  "tool": "search_cve",
  "arguments": {
    "product_name": "nginx",
    "severity": "high",
    "from_date": "2023-01-01",
    "limit": 5
  }
}
```

---

## Integration Examples

### Claude.app / VS Code / Docker

<details>
<summary>VS Code One-Click Install</summary>

[![Install with UV in VS Code](https://img.shields.io/badge/VS_Code-UV-0098FF?style=flat-square&logo=visualstudiocode&logoColor=white)](https://insiders.vscode.dev/redirect/mcp/install?name=check&config=%7B%22command%22%3A%22uvx%22%2C%22args%22%3A%5B%22check-mcp%22%5D%7D)
[![Install with Docker in VS Code](https://img.shields.io/badge/VS_Code-Docker-0098FF?style=flat-square&logo=visualstudiocode&logoColor=white)](https://insiders.vscode.dev/redirect/mcp/install?name=check&config=%7B%22command%22%3A%22docker%22%2C%22args%22%3A%5B%22run%22%2C%22-i%22%2C%22--rm%22%2C%22mcp%2Fcheck%22%5D%7D)

</details>

<details>
<summary>Claude.app Configuration (uvx, uv, docker, pip)</summary>

```json
"mcpServers": {
  "check": {
    "command": "uvx",
    "args": ["check-mcp"]
  }
}
```

```json
"mcpServers": {
  "check": {
    "command": "uv",
    "args": ["--directory", "E://check-mcp/client", "run", "check-mcp"]
  }
}
```

```json
"mcpServers": {
  "check": {
    "command": "docker",
    "args": ["run", "-i", "--rm", "opsifydev/check-mcp:latest-client"]
  }
}
```

```json
"mcpServers": {
  "check": {
    "command": "python",
    "args": ["-m", "check_mcp"]
  }
}
```
</details>

<details>
<summary>SSE Server Integration</summary>

```json
{
  "mcpServers": {
    "devopsify": {
      "transport": "sse",
      "url": "http://localhost:8050/sse"
    }
  }
}
```

*For Windsurf users, use `serverUrl` instead of `url`.*

*For n8n users, use `host.docker.internal` instead of `localhost`.*
</details>

<details>
<summary>Python with Stdio</summary>

```json
{
  "mcpServers": {
    "devopsify": {
      "command": "your/path/to/check-mcp/.venv/Scripts/python.exe",
      "args": ["your/path/to/check-mcp/src/main.py"],
      "env": {
        "TRANSPORT": "stdio"
      }
    }
  }
}
```
</details>

<details>
<summary>Docker with Stdio</summary>

```json
{
  "mcpServers": {
    "devopsify": {
      "command": "docker",
      "args": ["run", "--rm", "-i", "-e", "TRANSPORT", "opsifydev/check-mcp"],
      "env": {
        "TRANSPORT": "stdio"
      }
    }
  }
}
```
</details>

---

## Debugging

- Use the MCP inspector for debugging (see client/README.md for details).
- For advanced customization, extend the server with new tools, resources, or prompts using the MCP decorators.

---

## Building Your Own Server

1. Add tools with `@mcp.tool()`
2. Add dependencies via a custom lifespan function
3. Extend `utils.py` for helpers
4. Add resources/prompts with `@mcp.resource()` and `@mcp.prompt()`


For more details, see the [official documentation](https://devopsifyco.github.io/check-cli).

## 🤝 Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for details on how to contribute to this project.

## 🎫 License

This project is licensed under the Apache License, Version 2.0. See the [LICENSE](LICENSE) file or visit [https://devopsify.co/license](https://devopsify.co/license) for details.

## Support

For support, please open an issue in the GitHub repository or contact the maintainers.