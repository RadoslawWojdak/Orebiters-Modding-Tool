from __future__ import annotations

import json
from pathlib import Path

from orebiters_modding_tool.domain.project import Project


class ProjectRepository:
    """Handles project persistence on the file system."""

    _PROJECT_FILE_NAME = "mod.json"

    def __init__(self, mods_directory: Path) -> None:
        """Initialize the project repository.

        :param mods_directory: Directory containing all mod projects.
        """
        self._mods_directory = mods_directory

    def create(self, project: Project) -> None:
        """Create a new project directory and project file.

        :param project: Project to create.
        """
        project_directory = self._get_project_directory(project)

        project_directory.mkdir(parents=True, exist_ok=False)

        self.save(project)

    def load(self, qualified_id: str) -> Project:
        """Load a project by its qualified identifier.

        :param qualified_id: Full project identifier.
        :returns: Loaded project.
        """
        project_directory = self._mods_directory / qualified_id
        project_file_path = project_directory / self._PROJECT_FILE_NAME

        with project_file_path.open("r", encoding="utf-8") as file:
            data = json.load(file)

        return Project(namespace=data["namespace"], mod_id=data["id"], name=data["name"])

    def load_all(self) -> list[Project]:
        """Load all available projects.

        :returns: List of loaded projects.
        """
        if not self._mods_directory.is_dir():
            return []

        projects: list[Project] = []

        for project_directory in self._mods_directory.iterdir():
            if not project_directory.is_dir():
                continue

            project_file_path = project_directory / self._PROJECT_FILE_NAME

            if not project_file_path.is_file():
                continue

            project = self.load(project_directory.name)
            projects.append(project)

        return sorted(projects, key=lambda project: project.name.lower())

    def list_project_qualified_ids(self) -> list[str]:
        """Return a sorted list of qualified identifiers of all available projects."""
        if not self._mods_directory.exists():
            return []

        project_ids = [
            directory.name
            for directory in self._mods_directory.iterdir()
            if directory.is_dir() and (directory / self._PROJECT_FILE_NAME).is_file()
        ]

        return sorted(project_ids)

    def save(self, project: Project) -> None:
        """Save a project to its directory.

        :param project: Project to save.
        """
        project_file_path = self._get_project_directory(project) / self._PROJECT_FILE_NAME

        data = {
            "namespace": project.namespace,
            "id": project.mod_id,
            "name": project.name,
        }

        with project_file_path.open("w", encoding="utf-8") as file:
            json.dump(data, file, ensure_ascii=False, indent=4)

    def _get_project_directory(self, project: Project) -> Path:
        """Return the directory for a project.

        :param project: Project whose directory should be returned.
        :returns: Project directory path.
        """
        return self._mods_directory / project.qualified_id
