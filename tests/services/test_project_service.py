import shutil
from pathlib import Path
from typing import cast

import pytest

from orebiters_modding_tool.domain.content import ContentType
from orebiters_modding_tool.domain.material import Material, MaterialLocalization
from orebiters_modding_tool.infrastructure.localization_repository import LocalizationRepository
from orebiters_modding_tool.infrastructure.material_repository import MaterialRepository
from orebiters_modding_tool.infrastructure.project_repository import ProjectRepository
from orebiters_modding_tool.services.project_service import ProjectService
from tests.factories.content import ContentReferenceFactory
from tests.factories.material import MaterialFactory
from tests.factories.material_requirement import MaterialRequirementFactory


def create_project_service(tmp_path: Path) -> ProjectService:
    """Create a project service using temporary storage.

    :param tmp_path: Temporary storage directory.
    :returns: Configured project service.
    """
    return ProjectService(
        project_repository=ProjectRepository(tmp_path),
        localization_repository=LocalizationRepository(tmp_path),
        material_repository=MaterialRepository(tmp_path),
    )


def test_create_project_normalizes_identifiers_and_activates_project(
    project_service: ProjectService,
) -> None:
    """Verify that creating a project normalizes its identifiers and activates it."""
    project = project_service.create_project(
        namespace="My Namespace",
        name="My Mod",
    )

    assert project.namespace == "my_namespace"
    assert project.mod_id == "my_mod"
    assert project_service.active_project is project
    assert project_service.has_active_project


def test_close_project_clears_active_project(project_service: ProjectService) -> None:
    """Verify that closing a project clears the active project."""
    project_service.create_project(namespace="test", name="Test Mod")

    project_service.close_project()

    assert project_service.active_project is None
    assert not project_service.has_active_project


def test_get_content_references_returns_references_from_all_projects(
    project_service: ProjectService,
) -> None:
    """Verify that content references include content from all projects."""
    first_project = project_service.create_project(namespace="test", name="First Mod")
    first_material = MaterialFactory.create(id="clay")
    project_service.add_content(ContentType.MATERIALS, first_material)
    project_service.save_project()

    second_project = project_service.create_project(namespace="test", name="Second Mod")
    second_material = MaterialFactory.create(id="stone")
    project_service.add_content(ContentType.MATERIALS, second_material)
    project_service.save_project()

    references = project_service.get_content_references(ContentType.MATERIALS)

    assert set(references) == {
        ContentReferenceFactory.from_content(first_material, mod_id=first_project.qualified_id),
        ContentReferenceFactory.from_content(second_material, mod_id=second_project.qualified_id),
    }


def test_open_project_loads_saved_materials(tmp_path: Path) -> None:
    """Verify that opening a project loads its saved materials."""
    project_service = create_project_service(tmp_path)

    project = project_service.create_project(namespace="test", name="Test Mod")

    clay = MaterialFactory.create(id="clay")

    mud_patch_mix = MaterialFactory.create(
        id="mud_patch_mix",
        crafting_materials=[
            MaterialRequirementFactory.create(
                ContentReferenceFactory.from_content(clay, mod_id=project.qualified_id),
                amount=2,
            ),
        ],
    )

    project_service.add_content(ContentType.MATERIALS, clay)
    project_service.add_content(ContentType.MATERIALS, mud_patch_mix)

    project_service.save_project()

    reopened_project_service = create_project_service(tmp_path)

    reopened_project = reopened_project_service.open_project(project.qualified_id)
    materials = cast(list[Material], reopened_project.content[ContentType.MATERIALS])

    assert [material.id for material in materials] == ["clay", "mud_patch_mix"]

    loaded_mud_patch_mix = next(
        material for material in materials if material.id == "mud_patch_mix"
    )

    assert len(loaded_mud_patch_mix.crafting_materials) == 1

    requirement = loaded_mud_patch_mix.crafting_materials[0]

    assert requirement.material_reference == ContentReferenceFactory.from_content(
        clay,
        mod_id=project.qualified_id,
    )
    assert requirement.amount == 2


def test_list_project_qualified_ids_returns_available_projects(tmp_path: Path) -> None:
    """Return qualified IDs of available projects."""
    project_service = create_project_service(tmp_path)

    first_project = project_service.create_project(namespace="test", name="First Mod")
    project_service.close_project()

    second_project = project_service.create_project(namespace="test", name="Second Mod")

    assert project_service.list_project_qualified_ids() == [
        first_project.qualified_id,
        second_project.qualified_id,
    ]


def test_add_content_raises_for_duplicate_content(project_service: ProjectService) -> None:
    """Raise an error when adding content with an existing ID."""
    project_service.create_project(namespace="test", name="Test Mod")

    first_material = MaterialFactory.create(id="clay")
    second_material = MaterialFactory.create(id="clay")

    project_service.add_content(ContentType.MATERIALS, first_material)

    with pytest.raises(ValueError, match="Content with ID 'clay' already exists."):
        project_service.add_content(ContentType.MATERIALS, second_material)


def test_save_project_raises_without_active_project(project_service: ProjectService) -> None:
    """Raise an error when saving without an active project."""
    with pytest.raises(RuntimeError, match="No project is currently active."):
        project_service.save_project()


def test_save_project_deletes_removed_materials(tmp_path: Path) -> None:
    """Delete materials that are no longer present in the project."""
    project_service = create_project_service(tmp_path)

    project = project_service.create_project(namespace="test", name="Test Mod")

    clay = MaterialFactory.create(id="clay")
    stone = MaterialFactory.create(id="stone")

    project_service.add_content(ContentType.MATERIALS, clay)
    project_service.add_content(ContentType.MATERIALS, stone)
    project_service.save_project()

    project_service.remove_content(ContentType.MATERIALS, stone)
    project_service.save_project()

    assert MaterialRepository(tmp_path).list_material_ids(project) == ["clay"]


def test_save_project_deletes_removed_localization_languages(tmp_path: Path) -> None:
    """Delete localization languages that are no longer present in the project."""
    project_service = create_project_service(tmp_path)

    project = project_service.create_project(namespace="test", name="Test Mod")

    material = MaterialFactory.create(
        id="clay",
        localizations={
            "en": MaterialLocalization(
                one="Clay",
                few="Clays",
                many="Clay",
                hint="Clay",
                description="Clay",
            ),
            "pl": MaterialLocalization(
                one="Glina",
                few="Gliny",
                many="Glin",
                hint="Glina",
                description="Glina",
            ),
        },
    )

    project_service.add_content(ContentType.MATERIALS, material)
    project_service.save_project()

    del material.localizations["pl"]
    project_service.save_project()

    assert LocalizationRepository(tmp_path).list_languages(project) == ["en"]


# =============================================================================
# Project State
# =============================================================================


def test_mark_project_as_modified_marks_active_project_as_modified(
    project_service: ProjectService,
) -> None:
    """Mark the active project as having unsaved changes."""
    project = project_service.create_project(namespace="test", name="Test Mod")

    project_service.mark_project_as_modified()

    assert project.has_unsaved_changes


def test_mark_project_as_modified_raises_without_active_project(
    project_service: ProjectService,
) -> None:
    """Raise an error when marking a project as modified without an active project."""
    with pytest.raises(RuntimeError, match="No project is currently active."):
        project_service.mark_project_as_modified()


def test_add_content_marks_project_as_modified(project_service: ProjectService) -> None:
    """Mark the project as modified when content is added."""
    project = project_service.create_project(namespace="test", name="Test Mod")
    material = MaterialFactory.create(id="clay")

    assert not project.has_unsaved_changes

    project_service.add_content(ContentType.MATERIALS, material)

    assert project.has_unsaved_changes


def test_remove_content_marks_project_as_modified(project_service: ProjectService) -> None:
    """Mark the project as modified when content is removed."""
    project = project_service.create_project(namespace="test", name="Test Mod")
    material = MaterialFactory.create(id="clay")

    project_service.add_content(ContentType.MATERIALS, material)
    project_service.save_project()

    assert not project.has_unsaved_changes

    project_service.remove_content(ContentType.MATERIALS, material)

    assert project.has_unsaved_changes


def test_save_project_marks_project_as_saved(project_service: ProjectService) -> None:
    """Mark the project as saved after successfully saving it."""
    project = project_service.create_project(namespace="test", name="Test Mod")
    material = MaterialFactory.create(id="clay")

    project_service.add_content(ContentType.MATERIALS, material)

    assert project.has_unsaved_changes

    project_service.save_project()

    assert not project.has_unsaved_changes


# =============================================================================
# Project Synchronization
# =============================================================================


def test_refresh_projects_preserves_active_and_reloads_other_projects(tmp_path: Path) -> None:
    """Preserve the active project and reload other projects from disk."""
    project_service = create_project_service(tmp_path)

    active_project = project_service.create_project(namespace="test", name="Core Mod")
    active_material = MaterialFactory.create(id="clay")

    project_service.add_content(ContentType.MATERIALS, active_material)
    project_service.save_project()

    other_project = project_service.create_project(namespace="test", name="Other Mod")
    other_material = MaterialFactory.create(id="stone")

    project_service.add_content(ContentType.MATERIALS, other_material)
    project_service.save_project()

    active_project = project_service.open_project(active_project.qualified_id)
    active_material = cast(list[Material], active_project.content[ContentType.MATERIALS])[0]

    active_material.id = "modified_clay"

    external_service = create_project_service(tmp_path)
    external_service.open_project(other_project.qualified_id)

    external_material = MaterialFactory.create(id="iron")
    external_service.add_content(ContentType.MATERIALS, external_material)
    external_service.save_project()

    project_service.refresh_projects()

    assert project_service.active_project is active_project

    active_materials = cast(list[Material], active_project.content[ContentType.MATERIALS])
    assert [material.id for material in active_materials] == ["modified_clay"]

    refreshed_other = project_service._project_registry.get_project(other_project.qualified_id)
    other_materials = cast(list[Material], refreshed_other.content[ContentType.MATERIALS])

    assert [material.id for material in other_materials] == ["iron", "stone"]


def test_refresh_projects_adds_and_removes_projects_to_match_disk(tmp_path: Path) -> None:
    """Synchronize registered projects with projects available on disk."""
    project_service = create_project_service(tmp_path)

    active_project = project_service.create_project(namespace="test", name="Active Mod")
    project_service.save_project()

    removed_project = project_service.create_project(namespace="test", name="Removed Mod")
    project_service.save_project()

    project_service.open_project(active_project.qualified_id)

    external_service = create_project_service(tmp_path)
    added_project = external_service.create_project(namespace="test", name="Added Mod")
    external_service.save_project()

    shutil.rmtree(tmp_path / removed_project.qualified_id)

    project_service.refresh_projects()

    registered_ids = {
        project.qualified_id for project in project_service._project_registry.projects
    }

    assert registered_ids == {active_project.qualified_id, added_project.qualified_id}


def test_refresh_projects_updates_content_references_for_reloaded_projects(tmp_path: Path) -> None:
    """Update content references when refreshing a project."""
    project_service = create_project_service(tmp_path)

    active_project = project_service.create_project(namespace="test", name="Active Mod")
    project_service.save_project()

    other_project = project_service.create_project(namespace="test", name="Other Mod")
    material = MaterialFactory.create(id="stone")

    project_service.add_content(ContentType.MATERIALS, material)
    project_service.save_project()

    project_service.open_project(active_project.qualified_id)

    external_service = create_project_service(tmp_path)
    external_project = external_service.open_project(other_project.qualified_id)
    external_materials = cast(list[Material], external_project.content[ContentType.MATERIALS])

    external_service.remove_content(ContentType.MATERIALS, external_materials[0])
    external_service.save_project()

    project_service.refresh_projects()

    assert not project_service._project_registry.has_content_reference(
        ContentType.MATERIALS,
        f"{other_project.qualified_id}.stone",
    )


def test_open_project_refreshes_all_projects(tmp_path: Path) -> None:
    """Refresh all projects from persistent storage when opening a project."""
    project_service = create_project_service(tmp_path)

    first_project = project_service.create_project(namespace="test", name="Core Mod")
    first_material = MaterialFactory.create(id="clay")

    project_service.add_content(ContentType.MATERIALS, first_material)
    project_service.save_project()

    second_project = project_service.create_project(namespace="test", name="Test Mod")
    second_material = MaterialFactory.create(id="stone")

    project_service.add_content(ContentType.MATERIALS, second_material)
    project_service.save_project()

    third_project = project_service.create_project(namespace="test", name="Other Mod")
    third_material = MaterialFactory.create(id="sand")

    project_service.add_content(ContentType.MATERIALS, third_material)
    project_service.save_project()

    project_service.open_project(first_project.qualified_id)

    unsaved_material = MaterialFactory.create(id="unsaved")
    project_service.add_content(ContentType.MATERIALS, unsaved_material)

    external_service = create_project_service(tmp_path)

    external_service.open_project(first_project.qualified_id)
    external_first_material = MaterialFactory.create(id="external")
    external_service.add_content(ContentType.MATERIALS, external_first_material)
    external_service.save_project()

    external_service.open_project(second_project.qualified_id)
    external_second_material = MaterialFactory.create(id="iron")
    external_service.add_content(ContentType.MATERIALS, external_second_material)
    external_service.save_project()

    external_service.open_project(third_project.qualified_id)
    external_third_material = MaterialFactory.create(id="gold")
    external_service.add_content(ContentType.MATERIALS, external_third_material)
    external_service.save_project()

    project_service.open_project(second_project.qualified_id)

    refreshed_first = project_service._project_registry.get_project(first_project.qualified_id)
    refreshed_second = project_service._project_registry.get_project(second_project.qualified_id)
    refreshed_third = project_service._project_registry.get_project(third_project.qualified_id)

    first_materials = cast(list[Material], refreshed_first.content[ContentType.MATERIALS])
    second_materials = cast(list[Material], refreshed_second.content[ContentType.MATERIALS])
    third_materials = cast(list[Material], refreshed_third.content[ContentType.MATERIALS])

    assert [material.id for material in first_materials] == ["clay", "external"]
    assert [material.id for material in second_materials] == ["iron", "stone"]
    assert [material.id for material in third_materials] == ["gold", "sand"]
