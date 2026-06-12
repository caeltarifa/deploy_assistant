import asyncio
import json
import sys
from fastmcp import Client

MCP_URL = "http://localhost:8000/mcp"


async def run_interactive(client: Client):
    print("Listing tools...")
    tools = await client.list_tools()
    tools_json = [getattr(t, "model_dump", lambda: t)() for t in tools]
    print(json.dumps(tools_json, indent=2))

    print("\nCalling list_all_containers...")
    result = await client.call_tool("list_all_containers", {})
    if hasattr(result, "content"):
        content = result.content
        if content and hasattr(content[0], "text"):
            try:
                print(json.dumps(json.loads(content[0].text), indent=2))
                return
            except json.JSONDecodeError:
                pass

    if hasattr(result, "model_dump"):
        print(json.dumps(result.model_dump(), indent=2))
        return

    print(result)

    container_id = input("\nEnter container id or name to restart (or blank to skip): ").strip()
    if container_id:
        print(f"\nCalling restart_container({container_id})...")
        restart = await client.call_tool("restart_container", {"container_id": container_id})
        if hasattr(restart, "content") and restart.content and hasattr(restart.content[0], "text"):
            try:
                print(json.dumps(json.loads(restart.content[0].text), indent=2))
                return
            except json.JSONDecodeError:
                pass
        if hasattr(restart, "model_dump"):
            print(json.dumps(restart.model_dump(), indent=2))
            return
        print(restart)

    container_id = input("\nEnter container id or name to stop (or blank to skip): ").strip()
    if container_id:
        print(f"\nCalling stop_container({container_id})...")
        stopped = await client.call_tool("stop_container", {"container_id": container_id})
        if hasattr(stopped, "content") and stopped.content and hasattr(stopped.content[0], "text"):
            try:
                print(json.dumps(json.loads(stopped.content[0].text), indent=2))
                return
            except json.JSONDecodeError:
                pass
        if hasattr(stopped, "model_dump"):
            print(json.dumps(stopped.model_dump(), indent=2))
            return
        print(stopped)


async def run_command(client: Client, args: list[str]):
    if not args:
        await run_interactive(client)
        return

    cmd = args[0]
    if cmd == "list":
        result = await client.call_tool("list_all_containers", {})
    elif cmd == "restart" and len(args) >= 2:
        result = await client.call_tool("restart_container", {"container_id": args[1]})
    elif cmd == "stop" and len(args) >= 2:
        result = await client.call_tool("stop_container", {"container_id": args[1]})
    elif cmd == "login_fixed":
        result = await client.call_tool("login_fixed_user", {})
    elif cmd == "login" and len(args) >= 4:
        result = await client.call_tool(
            "login",
            {"url": args[1], "username": args[2], "password": args[3]},
        )
    elif cmd == "check_user" and len(args) >= 2:
        result = await client.call_tool("check_akira_db_user", {"username": args[1]})
    elif cmd == "reset_password" and len(args) >= 3:
        result = await client.call_tool(
            "reset_akira_password",
            {"username": args[1], "new_password": args[2]},
        )
    elif cmd == "user_state" and len(args) >= 2:
        result = await client.call_tool("get_akira_user_state", {"username": args[1]})
    elif cmd == "unlock_user" and len(args) >= 2:
        result = await client.call_tool("unlock_akira_user", {"username": args[1]})
    elif cmd == "verify_password" and len(args) >= 3:
        result = await client.call_tool(
            "verify_akira_password",
            {"username": args[1], "password": args[2]},
        )
    elif cmd == "create_service" and len(args) >= 3:
        result = await client.call_tool(
            "create_service_module",
            {"service_name": args[1], "video_url": args[2]},
        )
    elif cmd == "start_service" and len(args) >= 2:
        result = await client.call_tool(
            "start_service_module",
            {"service_name": args[1]},
        )
    elif cmd == "stop_service" and len(args) >= 2:
        result = await client.call_tool(
            "stop_service_module",
            {"service_name": args[1]},
        )
    elif cmd == "list_services":
        result = await client.call_tool("list_service_names", {})
    else:
        print(
            "Usage: python3.10 client.py [list|restart|stop <container_id_or_name>|login_fixed|login <url> <username> <password>|check_user <username>|reset_password <username> <new_password>|user_state <username>|unlock_user <username>|verify_password <username> <password>|create_service <service_name> <video_url>|start_service <service_name>|stop_service <service_name>|list_services]"
        )
        return

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


async def main():
    async with Client(MCP_URL) as client:
        await run_command(client, sys.argv[1:])


def run():
    asyncio.run(main())


if __name__ == "__main__":
    run()
