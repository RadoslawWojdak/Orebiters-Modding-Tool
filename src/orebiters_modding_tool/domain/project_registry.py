from collections.abc import Mapping
from types import MappingProxyType

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
        return tuple(self._projects)

    @property
    def project_references(self) -> Mapping[ContentType, tuple[ContentReference, ...]]:
        """Return references to content from all projects.

        :returns: Content references grouped by content type.
        """
        return MappingProxyType(
            {
                content_type: tuple(references)
                for content_type, references in self._project_references.items()
            }
        )

    def add_project(self, project: Project) -> None:
        """Add a project to the registry.

        :param project: Project to add.
        """
        self._projects.append(project)
        self._add_project_references(project)

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

    def add_content_reference(self, reference: ContentReference) -> None:
        """Add a content reference to the registry.

        :param reference: Reference to add.
        """
        self._project_references[reference.content_type].append(reference)

    def remove_content_reference(self, reference: ContentReference) -> None:
        """Remove a content reference from the registry.

        :param reference: Reference to remove.
        """
        self._project_references[reference.content_type].remove(reference)

    def _add_project_references(self, project: Project) -> None:
        """Add references to all content belonging to a project.

        :param project: Project whose content should be indexed.
        """
        for content_type, items in project.content.items():
            for item in items:
                reference = ContentReference(
                    content_type=content_type,
                    qualified_id=item.get_qualified_id(project.qualified_id),
                )
                self.add_content_reference(reference)

    def _remove_project_references(self, project: Project) -> None:
        """Remove references to all content belonging to a project.

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
