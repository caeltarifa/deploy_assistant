from fastmcp import FastMCP
from starlette.requests import Request
from starlette.responses import PlainTextResponse

from app.tools import akira_db_tools, docker_tools, register_akira_skills

mcp = FastMCP("Docker MCP")


docker_tools.register(mcp)
akira_db_tools.register(mcp)
register_akira_skills(mcp)


@mcp.custom_route("/health", methods=["GET"])
async def health(_: Request):
    return PlainTextResponse("OK")


if __name__ == "__main__":
    mcp.run(transport="streamable-http", host="0.0.0.0", port=8000)
