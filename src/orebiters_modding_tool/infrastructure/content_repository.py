import json
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, ClassVar, TypeVar

from orebiters_modding_tool.domain.content import Content, ContentState, ContentType
from orebiters_modding_tool.domain.project import Project

TContent = TypeVar("TContent", bound=Content[Any])


class ContentRepository[T: Content[Any]](ABC):
    """Handle generic content persistence on the file system."""

    CONTENT_TYPE: ClassVar[ContentType | None] = None

    _registry: ClassVar[dict[ContentType, type[ContentRepository[Any]]]] = {}

    def __init__(self, mods_directory: Path) -> None:
        """Initialize the content repository.

        :param mods_directory: Directory containing all mod projects.
        """
        self._mods_directory = mods_directory

    def __init_subclass__(cls, **kwargs: Any) -> None:
        """Register concrete content repository subclasses."""
        super().__init_subclass__(**kwargs)
        cls._register()

    @classmethod
    def get_class(cls, content_type: ContentType) -> type[ContentRepository[Any]]:
        """Return the repository class registered for the given content type.

        :param content_type: Type of content to retrieve.
        :returns: Registered repository class.
        :raises KeyError: If no repository is registered for the given type.
        """
        return cls._registry[content_type]

    def load_all(self, project: Project) -> list[T]:
        """Load all content items belonging to a project.

        :param project: Project whose content should be loaded.
        :returns: Loaded content items.
        """
        content_directory = self._get_directory_path(project)

        if not content_directory.exists():
            return []

        file_paths = sorted(content_directory.glob("*.json"))

        return [self._load_file(file_path) for file_path in file_paths]

    def load(self, project: Project, content_id: str) -> T:
        """Load a content item from a project.

        :param project: Project containing the content.
        :param content_id: Local content ID.
        :returns: Loaded content item.
        """
        return self._load_file(self._get_file_path(project, content_id))

    def list_ids(self, project: Project) -> list[str]:
        """Return sorted IDs of all content items.

        :param project: Project whose content IDs should be returned.
        :returns: Sorted content IDs.
        """
        content_directory = self._get_directory_path(project)

        if not content_directory.exists():
            return []

        return sorted(file_path.stem for file_path in content_directory.glob("*.json"))

    def save(self, project: Project, content: T) -> None:
        """Save a content item to a project.

        :param project: Project containing the content.
        :param content: Content item to save.
        """
        content_directory = self._get_directory_path(project)
        content_directory.mkdir(parents=True, exist_ok=True)

        file_path = self._get_file_path(project, content.id)
        data = self._serialize(project, content)

        with file_path.open("w", encoding="utf-8") as file:
            json.dump(data, file, ensure_ascii=False, indent=4)

        content.state = ContentState.SAVED

    def delete(self, project: Project, content_id: str) -> None:
        """Delete a content item from a project.

        :param project: Project containing the content.
        :param content_id: Local content ID.
        """
        self._get_file_path(project, content_id).unlink()

    def _load_file(self, file_path: Path) -> T:
        """Load and deserialize a content file.

        :param file_path: Path to the content file.
        :returns: Deserialized content item.
        """
        with file_path.open("r", encoding="utf-8") as file:
            data = json.load(file)

        return self._deserialize(data)

    def _get_directory_path(self, project: Project) -> Path:
        """Return the content directory path for a project.

        :param project: Project containing the content.
        :returns: Content directory path.
        """
        return self._mods_directory / project.qualified_id / self._get_directory_name()

    @classmethod
    def _get_directory_name(cls) -> str:
        if cls.CONTENT_TYPE is None:
            raise NotImplementedError(f"{cls.__name__} must define CONTENT_TYPE")

        return str(cls.CONTENT_TYPE.value)

    def _get_file_path(self, project: Project, content_id: str) -> Path:
        """Return the file path for a content item.

        :param project: Project containing the content.
        :param content_id: Local content ID.
        :returns: Content file path.
        """
        return self._get_directory_path(project) / f"{content_id}.json"

    @abstractmethod
    def _serialize(self, project: Project, content: T) -> dict[str, object]:
        """Serialize content into JSON-compatible data.

        :param project: Project containing the content.
        :param content: Content item to serialize.
        :returns: Serialized content data.
        """

    @abstractmethod
    def _deserialize(self, data: dict[str, Any]) -> T:
        """Deserialize JSON-compatible data into content.

        :param data: Serialized content data.
        :returns: Deserialized content item.
        """

    @classmethod
    def _register(cls) -> None:
        """Register the content repository class."""
        content_type = cls.__dict__.get("CONTENT_TYPE")

        if content_type is None:
            return

        if content_type in ContentRepository._registry:
            raise ValueError(f"Content table model for '{content_type}' is already registered.")

        ContentRepository._registry[content_type] = cls
