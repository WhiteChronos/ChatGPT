from __future__ import annotations

from typing import Any


_SUPPORTED_SCHEMA_KEYS = {"$schema", "title", "description", "type", "enum", "const", "required", "properties", "additionalProperties", "items", "minLength"}

_TYPE_CHECKS = {
    "object": lambda value: isinstance(value, dict),
    "array": lambda value: isinstance(value, list),
    "string": lambda value: isinstance(value, str),
    "integer": lambda value: isinstance(value, int) and not isinstance(value, bool),
    "number": lambda value: isinstance(value, (int, float)) and not isinstance(value, bool),
    "boolean": lambda value: isinstance(value, bool),
    "null": lambda value: value is None,
}


def _matches_type(value: object, expected: object) -> bool:
    names = expected if isinstance(expected, list) else [expected]
    if not all(isinstance(name, str) and name in _TYPE_CHECKS for name in names):
        raise ValueError(f"unsupported schema type declaration: {expected!r}")
    return any(_TYPE_CHECKS[name](value) for name in names)


def _json_equal(left: object, right: object) -> bool:
    if isinstance(left, bool) or isinstance(right, bool):
        return type(left) is type(right) and left == right
    return left == right


def validate_schema_subset(value: object, schema: dict[str, Any], path: str = "$") -> None:
    """Validate the JSON Schema subset used by Control Plane registries."""
    unsupported = sorted(set(schema) - _SUPPORTED_SCHEMA_KEYS)
    if unsupported:
        raise ValueError(f"{path}: unsupported schema keyword {unsupported[0]!r}")
    if "type" in schema and not _matches_type(value, schema["type"]):
        raise ValueError(f"{path}: expected type {schema['type']!r}")

    if "const" in schema and not _json_equal(value, schema["const"]):
        raise ValueError(f"{path}: expected const {schema['const']!r}")

    if "enum" in schema and not any(_json_equal(value, option) for option in schema["enum"]):
        raise ValueError(f"{path}: value {value!r} is not in enum {schema['enum']!r}")

    if "minLength" in schema and isinstance(value, str) and len(value) < int(schema["minLength"]):
        raise ValueError(f"{path}: string shorter than minLength {schema['minLength']}")

    if isinstance(value, dict):
        required = schema.get("required", [])
        for key in required:
            if key not in value:
                raise ValueError(f"{path}.{key}: required property missing")
        properties = schema.get("properties", {})
        if schema.get("additionalProperties") is False:
            extras = sorted(set(value) - set(properties))
            if extras:
                raise ValueError(f"{path}.{extras[0]}: additional property not allowed")
        for key, child_schema in properties.items():
            if key in value:
                validate_schema_subset(value[key], child_schema, f"{path}.{key}")

    if isinstance(value, list) and "items" in schema:
        item_schema = schema["items"]
        for index, item in enumerate(value):
            validate_schema_subset(item, item_schema, f"{path}[{index}]")
