# Check MCP Server (Stdio)

A Model Context Protocol server that provides CVE checking capabilities via the Opsify API. This server enables LLMs to search for and retrieve CVE (Common Vulnerabilities and Exposures) information using a flexible set of filters.

> [!CAUTION]
> This server can access external APIs and may represent a security risk if misconfigured. Ensure your API key and usage comply with your organization's security policies.

> The API key is read from the `CHECK_API_KEY` environment variable. Set this variable to your Opsify API key before running the client or server.

### Available Tools

- `search_cve` - Search CVEs with various filters via the Opsify API.
    - `cve_id` (string, optional): CVE ID to search for
    - `title` (string, optional): Title to search in CVE description
    - `state` (string, optional): State to filter by
    - `priority` (string, optional): Priority level to filter by
    - `severity` (string, optional): Severity level to filter by
    - `score` (float, optional): CVSS score to filter by
    - `product_name` (string, optional): Product name to filter affected products
    - `product_version` (string, optional): Product version to filter affected products
    - `vendor` (string, optional): Vendor name to filter affected products
    - `from_date` (string, optional): Start date for filtering (YYYY-MM-DD or ISO 8601)
    - `to_date` (string, optional): End date for filtering (YYYY-MM-DD or ISO 8601)
    - `skip` (int, optional): Number of records to skip (pagination)
    - `limit` (int, optional): Maximum number of records to return (pagination)

- `search_release` - Search releases with optional filters for vendor, product name, and date range. Supports pagination.
    - `vendor` (string, optional): Vendor name to filter by (case-insensitive)
    - `product_name` (string, optional): Product name to filter by (case-insensitive)
    - `from_date` (string, optional): Start date (inclusive) for filtering (YYYY-MM-DD or ISO datetime)
    - `to_date` (string, optional): End date (inclusive) for filtering (YYYY-MM-DD or ISO datetime)
    - `date_field` (string, optional): Which date field to filter on (e.g., "release_date")
    - `page` (int, optional): Page number (starting from 1)
    - `page_size` (int, optional): Number of items per page

- `get_version_cves` - Get CVEs for a specific version of a product. Optionally filter by vendor. Uses caching (TTL: 1 day).
    - `product_name` (string, required): Product name (e.g., 'nginx')
    - `version` (string, required): Specific version to retrieve CVEs for (e.g., '1.0.0')
    - `vendor` (string, optional): Vendor name to filter by (case-insensitive)

### Example Usage

```python
python -m check_mcp
```

Or as a script/entry point:

```shell
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

## Installation

### Using uv (recommended)

When using [`uv`](https://docs.astral.sh/uv/) no specific installation is needed. We will
use [`uvx`](https://docs.astral.sh/uv/guides/tools/) to directly run *check-mcp*.

### Using PIP

Alternatively you can install `check-mcp` via pip:

```
pip install check-mcp
```

After installation, you can run it as a script using:

```
python -m check_mcp
```

## Configuration

### Configure for Claude.app

Add to your Claude settings:

<details>
<summary>Using uvx</summary>

```json
"mcpServers": {
  "check": {
    "command": "uvx",
    "args": ["check-mcp"]
  }
}
```
</details>

<details>
<summary>Using uv</summary>

```json
"mcpServers": {
  "check": {
    "command": "uv",
    "args": [
          "--directory",
          "E://check-mcp/client",
          "run",
          "check-mcp"
    ]
  }
}
```