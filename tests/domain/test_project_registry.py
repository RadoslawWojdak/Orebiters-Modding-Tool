from orebiters_modding_tool.domain.content import ContentReference, ContentType
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


def test_content_reference_operations_update_registry() -> None:
    """Add and remove content references from the registry."""
    registry = ProjectRegistry()

    first_reference = ContentReference(
        content_type=ContentType.MATERIALS,
        qualified_id="test.first_mod.clay",
    )
    second_reference = ContentReference(
        content_type=ContentType.MATERIALS,
        qualified_id="test.second_mod.stone",
    )

    registry.add_content_reference(first_reference.content_type, first_reference.qualified_id)
    registry.add_content_reference(second_reference.content_type, second_reference.qualified_id)

    assert registry.get_content_references(ContentType.MATERIALS) == (
        first_reference,
        second_reference,
    )

    registry.remove_content_reference(first_reference.content_type, first_reference.qualified_id)

    assert registry.get_content_references(ContentType.MATERIALS) == (second_reference,)
