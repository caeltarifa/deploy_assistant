from app.tools.akira_skills import create_module, list_services, login, start_module, stop_module


def register(mcp):
    login.register(mcp)
    create_module.register(mcp)
    start_module.register(mcp)
    stop_module.register(mcp)
    list_services.register(mcp)


__all__ = ["register", "login", "create_module", "start_module", "stop_module", "list_services"]
