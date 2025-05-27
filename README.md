# MCP Server Check

A Model Context Protocol server that provides tools to search and report CVEs (Common Vulnerabilities and Exposures) using the Opsify API. This server enables LLMs to retrieve and process CVE information with various filters.

## Available Tools

- `search_cve` - Searches for CVEs using the Opsify API with various filters.
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

## API

- Endpoint: `https://api.opsify.dev/checks/cve`
- Method: GET
- Default API Key: `SPK1HgBWcxO5EmLsCSP6aIRNhX6wXMYa`

### Sample Response

```
[
  {
    "cve_id": "string",
    "state": "string",
    "published_date": "string",
    "score": 0,
    "title": "string",
    "description": "string",
    "references": [
      "string"
    ],
    "vendor": "string"
  }
]
```

## Installation

Install via pip:

```
pip install mcp-server-check
```

After installation, you can run it as a script using:

```
python -m mcp_server_check
```

## Configuration

Add to your MCP settings as needed. See the API and tool details above for usage.

## Contributing

We welcome contributions to mcp-server-check! To contribute:
- Fork the repository and create your branch from `main`.
- Make your changes with clear commit messages.
- Ensure your code follows the existing style and passes any tests or linters.
- Submit a pull request describing your changes and why they are needed.

For questions or suggestions, feel free to open an issue.

## License

mcp-server-check is licensed under the MIT License. See the LICENSE file for details.
