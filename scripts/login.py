import asyncio
import json
import sys
from fastmcp import Client

MCP_URL = "http://localhost:8000/mcp"


def _result_text(result) -> str:
    if hasattr(result, "content") and result.content and hasattr(result.content[0], "text"):
        return result.content[0].text or ""
    if hasattr(result, "model_dump"):
        try:
            return json.dumps(result.model_dump(), indent=2)
        except Exception:
            return str(result)
    return str(result)


def _print_result(result) -> None:
    text = _result_text(result)
    try:
        print(json.dumps(json.loads(text), indent=2))
        return
    except Exception:
        pass
    print(text)


async def login_fixed(client: Client):
    return await client.call_tool("login_fixed_user", {})


async def login_custom(client: Client, url: str, username: str, password: str):
    return await client.call_tool(
        "login",
        {"url": url, "username": username, "password": password},
    )


async def run_login(args: list[str]) -> int:
    if not args:
        print("Usage: python3.10 scripts/login.py fixed|<url> <username> <password>")
        return 1

    async with Client(MCP_URL) as client:
        if args[0] == "fixed":
            result = await login_fixed(client)
        else:
            if len(args) < 3:
                print("Usage: python3.10 scripts/login.py <url> <username> <password>")
                return 1
            result = await login_custom(client, args[0], args[1], args[2])

    _print_result(result)
    text = _result_text(result).lower()
    if "successful" in text or "success" in text:
        return 0
    if "failed" in text or "error" in text:
        return 2
    return 0


async def main():
    await run_login(sys.argv[1:])


if __name__ == "__main__":
    asyncio.run(main())
