import re


def normalize_identifier(value: str) -> str:
    """Normalize a value for use in an identifier.

    :param value: Value to normalize.
    :returns: Normalized identifier value.
    """
    normalized_value = value.strip().lower()
    normalized_value = re.sub(r"\s+", "_", normalized_value)
    normalized_value = re.sub(r"[^a-z0-9_]", "", normalized_value)

    return normalized_value


def create_qualified_id(namespace: str, mod_id: str) -> str:
    """Create a qualified identifier from a namespace and mod ID.

    :param namespace: Mod namespace.
    :param mod_id: Mod identifier.
    :returns: Qualified mod identifier.
    """
    return f"{namespace}.{mod_id}"
