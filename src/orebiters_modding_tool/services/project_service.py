from collections import defaultdict
from collections.abc import Sequence
from typing import Any, cast

from orebiters_modding_tool.domain.content import Content, ContentReference, ContentType
from orebiters_modding_tool.domain.material import Material, MaterialLocalization
from orebiters_modding_tool.domain.project import Project
from orebiters_modding_tool.domain.project_identifier import normalize_identifier
from orebiters_modding_tool.domain.project_registry import ProjectRegistry
from orebiters_modding_tool.infrastructure.localization_repository import LocalizationRepository
from orebiters_modding_tool.infrastructure.material_repository import MaterialRepository
from orebiters_modding_tool.infrastructure.project_repository import ProjectRepository


class ProjectService:
    """Manage projects and their persistence."""

    def __init__(
        self,
        project_repository: ProjectRepository,
        localization_repository: LocalizationRepository,
        material_repository: MaterialRepository,
    ) -> None:
        """Initialize the project service.

        :param project_repository: Repository used for project persistence.
        :param localization_repository: Repository used for localization persistence.
        :param material_repository: Repository used for material persistence.
        """
        self._project_repository = project_repository
        self._localization_repository = localization_repository
        self._material_repository = material_repository

        self._project_registry = ProjectRegistry(self._load_all_projects())
        self._active_project: Project | None = None

    @property
    def active_project(self) -> Project | None:
        """Return the currently active project."""
        return self._active_project

    @property
    def has_active_project(self) -> bool:
        """Return whether a project is currently active."""
        return self._active_project is not None

    @property
    def has_unsaved_changes(self) -> bool:
        """Return whether the active project has unsaved changes."""
        return self._active_project is not None and self._active_project.has_unsaved_changes

    def get_content_references(self, content_type: ContentType) -> Sequence[ContentReference]:
        """Return references to content of the specified type.

        :param content_type: Type of content to retrieve.
        :returns: References to the requested content.
        """
        return self._project_registry.get_content_references(content_type)

    def mark_project_as_modified(self) -> None:
        """Mark the active project as having unsaved changes."""
        self._require_active_project().has_unsaved_changes = True

    def _mark_project_as_saved(self) -> None:
        """Mark the active project as having no unsaved changes."""
        self._require_active_project().has_unsaved_changes = False

    def create_project(self, namespace: str, name: str) -> Project:
        """Create, persist, and activate a new project.

        :param namespace: Namespace used for the project identifier.
        :param name: Human-readable project name.
        :returns: Created project.
        """
        normalized_namespace = normalize_identifier(namespace)
        mod_id = normalize_identifier(name)

        project = Project(namespace=normalized_namespace, mod_id=mod_id, name=name)
        self._project_repository.create(project)
        self._project_registry.add_project(project)
        self._active_project = project

        return project

    def open_project(self, qualified_id: str) -> Project:
        """Open a project from persistent storage.

        :param qualified_id: Namespace-qualified project identifier.
        :returns: Opened project.
        """
        project = self._load_project(qualified_id)

        self._project_registry.replace_project(project)
        self._active_project = project

        self.refresh_projects()

        return project

    def refresh_projects(self) -> None:
        """Refresh non-active projects from persistent storage."""
        active_project_id = (
            self._active_project.qualified_id if self._active_project is not None else None
        )
        project_ids = self._project_repository.list_project_qualified_ids()

        for qualified_id in project_ids:
            if qualified_id == active_project_id:
                continue

            self._project_registry.replace_project(self._load_project(qualified_id))

        for project in self._project_registry.projects:
            if project.qualified_id == active_project_id:
                continue

            if project.qualified_id not in project_ids:
                self._project_registry.remove_project(project)

    def list_project_qualified_ids(self) -> list[str]:
        """Return a sorted list of qualified identifiers of all available projects."""
        return self._project_repository.list_project_qualified_ids()

    def save_project(self) -> None:
        """Save the currently active project."""
        project = self._require_active_project()

        self._project_repository.save(project)
        self._save_materials(project)
        self._save_localizations(project)

        self._mark_project_as_saved()

    def close_project(self) -> None:
        """Close the currently active project."""
        self._active_project = None

    def add_content(self, content_type: ContentType, content: Content[Any]) -> None:
        """Add content to the active project and registry.

        :param content_type: Type of content to add.
        :param content: Content to add.
        """
        project = self._require_active_project()

        qualified_id = content.get_qualified_id(project.qualified_id)

        if self._project_registry.has_content_reference(content_type, qualified_id):
            raise ValueError(f"Content with ID '{content.id}' already exists.")

        project.content[content_type].append(content)
        self._project_registry.add_content_reference(content_type, qualified_id)
        self.mark_project_as_modified()

    def remove_content(self, content_type: ContentType, content: Content[Any]) -> None:
        """Remove content from the active project and registry.

        :param content_type: Type of content to remove.
        :param content: Content to remove.
        """
        project = self._require_active_project()

        qualified_id = content.get_qualified_id(project.qualified_id)

        project.content[content_type].remove(content)
        self._project_registry.remove_content_reference(content_type, qualified_id)
        self.mark_project_as_modified()

    def _require_active_project(self) -> Project:
        """Return the active project.

        :returns: Currently active project.
        :raises RuntimeError: If no project is currently active.
        """
        if self._active_project is None:
            raise RuntimeError("No project is currently active.")

        return self._active_project

    def _save_materials(self, project: Project) -> None:
        """Synchronize project materials with persistent storage.

        :param project: Project whose materials should be saved.
        """
        materials = cast(list[Material], project.content[ContentType.MATERIALS])

        existing_material_ids = set(self._material_repository.list_material_ids(project))
        current_material_ids = {material.id for material in materials}

        for material in materials:
            self._material_repository.save(project, material)

        deleted_material_ids = existing_material_ids - current_material_ids

        for material_id in deleted_material_ids:
            self._material_repository.delete(project, material_id)

    def _save_localizations(self, project: Project) -> None:
        """Synchronize project localizations with persistent storage.

        :param project: Project whose localizations should be saved.
        """
        localization_data: dict[str, dict[str, str]] = defaultdict(dict)

        for material in project.content[ContentType.MATERIALS]:
            prefix = f"config.{material.id}"

            for language, localization in material.localizations.items():
                entries = localization_data[language]

                entries[f"{prefix}.one"] = localization.one
                entries[f"{prefix}.few"] = localization.few
                entries[f"{prefix}.many"] = localization.many
                entries[f"{prefix}.hint"] = localization.hint
                entries[f"{prefix}.description"] = localization.description

        existing_languages = set(self._localization_repository.list_languages(project))
        current_languages = set(localization_data)

        self._localization_repository.save_all(project, localization_data)

        deleted_languages = existing_languages - current_languages

        for language in deleted_languages:
            self._localization_repository.delete(project, language)

    def _load_all_projects(self) -> list[Project]:
        """Load all available projects from persistent storage."""
        return [
            self._load_project(qualified_id)
            for qualified_id in self._project_repository.list_project_qualified_ids()
        ]

    def _load_project(self, qualified_id: str) -> Project:
        """Load a complete project from persistent storage.

        :param qualified_id: Full project identifier.
        :returns: Loaded project.
        """
        project = self._project_repository.load(qualified_id)

        project.content[ContentType.MATERIALS] = cast(
            list[Content[Any]],
            self._material_repository.load_all(project),
        )

        localization_data = self._localization_repository.load_all(project)
        self._load_material_localizations(project, localization_data)

        return project

    @staticmethod
    def _load_material_localizations(
        project: Project,
        localization_data: dict[str, dict[str, str]],
    ) -> None:
        """Apply localization data to project materials."""
        for language, entries in localization_data.items():
            for material in project.content[ContentType.MATERIALS]:
                prefix = f"config.{material.id}"

                material.localizations[language] = MaterialLocalization(
                    one=entries[f"{prefix}.one"],
                    few=entries[f"{prefix}.few"],
                    many=entries[f"{prefix}.many"],
                    hint=entries[f"{prefix}.hint"],
                    description=entries[f"{prefix}.description"],
                )
