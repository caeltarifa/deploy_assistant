import asyncio
import json
import sys
from fastmcp import Client

MCP_URL = "http://localhost:8000/mcp"


async def main():
    if len(sys.argv) < 2:
        print("Usage: python3.10 scripts/stop_module.py <service_name>")
        return

    async with Client(MCP_URL) as client:
        result = await client.call_tool(
            "stop_service_module",
            {"service_name": sys.argv[1]},
        )

    if hasattr(result, "content") and result.content and hasattr(result.content[0], "text"):
        try:
            print(json.dumps(json.loads(result.content[0].text), indent=2))
            return
        except json.JSONDecodeError:
            pass
    if hasattr(result, "model_dump"):
        print(json.dumps(result.model_dump(), indent=2))
        return
    print(result)


if __name__ == "__main__":
    asyncio.run(main())
