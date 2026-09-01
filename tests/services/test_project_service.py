from pathlib import Path

from orebiters_modding_tool.domain.material import MaterialRequirement
from orebiters_modding_tool.infrastructure.localization_repository import LocalizationRepository
from orebiters_modding_tool.infrastructure.material_repository import MaterialRepository
from orebiters_modding_tool.infrastructure.project_repository import ProjectRepository
from orebiters_modding_tool.services.project_service import ProjectService
from tests.factories.content import ContentReferenceFactory
from tests.factories.material import MaterialFactory


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

    project.materials.extend([clay, mud_patch_mix])

    project_service.save_project()

    reopened_project_service = ProjectService(
        project_repository=ProjectRepository(tmp_path),
        localization_repository=LocalizationRepository(tmp_path),
        material_repository=MaterialRepository(tmp_path),
    )

    reopened_project = reopened_project_service.open_project(project.qualified_id)

    assert [material.id for material in reopened_project.materials] == ["clay", "mud_patch_mix"]

    loaded_mud_patch_mix = next(
        material for material in reopened_project.materials if material.id == "mud_patch_mix"
    )

    assert len(loaded_mud_patch_mix.crafting_materials) == 1

    requirement = loaded_mud_patch_mix.crafting_materials[0]

    assert requirement.material == ContentReferenceFactory.from_content(
        clay,
        mod_id=project.qualified_id,
    )
    assert requirement.amount == 2
