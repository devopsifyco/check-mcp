from typing import Annotated, Optional, List
from pydantic import BaseModel, Field
import httpx
from mcp.shared.exceptions import McpError
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import (
    ErrorData,
    GetPromptResult,
    Prompt,
    PromptArgument,
    PromptMessage,
    TextContent,
    Tool,
    INVALID_PARAMS,
    INTERNAL_ERROR,
)

API_URL = "https://api.opsify.dev/checks/cve"
API_KEY = "SPK1HgBWcxO5EmLsCSP6aIRNhX6wXMYa"

class SearchCVEParams(BaseModel):
    cve_id: Optional[str] = Field(None, description="CVE ID to search for")
    title: Optional[str] = Field(None, description="Title to search in CVE description")
    state: Optional[str] = Field(None, description="State to filter by")
    priority: Optional[str] = Field(None, description="Priority level to filter by")
    severity: Optional[str] = Field(None, description="Severity level to filter by")
    score: Optional[float] = Field(None, description="CVSS score to filter by")
    product_name: Optional[str] = Field(None, description="Product name to filter affected products")
    product_version: Optional[str] = Field(None, description="Product version to filter affected products")
    vendor: Optional[str] = Field(None, description="Vendor name to filter affected products")
    from_date: Optional[str] = Field(None, description="Start date for filtering (YYYY-MM-DD or ISO 8601)")
    to_date: Optional[str] = Field(None, description="End date for filtering (YYYY-MM-DD or ISO 8601)")
    skip: Optional[int] = Field(0, description="Number of records to skip (pagination)")
    limit: Optional[int] = Field(10, description="Maximum number of records to return (pagination)")

async def search_cve_api(params: SearchCVEParams) -> List[dict]:
    headers = {"x-api-key": API_KEY}
    query = {k: v for k, v in params.dict().items() if v is not None}
    async with httpx.AsyncClient() as client:
        try:
            resp = await client.get(API_URL, params=query, headers=headers, timeout=30)
            resp.raise_for_status()
            return resp.json()
        except Exception as e:
            raise McpError(ErrorData(code=INTERNAL_ERROR, message=f"Failed to fetch CVEs: {e}"))

async def serve() -> None:
    server = Server("mcp-check")

    @server.list_tools()
    async def list_tools() -> list[Tool]:
        return [
            Tool(
                name="search_cve",
                description="Searches for CVEs using the Opsify API with various filters.",
                inputSchema=SearchCVEParams.model_json_schema(),
            )
        ]

    @server.list_prompts()
    async def list_prompts() -> list[Prompt]:
        return [
            Prompt(
                name="search_cve",
                description="Search for CVEs using various filters.",
                arguments=[
                    PromptArgument(name=field.alias or name, description=field.field_info.description or "", required=False)
                    for name, field in SearchCVEParams.model_fields.items()
                ],
            )
        ]

    @server.call_tool()
    async def call_tool(name, arguments: dict) -> list[TextContent]:
        try:
            args = SearchCVEParams(**arguments)
        except Exception as e:
            raise McpError(ErrorData(code=INVALID_PARAMS, message=str(e)))
        cves = await search_cve_api(args)
        if not cves:
            return [TextContent(type="text", text="No CVEs found for the given criteria.")]
        return [TextContent(type="text", text=f"Found {len(cves)} CVEs:\n" + "\n\n".join([
            f"CVE ID: {cve.get('cve_id')}\nTitle: {cve.get('title')}\nScore: {cve.get('score')}\nState: {cve.get('state')}\nPublished: {cve.get('published_date')}\nVendor: {cve.get('vendor')}\nDescription: {cve.get('description')}\nReferences: {', '.join(cve.get('references', []))}"
            for cve in cves
        ]))]

    @server.get_prompt()
    async def get_prompt(name: str, arguments: dict | None) -> GetPromptResult:
        if not arguments:
            raise McpError(ErrorData(code=INVALID_PARAMS, message="At least one filter argument is required."))
        try:
            args = SearchCVEParams(**arguments)
        except Exception as e:
            raise McpError(ErrorData(code=INVALID_PARAMS, message=str(e)))
        cves = await search_cve_api(args)
        if not cves:
            return GetPromptResult(
                description="No CVEs found for the given criteria.",
                messages=[PromptMessage(role="user", content=TextContent(type="text", text="No CVEs found."))],
            )
        return GetPromptResult(
            description=f"Found {len(cves)} CVEs.",
            messages=[
                PromptMessage(
                    role="user",
                    content=TextContent(type="text", text=f"Found {len(cves)} CVEs:\n" + "\n\n".join([
                        f"CVE ID: {cve.get('cve_id')}\nTitle: {cve.get('title')}\nScore: {cve.get('score')}\nState: {cve.get('state')}\nPublished: {cve.get('published_date')}\nVendor: {cve.get('vendor')}\nDescription: {cve.get('description')}\nReferences: {', '.join(cve.get('references', []))}"
                        for cve in cves
                    ])),
                )
            ],
        )

    options = server.create_initialization_options()
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, options, raise_exceptions=True)
