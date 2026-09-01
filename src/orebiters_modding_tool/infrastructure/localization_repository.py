from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from orebiters_modding_tool.domain.project import Project


class LocalizationRepository:
    """Handle localization persistence on the file system."""

    _LOCALIZATION_DIRECTORY_NAME = "localization"

    def __init__(self, mods_directory: Path) -> None:
        """Initialize the localization repository.

        :param mods_directory: Directory containing all mod projects.
        """
        self._mods_directory = mods_directory

    def load_all(self, project: Project) -> dict[str, dict[str, str]]:
        """Load all localizations belonging to a project.

        :param project: Project whose localizations should be loaded.
        :returns: Mapping of language codes to localization entries.
        """
        localization_directory = self._get_localization_directory(project)

        if not localization_directory.exists():
            return {}

        localization_file_paths = sorted(localization_directory.glob("*.json"))

        return {
            localization_file_path.stem: self._load_file(localization_file_path)
            for localization_file_path in localization_file_paths
        }

    def load(self, project: Project, language: str) -> dict[str, str]:
        """Load localization entries for a language.

        :param project: Project containing the localization.
        :param language: Language code to load.
        :returns: Localization entries.
        """
        localization_file_path = self._get_localization_file_path(project, language)

        return self._load_file(localization_file_path)

    def list_languages(self, project: Project) -> list[str]:
        """Return all available localization languages.

        :param project: Project whose localization languages should be returned.
        :returns: Sorted list of language codes.
        """
        localization_directory = self._get_localization_directory(project)

        if not localization_directory.exists():
            return []

        return sorted(
            localization_file_path.stem
            for localization_file_path in localization_directory.glob("*.json")
        )

    def save_all(self, project: Project, localization_data: dict[str, dict[str, str]]) -> None:
        """Save localization entries for all languages.

        :param project: Project containing the localization.
        :param localization_data: Mapping of language codes to localization entries.
        """
        for language, localizations in localization_data.items():
            self.save(project, language, localizations)

    def save(self, project: Project, language: str, localizations: dict[str, str]) -> None:
        """Save localization entries for a language.

        :param project: Project containing the localization.
        :param language: Language code to save.
        :param localizations: Localization entries to save.
        """
        localization_directory = self._get_localization_directory(project)
        localization_directory.mkdir(parents=True, exist_ok=True)

        localization_file_path = self._get_localization_file_path(project, language)

        with localization_file_path.open("w", encoding="utf-8") as file:
            json.dump(localizations, file, ensure_ascii=False, indent=4)

    def delete(self, project: Project, language: str) -> None:
        """Delete localization entries for a language.

        :param project: Project containing the localization.
        :param language: Language code to delete.
        """
        localization_file_path = self._get_localization_file_path(project, language)
        localization_file_path.unlink()

    @staticmethod
    def _load_file(localization_file_path: Path) -> dict[str, str]:
        """Load localization entries from a JSON file.

        :param localization_file_path: Path to the localization file.
        :returns: Loaded localization entries.
        """
        with localization_file_path.open("r", encoding="utf-8") as file:
            data: Any = json.load(file)

        if not isinstance(data, dict):
            raise ValueError(
                f"Localization file must contain a JSON object: {localization_file_path}",
            )

        if not all(isinstance(key, str) and isinstance(value, str) for key, value in data.items()):
            raise ValueError(
                f"Localization file must contain string keys and values: {localization_file_path}",
            )

        return data

    def _get_localization_directory(self, project: Project) -> Path:
        """Return the localization directory for a project.

        :param project: Project whose localization directory is requested.
        :returns: Localization directory path.
        """
        project_directory = self._mods_directory / project.qualified_id

        return project_directory / self._LOCALIZATION_DIRECTORY_NAME

    def _get_localization_file_path(self, project: Project, language: str) -> Path:
        """Return the file path for a localization language.

        :param project: Project containing the localization.
        :param language: Language code of the localization.
        :returns: Localization file path.
        """
        return self._get_localization_directory(project) / f"{language}.json"
