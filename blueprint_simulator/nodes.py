"""Node implementations for the blueprint simulator."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Optional

from .value_resolver import BlueprintEvaluationError, ValueResolver


@dataclass
class RuntimeContext:
    variables: Dict[str, Any]
    logs: list[str]


class NodeExecutionError(RuntimeError):
    """Raised when a node cannot be executed."""


class Node:
    """Base class for all nodes."""

    node_type: str = "node"

    def __init__(self, definition: Dict[str, Any]):
        self.definition = definition

    def run(self, context: RuntimeContext, resolver: ValueResolver) -> Optional[str]:
        raise NotImplementedError

    @staticmethod
    def _next(definition: Dict[str, Any]) -> Optional[str]:
        return definition.get("next")


class EventNode(Node):
    node_type = "Event"

    def run(self, context: RuntimeContext, resolver: ValueResolver) -> Optional[str]:
        return self._next(self.definition)


class PrintNode(Node):
    node_type = "PrintString"

    def run(self, context: RuntimeContext, resolver: ValueResolver) -> Optional[str]:
        value = resolver.resolve(self.definition.get("value"))
        context.logs.append(str(value))
        return self._next(self.definition)


class SetVariableNode(Node):
    node_type = "SetVariable"

    def run(self, context: RuntimeContext, resolver: ValueResolver) -> Optional[str]:
        target = self.definition.get("target")
        if not target:
            raise NodeExecutionError("SetVariable node is missing 'target'")
        value = resolver.resolve(self.definition.get("value"))
        context.variables[target] = value
        return self._next(self.definition)


class ComputeNode(Node):
    node_type = "Compute"

    def run(self, context: RuntimeContext, resolver: ValueResolver) -> Optional[str]:
        store_as = self.definition.get("store_as")
        if not store_as:
            raise NodeExecutionError("Compute node requires 'store_as'")
        expression = self.definition.get("expression")
        value = resolver.resolve(expression)
        context.variables[store_as] = value
        return self._next(self.definition)


class BranchNode(Node):
    node_type = "Branch"

    def run(self, context: RuntimeContext, resolver: ValueResolver) -> Optional[str]:
        condition = self.definition.get("condition")
        if condition is None:
            raise NodeExecutionError("Branch node missing 'condition'")
        result = resolver.resolve(condition)
        if not isinstance(result, bool):
            raise BlueprintEvaluationError("Branch conditions must evaluate to booleans")
        return self.definition.get("true_next") if result else self.definition.get("false_next")


NODE_TYPES = {
    cls.node_type: cls
    for cls in [EventNode, PrintNode, SetVariableNode, ComputeNode, BranchNode]
}


def create_node(definition: Dict[str, Any]) -> Node:
    node_type = definition.get("type")
    if not node_type:
        raise NodeExecutionError("Node is missing 'type'")
    cls = NODE_TYPES.get(node_type)
    if not cls:
        available = ", ".join(sorted(NODE_TYPES))
        raise NodeExecutionError(f"Unsupported node type '{node_type}'. Available: {available}")
    return cls(definition)
