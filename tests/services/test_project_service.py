from pathlib import Path
from typing import cast

import pytest

from orebiters_modding_tool.domain.content import ContentType
from orebiters_modding_tool.domain.material import (
    Material,
    MaterialLocalization,
    MaterialRequirement,
)
from orebiters_modding_tool.infrastructure.localization_repository import LocalizationRepository
from orebiters_modding_tool.infrastructure.material_repository import MaterialRepository
from orebiters_modding_tool.infrastructure.project_repository import ProjectRepository
from orebiters_modding_tool.services.project_service import ProjectService
from tests.factories.content import ContentReferenceFactory
from tests.factories.material import MaterialFactory


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
    project_repository = ProjectRepository(tmp_path)
    localization_repository = LocalizationRepository(tmp_path)
    material_repository = MaterialRepository(tmp_path)

    project_service = ProjectService(
        project_repository=project_repository,
        localization_repository=localization_repository,
        material_repository=material_repository,
    )

    project = project_service.create_project(namespace="test", name="Test Mod")

    clay = MaterialFactory.create(id="clay")

    mud_patch_mix = MaterialFactory.create(
        id="mud_patch_mix",
        crafting_materials=[
            MaterialRequirement(
                material=ContentReferenceFactory.from_content(clay, mod_id=project.qualified_id),
                amount=2,
            ),
        ],
    )

    project_service.add_content(ContentType.MATERIALS, clay)
    project_service.add_content(ContentType.MATERIALS, mud_patch_mix)

    project_service.save_project()

    reopened_project_service = ProjectService(
        project_repository=ProjectRepository(tmp_path),
        localization_repository=LocalizationRepository(tmp_path),
        material_repository=MaterialRepository(tmp_path),
    )

    reopened_project = reopened_project_service.open_project(project.qualified_id)
    materials = cast(list[Material], reopened_project.content[ContentType.MATERIALS])

    assert [material.id for material in materials] == ["clay", "mud_patch_mix"]

    loaded_mud_patch_mix = next(
        material for material in materials if material.id == "mud_patch_mix"
    )

    assert len(loaded_mud_patch_mix.crafting_materials) == 1

    requirement = loaded_mud_patch_mix.crafting_materials[0]

    assert requirement.material == ContentReferenceFactory.from_content(
        clay,
        mod_id=project.qualified_id,
    )
    assert requirement.amount == 2


def test_list_project_qualified_ids_returns_available_projects(tmp_path: Path) -> None:
    """Return qualified IDs of available projects."""
    project_repository = ProjectRepository(tmp_path)
    localization_repository = LocalizationRepository(tmp_path)
    material_repository = MaterialRepository(tmp_path)

    project_service = ProjectService(
        project_repository=project_repository,
        localization_repository=localization_repository,
        material_repository=material_repository,
    )

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
    project_repository = ProjectRepository(tmp_path)
    localization_repository = LocalizationRepository(tmp_path)
    material_repository = MaterialRepository(tmp_path)

    project_service = ProjectService(
        project_repository=project_repository,
        localization_repository=localization_repository,
        material_repository=material_repository,
    )

    project = project_service.create_project(namespace="test", name="Test Mod")

    clay = MaterialFactory.create(id="clay")
    stone = MaterialFactory.create(id="stone")

    project_service.add_content(ContentType.MATERIALS, clay)
    project_service.add_content(ContentType.MATERIALS, stone)
    project_service.save_project()

    project_service.remove_content(ContentType.MATERIALS, stone)
    project_service.save_project()

    assert material_repository.list_material_ids(project) == ["clay"]


def test_save_project_deletes_removed_localization_languages(tmp_path: Path) -> None:
    """Delete localization languages that are no longer present in the project."""
    project_repository = ProjectRepository(tmp_path)
    localization_repository = LocalizationRepository(tmp_path)
    material_repository = MaterialRepository(tmp_path)

    project_service = ProjectService(
        project_repository=project_repository,
        localization_repository=localization_repository,
        material_repository=material_repository,
    )

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

    assert localization_repository.list_languages(project) == ["en"]
