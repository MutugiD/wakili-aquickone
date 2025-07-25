from typing import Callable, Dict, Any

class ToolRegistry:
    """
    Registry for agent tools. Supports registration and invocation by name.
    """
    def __init__(self):
        self.tools: Dict[str, Callable] = {}

    def register(self, name: str, func: Callable):
        self.tools[name] = func

    def call(self, name: str, *args, **kwargs) -> Any:
        if name not in self.tools:
            raise ValueError(f"Tool '{name}' not found")
        return self.tools[name](*args, **kwargs)

    def list_tools(self):
        return list(self.tools.keys())