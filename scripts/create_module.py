import asyncio
import json
import sys
from fastmcp import Client

import login as login_script

MCP_URL = "http://localhost:8000/mcp"


async def main():
    if len(sys.argv) < 3:
        print("Usage: python3.10 scripts/create_module.py <service_name> <video_url>")
        return

    login_code = await login_script.run_login(["fixed"])
    if login_code != 0:
        return

    async with Client(MCP_URL) as client:
        result = await client.call_tool(
            "create_service_module",
            {"service_name": sys.argv[1], "video_url": sys.argv[2]},
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
