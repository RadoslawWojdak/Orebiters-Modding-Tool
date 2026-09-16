from collections.abc import Sequence

from orebiters_modding_tool.domain.content import ContentReference, ContentType
from orebiters_modding_tool.domain.project import Project


class ProjectRegistry:
    """Registry of available projects and their content."""

    def __init__(self, projects: list[Project] | None = None) -> None:
        """Initialize the project registry.

        :param projects: Initial projects.
        """
        self._projects: list[Project] = []
        self._project_references: dict[ContentType, list[ContentReference]] = {
            content_type: [] for content_type in ContentType
        }

        for project in projects or []:
            self.add_project(project)

    @property
    def projects(self) -> tuple[Project, ...]:
        """Return all registered projects."""
        return tuple(self._projects)

    def get_content_references(self, content_type: ContentType) -> Sequence[ContentReference]:
        """Return independent references to content of the specified type.

        :param content_type: Type of content to retrieve.
        :returns: Independent references to the requested content.
        """
        return tuple(
            ContentReference(
                content_type=reference.content_type,
                qualified_id=reference.qualified_id,
            )
            for reference in self._project_references[content_type]
        )

    def get_project(self, qualified_id: str) -> Project:
        """Return the project with the specified qualified ID.

        :param qualified_id: Qualified project ID.
        :returns: Matching project.
        :raises ValueError: If no matching project exists.
        """
        for project in self._projects:
            if project.qualified_id == qualified_id:
                return project

        raise ValueError(f"Project not found: {qualified_id}.")

    def add_project(self, project: Project) -> None:
        """Add a project to the registry.

        :param project: Project to add.
        """
        self._projects.append(project)
        self._add_project_references(project)

    def replace_project(self, project: Project) -> None:
        """Replace a registered project.

        :param project: Project replacing the existing registered project.
        """
        for index, existing_project in enumerate(self._projects):
            if existing_project.qualified_id != project.qualified_id:
                continue

            self._projects[index] = project
            self._remove_project_references(existing_project)
            self._add_project_references(project)
            return

        self.add_project(project)

    def remove_project(self, project: Project) -> None:
        """Remove a project from the registry.

        :param project: Project to remove.
        """
        self._projects.remove(project)
        self._remove_project_references(project)

    def has_content_reference(self, content_type: ContentType, qualified_id: str) -> bool:
        """Check whether a content reference is registered.

        :param content_type: Type of content.
        :param qualified_id: Qualified content ID.
        :returns: Whether the reference is registered.
        """
        return any(
            reference.qualified_id == qualified_id
            for reference in self._project_references[content_type]
        )

    def add_content_reference(self, content_type: ContentType, qualified_id: str) -> None:
        """Register a content reference.

        :param content_type: Type of content.
        :param qualified_id: Qualified content ID.
        """
        reference = ContentReference(content_type=content_type, qualified_id=qualified_id)
        self._project_references[content_type].append(reference)

    def remove_content_reference(self, content_type: ContentType, qualified_id: str) -> None:
        """Unregister a content reference.

        :param content_type: Type of content.
        :param qualified_id: Qualified content ID.
        """
        reference = ContentReference(content_type=content_type, qualified_id=qualified_id)
        self._project_references[content_type].remove(reference)

    def _add_project_references(self, project: Project) -> None:
        """Register references to all content belonging to a project.

        :param project: Project whose content should be indexed.
        """
        for content_type, items in project.content.items():
            for item in items:
                qualified_id = item.get_qualified_id(project.qualified_id)
                self.add_content_reference(content_type, qualified_id)

    def _remove_project_references(self, project: Project) -> None:
        """Unregister references to all content belonging to a project.

        :param project: Project whose content should be removed.
        """
        project_qualified_id = project.qualified_id

        for references in self._project_references.values():
            references_to_remove = [
                reference
                for reference in references
                if reference.qualified_id is not None
                and reference.qualified_id.startswith(f"{project_qualified_id}.")
            ]

            for reference in references_to_remove:
                references.remove(reference)
