from collections import defaultdict

from orebiters_modding_tool.domain.material import MaterialLocalization
from orebiters_modding_tool.domain.project import Project
from orebiters_modding_tool.domain.project_identifier import normalize_identifier
from orebiters_modding_tool.infrastructure.localization_repository import LocalizationRepository
from orebiters_modding_tool.infrastructure.material_repository import MaterialRepository
from orebiters_modding_tool.infrastructure.project_repository import ProjectRepository


class ProjectService:
    """Manage the currently active project."""

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
        self._project: Project | None = None

    @property
    def project(self) -> Project | None:
        """Return the currently active project."""
        return self._project

    @property
    def has_active_project(self) -> bool:
        """Return whether a project is currently active."""
        return self._project is not None

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
        self._project = project

        return project

    def open_project(self, qualified_id: str) -> Project:
        """Load and activate an existing project.

        :param qualified_id: Namespace-qualified project identifier.
        :returns: Loaded project.
        """
        project = self._project_repository.load(qualified_id)

        project.materials = self._material_repository.load_all(project)

        localization_data = self._localization_repository.load_all(project)
        self._load_material_localizations(project, localization_data)

        self._project = project

        return project

    def list_projects(self) -> list[Project]:
        """Return all available projects."""
        return self._project_repository.list_projects()

    def list_project_qualified_ids(self) -> list[str]:
        """Return a sorted list of qualified identifiers of all available projects."""
        return self._project_repository.list_project_qualified_ids()

    def save_project(self) -> None:
        """Save the currently active project."""
        project = self._require_active_project()

        self._project_repository.save(project)
        self._save_materials(project)
        self._save_localizations(project)

    def close_project(self) -> None:
        """Close the currently active project."""
        self._project = None

    def _require_active_project(self) -> Project:
        """Return the active project.

        :returns: Currently active project.
        :raises RuntimeError: If no project is currently active.
        """
        if self._project is None:
            raise RuntimeError("No active project.")

        return self._project

    def _save_materials(self, project: Project) -> None:
        """Synchronize project materials with persistent storage.

        :param project: Project whose materials should be saved.
        """
        existing_material_ids = set(self._material_repository.list_material_ids(project))
        current_material_ids = {material.id for material in project.materials}

        for material in project.materials:
            self._material_repository.save(project, material)

        deleted_material_ids = existing_material_ids - current_material_ids

        for material_id in deleted_material_ids:
            self._material_repository.delete(project, material_id)

    def _save_localizations(self, project: Project) -> None:
        """Synchronize project localizations with persistent storage.

        :param project: Project whose localizations should be saved.
        """
        localization_data: dict[str, dict[str, str]] = defaultdict(dict)

        for material in project.materials:
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

    @staticmethod
    def _load_material_localizations(
        project: Project,
        localization_data: dict[str, dict[str, str]],
    ) -> None:
        """Apply localization data to project materials."""
        for language, entries in localization_data.items():
            for material in project.materials:
                prefix = f"config.{material.id}"

                material.localizations[language] = MaterialLocalization(
                    one=entries[f"{prefix}.one"],
                    few=entries[f"{prefix}.few"],
                    many=entries[f"{prefix}.many"],
                    hint=entries[f"{prefix}.hint"],
                    description=entries[f"{prefix}.description"],
                )
