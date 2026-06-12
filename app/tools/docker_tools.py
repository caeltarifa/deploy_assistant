import docker
from fastmcp import FastMCP


def register(mcp: FastMCP) -> None:
    @mcp.tool
    def list_all_containers() -> list[dict]:
        """List all containers on the host Docker daemon."""
        client = docker.from_env()
        containers = client.containers.list(all=True)
        return [
            {
                "id": c.id,
                "name": c.name,
                "image": c.image.tags[0] if c.image.tags else c.image.short_id,
                "status": c.status,
            }
            for c in containers
        ]

    @mcp.tool
    def restart_container(container_id: str) -> dict:
        """Restart a container by id or name."""
        client = docker.from_env()
        container = client.containers.get(container_id)
        container.restart()
        return {
            "id": container.id,
            "name": container.name,
            "status": container.status,
        }

    @mcp.tool
    def stop_container(container_id: str) -> dict:
        """Stop a container by id or name."""
        client = docker.from_env()
        container = client.containers.get(container_id)
        container.stop()
        return {
            "id": container.id,
            "name": container.name,
            "status": container.status,
        }
