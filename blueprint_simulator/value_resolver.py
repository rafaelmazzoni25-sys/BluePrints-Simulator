"""Helpers to resolve values described in a blueprint specification."""

from __future__ import annotations

from typing import Any, Dict, Iterable, List


class BlueprintEvaluationError(RuntimeError):
    """Raised when a value cannot be evaluated."""


Operation = str


class ValueResolver:
    """Utility class responsible for resolving value specifications."""

    def __init__(self, variables: Dict[str, Any]):
        self.variables = variables

    def resolve(self, spec: Any) -> Any:
        """Resolve a value specification to a Python value."""
        if spec is None:
            return None
        if isinstance(spec, (int, float, bool, str)):
            return spec
        if isinstance(spec, list):
            return [self.resolve(item) for item in spec]
        if isinstance(spec, dict):
            if "var" in spec:
                name = spec["var"]
                if name not in self.variables:
                    raise BlueprintEvaluationError(f"Variable '{name}' is not defined")
                return self.variables[name]
            if "op" in spec:
                op = spec["op"]
                inputs = spec.get("inputs")
                if not isinstance(inputs, Iterable):
                    raise BlueprintEvaluationError("Operation inputs must be a list")
                resolved_inputs = [self.resolve(item) for item in inputs]
                return self._apply_operation(op, resolved_inputs)
            if "format" in spec:
                template = spec["format"]
                try:
                    return template.format(**self.variables)
                except KeyError as exc:
                    raise BlueprintEvaluationError(
                        f"Missing variable '{exc.args[0]}' for format operation"
                    ) from exc
        raise BlueprintEvaluationError(f"Unsupported value specification: {spec!r}")

    def _apply_operation(self, op: Operation, values: List[Any]) -> Any:
        if op in {"add", "+"}:
            return sum(values)
        if op in {"mul", "*"}:
            result = 1
            for value in values:
                result *= value
            return result
        if op in {"sub", "-"}:
            return self._binary(values, lambda a, b: a - b)
        if op in {"div", "/"}:
            return self._binary(values, lambda a, b: a / b)
        if op == "max":
            return max(values)
        if op == "min":
            return min(values)
        if op in {"==", "eq"}:
            return self._binary(values, lambda a, b: a == b)
        if op in {"!=", "ne"}:
            return self._binary(values, lambda a, b: a != b)
        if op in {">", "gt"}:
            return self._binary(values, lambda a, b: a > b)
        if op in {"<", "lt"}:
            return self._binary(values, lambda a, b: a < b)
        if op in {">=", "ge"}:
            return self._binary(values, lambda a, b: a >= b)
        if op in {"<=", "le"}:
            return self._binary(values, lambda a, b: a <= b)
        if op == "and":
            return all(values)
        if op == "or":
            return any(values)
        if op == "not":
            if len(values) != 1:
                raise BlueprintEvaluationError("'not' operation expects a single input")
            return not values[0]
        raise BlueprintEvaluationError(f"Unsupported operation '{op}'")

    @staticmethod
    def _binary(values: List[Any], func):
        if len(values) != 2:
            raise BlueprintEvaluationError("Binary operations expect exactly 2 inputs")
        left, right = values
        return func(left, right)
