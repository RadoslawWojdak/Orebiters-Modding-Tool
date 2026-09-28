import pytest

from orebiters_modding_tool.domain.content import ContentType
from tests.factories.content_factory import ContentReferenceFactory


@pytest.mark.parametrize(
    ("qualified_id", "expected_type"),
    [
        ("test.test_mod.items.sword", ContentType.ITEMS),
        ("test.test_mod.materials.iron", ContentType.MATERIALS),
        ("test.test_mod.mineables.copper_ore", ContentType.MINEABLES),
    ],
)
def test_create_infers_content_type_from_qualified_id(
    qualified_id: str,
    expected_type: ContentType,
) -> None:
    """Test that the content type is inferred correctly from the qualified ID."""
    reference = ContentReferenceFactory.create(qualified_id)

    assert reference.qualified_id == qualified_id
    assert reference.content_type == expected_type


def test_create_uses_explicit_content_type_over_inferred_type() -> None:
    """Test that an explicitly provided content type takes precedence over inference."""
    reference = ContentReferenceFactory.create(
        qualified_id="test.test_mod.materials.iron",
        content_type=ContentType.ITEMS,
    )

    assert reference.content_type == ContentType.ITEMS
    assert reference.qualified_id == "test.test_mod.materials.iron"


def test_create_raises_for_unknown_content_type() -> None:
    """Test that a ValueError is raised when the content type cannot be inferred."""
    with pytest.raises(ValueError, match="Cannot infer content type"):
        ContentReferenceFactory.create("test.test_mod.unknown.something")
