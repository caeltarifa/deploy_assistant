import asyncio
import json
import sys
from fastmcp import Client

MCP_URL = "http://localhost:8000/mcp"


async def main():
    async with Client(MCP_URL) as client:
        result = await client.call_tool("list_service_names", {})

    if hasattr(result, "content") and result.content and hasattr(result.content[0], "text"):
        try:
            payload = json.loads(result.content[0].text)
            services = payload.get("services", [])
            if not services:
                print("0 services to show you")
                return
            print(json.dumps(payload, indent=2))
            return
        except json.JSONDecodeError:
            pass
    if hasattr(result, "model_dump"):
        payload = result.model_dump()
        services = payload.get("services", [])
        if not services:
            print("0 services to show you")
            return
        print(json.dumps(payload, indent=2))
        return
    print(result)


if __name__ == "__main__":
    asyncio.run(main())
