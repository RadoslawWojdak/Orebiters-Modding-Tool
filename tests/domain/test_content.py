import pytest

from orebiters_modding_tool.domain.content import ContentReference
from tests.factories.content import ContentReferenceFactory


def test_is_category_returns_true_for_category_reference(
    materials_category_reference: ContentReference,
) -> None:
    """Return true for a reference targeting a content category."""
    assert materials_category_reference.is_category


def test_is_category_returns_false_for_content_reference() -> None:
    """Return false for a reference targeting specific content."""
    reference = ContentReferenceFactory.create(qualified_id="orebiters.core.materials.iron")

    assert not reference.is_category


def test_namespace_returns_namespace_from_qualified_id() -> None:
    """Return the namespace from a qualified content ID."""
    reference = ContentReferenceFactory.create(qualified_id="orebiters.core.materials.iron")

    assert reference.namespace == "orebiters"


def test_namespace_raises_for_category_reference(
    materials_category_reference: ContentReference,
) -> None:
    """Raise an error when getting the namespace of a category reference."""
    with pytest.raises(ValueError, match="Content reference does not target specific content."):
        _ = materials_category_reference.namespace


def test_mod_id_returns_mod_id_from_qualified_id() -> None:
    """Return the mod ID from a qualified content ID."""
    reference = ContentReferenceFactory.create(qualified_id="orebiters.core.materials.iron")

    assert reference.mod_id == "core"


def test_mod_id_raises_for_category_reference(
    materials_category_reference: ContentReference,
) -> None:
    """Raise an error when getting the mod ID of a category reference."""
    with pytest.raises(ValueError, match="Content reference does not target specific content."):
        _ = materials_category_reference.mod_id


def test_content_id_returns_content_id_from_qualified_id() -> None:
    """Return the content ID from a qualified content ID."""
    reference = ContentReferenceFactory.create(qualified_id="orebiters.core.materials.iron")

    assert reference.content_id == "iron"


def test_content_id_raises_for_category_reference(
    materials_category_reference: ContentReference,
) -> None:
    """Raise an error when getting the content ID of a category reference."""
    with pytest.raises(ValueError, match="Content reference does not target specific content."):
        _ = materials_category_reference.content_id
