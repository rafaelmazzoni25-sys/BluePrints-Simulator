"""Execution runtime for blueprint graphs."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Iterable

from .nodes import NODE_TYPES, RuntimeContext, create_node
from .value_resolver import ValueResolver


@dataclass
class BlueprintRunner:
    definition: Dict[str, Any]

    def __post_init__(self) -> None:
        self._node_map = {node_def["id"]: node_def for node_def in self.definition["nodes"]}
        self._validate()

    def _validate(self) -> None:
        entry = self.definition.get("entry_point")
        if entry not in self._node_map:
            raise ValueError(f"Entry point '{entry}' does not match any node id")
        for node_def in self.definition["nodes"]:
            if "type" not in node_def:
                raise ValueError(f"Node {node_def.get('id')} is missing 'type'")
            if node_def["type"] not in NODE_TYPES:
                available = ", ".join(sorted(NODE_TYPES))
                raise ValueError(f"Node {node_def.get('id')} has unsupported type. {available}")

    def run(self, variable_overrides: Dict[str, Any] | None = None) -> RuntimeContext:
        context = RuntimeContext(
            variables={**self.definition.get("variables", {}), **(variable_overrides or {})},
            logs=[],
        )
        resolver = ValueResolver(context.variables)
        current_id = self.definition["entry_point"]
        visited = set()
        while current_id is not None:
            node_def = self._node_map.get(current_id)
            if not node_def:
                raise RuntimeError(f"Node '{current_id}' referenced but not defined")
            node = create_node(node_def)
            next_id = node.run(context, resolver)
            resolver.variables = context.variables
            if current_id in visited and next_id == current_id:
                raise RuntimeError(f"Detected self-loop at node '{current_id}'")
            visited.add(current_id)
            current_id = next_id
        return context

    def describe(self) -> str:
        nodes = self.definition["nodes"]
        lines = [
            f"Blueprint: {self.definition.get('name')}",
            f"Entry point: {self.definition.get('entry_point')}",
            "Nodes:",
        ]
        for node in nodes:
            lines.append(f"  - {node['id']}: {node['type']}")
        return "\n".join(lines)

    @classmethod
    def available_node_types(cls) -> Iterable[str]:
        return sorted(NODE_TYPES)
