import pytest

from orebiters_modding_tool.domain.content import ContentType
from orebiters_modding_tool.domain.project import Project
from orebiters_modding_tool.domain.project_registry import ProjectRegistry
from tests.factories.content import ContentReferenceFactory
from tests.factories.material import MaterialFactory


def test_init_registers_projects_and_content_references() -> None:
    """Register initial projects and their content references."""
    first_project = Project(namespace="test", mod_id="first_mod", name="First Mod")
    first_material = MaterialFactory.create(id="clay")
    first_project.content[ContentType.MATERIALS].append(first_material)

    second_project = Project(namespace="test", mod_id="second_mod", name="Second Mod")
    second_material = MaterialFactory.create(id="stone")
    second_project.content[ContentType.MATERIALS].append(second_material)

    registry = ProjectRegistry([first_project, second_project])

    assert registry.projects == (first_project, second_project)
    assert set(registry.get_content_references(ContentType.MATERIALS)) == {
        ContentReferenceFactory.from_content(first_material, mod_id=first_project.qualified_id),
        ContentReferenceFactory.from_content(second_material, mod_id=second_project.qualified_id),
    }


def test_add_project_registers_project_and_content_references() -> None:
    """Register a project and its content references."""
    registry = ProjectRegistry()

    project = Project(namespace="test", mod_id="test_mod", name="Test Mod")
    material = MaterialFactory.create(id="clay")
    project.content[ContentType.MATERIALS].append(material)

    registry.add_project(project)

    assert registry.projects == (project,)
    assert registry.get_content_references(ContentType.MATERIALS) == (
        ContentReferenceFactory.from_content(material, mod_id=project.qualified_id),
    )


def test_remove_project_unregisters_project_and_content_references() -> None:
    """Remove a project and its content references."""
    project = Project(namespace="test", mod_id="test_mod", name="Test Mod")
    material = MaterialFactory.create(id="clay")
    project.content[ContentType.MATERIALS].append(material)

    registry = ProjectRegistry([project])

    registry.remove_project(project)

    assert registry.projects == ()
    assert registry.get_content_references(ContentType.MATERIALS) == ()


def test_get_project_raises_for_unknown_project() -> None:
    """Raise an error when the project does not exist."""
    registry = ProjectRegistry()

    with pytest.raises(ValueError, match="Project not found: test.unknown_mod."):
        registry.get_project("test.unknown_mod")


def test_has_content_reference_returns_whether_reference_is_registered() -> None:
    """Check whether a content reference is registered."""
    registry = ProjectRegistry()

    registry.add_content_reference(ContentType.MATERIALS, "test.test_mod.clay")

    assert registry.has_content_reference(ContentType.MATERIALS, "test.test_mod.clay")
    assert not registry.has_content_reference(ContentType.MATERIALS, "test.test_mod.stone")


def test_get_content_references_returns_independent_references() -> None:
    """Return references independent of the registry's internal objects."""
    registry = ProjectRegistry()

    registry.add_content_reference(ContentType.MATERIALS, "test.test_mod.clay")

    first_references = registry.get_content_references(ContentType.MATERIALS)
    second_references = registry.get_content_references(ContentType.MATERIALS)

    assert first_references == second_references
    assert first_references[0] is not second_references[0]


def test_content_reference_operations_update_registry() -> None:
    """Add and remove content references from the registry."""
    registry = ProjectRegistry()

    first_reference = ContentReferenceFactory.create(content_type=ContentType.MATERIALS)
    second_reference = ContentReferenceFactory.create(content_type=ContentType.MATERIALS)

    registry.add_content_reference(first_reference.content_type, first_reference.qualified_id)
    registry.add_content_reference(second_reference.content_type, second_reference.qualified_id)

    assert registry.get_content_references(ContentType.MATERIALS) == (
        first_reference,
        second_reference,
    )

    registry.remove_content_reference(first_reference.content_type, first_reference.qualified_id)

    assert registry.get_content_references(ContentType.MATERIALS) == (second_reference,)
