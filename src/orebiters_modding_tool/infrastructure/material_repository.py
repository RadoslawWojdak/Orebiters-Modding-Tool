from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from orebiters_modding_tool.domain.content import ContentReference, ContentType
from orebiters_modding_tool.domain.material import Material, MaterialRequirement
from orebiters_modding_tool.domain.project import Project


class MaterialRepository:
    """Handle material persistence on the file system."""

    _MATERIALS_DIRECTORY_NAME = "materials"

    def __init__(self, mods_directory: Path) -> None:
        """Initialize the material repository.

        :param mods_directory: Directory containing all mod projects.
        """
        self._mods_directory = mods_directory

    def load_all(self, project: Project) -> list[Material]:
        """Load all materials belonging to a project.

        :param project: Project whose materials should be loaded.
        :returns: Loaded materials.
        """
        materials_directory = self._get_materials_directory(project)

        if not materials_directory.exists():
            return []

        material_file_paths = sorted(materials_directory.glob("*.json"))

        return [self._load_file(material_file_path) for material_file_path in material_file_paths]

    def load(self, project: Project, material_id: str) -> Material:
        """Load a material from a project.

        :param project: Project containing the material.
        :param material_id: Local ID of the material to load.
        :returns: Loaded material.
        """
        material_file_path = self._get_material_file_path(project, material_id)

        return self._load_file(material_file_path)

    def list_material_ids(self, project: Project) -> list[str]:
        """Return IDs of all materials belonging to a project.

        :param project: Project whose material IDs should be returned.
        :returns: Sorted list of material IDs.
        """
        materials_directory = self._get_materials_directory(project)

        if not materials_directory.exists():
            return []

        return sorted(
            material_file_path.stem for material_file_path in materials_directory.glob("*.json")
        )

    def save(self, project: Project, material: Material) -> None:
        """Save a material to a project.

        :param project: Project containing the material.
        :param material: Material to save.
        """
        materials_directory = self._get_materials_directory(project)
        materials_directory.mkdir(parents=True, exist_ok=True)

        material_file_path = self._get_material_file_path(project, material.id)
        data = self._serialize_material(project, material)

        with material_file_path.open("w", encoding="utf-8") as file:
            json.dump(data, file, ensure_ascii=False, indent=4)

    def delete(self, project: Project, material_id: str) -> None:
        """Delete a material from a project.

        :param project: Project containing the material.
        :param material_id: Local ID of the material to delete.
        """
        material_file_path = self._get_material_file_path(project, material_id)
        material_file_path.unlink()

    def _load_file(self, material_file_path: Path) -> Material:
        """Load a material from a JSON file.

        :param material_file_path: Path to the material file.
        :returns: Loaded material.
        """
        with material_file_path.open("r", encoding="utf-8") as file:
            data = json.load(file)

        return self._deserialize_material(data)

    @staticmethod
    def _serialize_material(project: Project, material: Material) -> dict[str, object]:
        """Serialize a material to JSON-compatible data.

        :param project: Project containing the material.
        :param material: Material to serialize.
        :returns: Serialized material data.
        """
        return {
            "id": material.get_qualified_id(project.qualified_id),
            "icon_tag": f"materials:{material.id}",
            "crafting_materials": {
                requirement.material_reference.qualified_id: requirement.amount
                for requirement in material.crafting_materials
            },
        }

    @staticmethod
    def _deserialize_material(data: dict[str, Any]) -> Material:
        """Deserialize a material from JSON data.

        :param data: JSON material data.
        :returns: Deserialized material.
        """
        qualified_id = data["id"]
        material_id = qualified_id.rsplit(".", maxsplit=1)[1]

        crafting_materials_data = data.get("crafting_materials", {})

        crafting_materials = [
            MaterialRequirement(
                material_reference=ContentReference(
                    content_type=ContentType.MATERIALS,
                    qualified_id=qualified_id,
                ),
                amount=amount,
            )
            for qualified_id, amount in crafting_materials_data.items()
        ]

        return Material(id=material_id, localizations={}, crafting_materials=crafting_materials)

    def _get_materials_directory(self, project: Project) -> Path:
        """Return the materials directory for a project.

        :param project: Project whose materials directory is requested.
        :returns: Materials directory path.
        """
        project_directory = self._mods_directory / project.qualified_id

        return project_directory / self._MATERIALS_DIRECTORY_NAME

    def _get_material_file_path(self, project: Project, material_id: str) -> Path:
        """Return the file path for a material.

        :param project: Project containing the material.
        :param material_id: Local ID of the material.
        :returns: Material file path.
        """
        return self._get_materials_directory(project) / f"{material_id}.json"
