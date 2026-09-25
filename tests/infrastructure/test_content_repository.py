import json
from pathlib import Path
from typing import Any

import pytest

from orebiters_modding_tool.domain.content import Content, ContentState, ContentType
from orebiters_modding_tool.domain.project import Project
from orebiters_modding_tool.infrastructure.content_repository import ContentRepository
from orebiters_modding_tool.infrastructure.material_repository import MaterialRepository
from tests.factories.content import ContentFactory
from tests.factories.material import MaterialFactory


class ContentRepositorySample(ContentRepository[Content[Any]]):
    """Sample repository for testing generic content persistence."""

    CONTENT_TYPE = None

    @classmethod
    def _get_directory_name(cls) -> str:
        return "sample"

    def _serialize(self, project: Project, content: Content[Any]) -> dict[str, object]:
        return {"id": f"{project.qualified_id}.contents.{content.id}"}

    def _deserialize(self, data: dict[str, Any]) -> Content[Any]:
        qualified_id = data["id"]
        content_id = qualified_id.rsplit(".", maxsplit=1)[1]
        return ContentFactory.create(id=content_id)


@pytest.fixture
def repository(tmp_path: Path) -> ContentRepositorySample:
    """Create a material repository using a temporary directory."""
    return ContentRepositorySample(tmp_path)


def test_get_class_returns_registered_repository() -> None:
    """Return the repository class registered for a content type."""
    assert ContentRepository.get_class(ContentType.MATERIALS) is MaterialRepository


def test_get_class_raises_for_unregistered_content_type() -> None:
    """Raise KeyError when no repository is registered for a content type."""
    unregistered_type = next(
        (
            content_type
            for content_type in ContentType
            if content_type not in ContentRepository._registry
        ),
        None,
    )

    if unregistered_type is None:
        pytest.skip("All content types have registered repositories.")

    with pytest.raises(KeyError):
        ContentRepository.get_class(unregistered_type)


def test_load_all_loads_all_content(
    project: Project,
    repository: ContentRepositorySample,
    tmp_path: Path,
) -> None:
    """Load JSON files in sorted filename order."""
    content_directory = tmp_path / project.qualified_id / "sample"
    content_directory.mkdir(parents=True)

    for content_id in ["zinc", "copper", "iron"]:
        (content_directory / f"{content_id}.json").write_text(
            json.dumps({"id": f"{project.qualified_id}.{content_id}"}),
            encoding="utf-8",
        )

    contents = repository.load_all(project)

    assert [content.id for content in contents] == ["copper", "iron", "zinc"]


def test_load_all_returns_empty_list_when_directory_does_not_exist(
    project: Project,
    repository: ContentRepositorySample,
) -> None:
    """Return an empty list when the content directory is missing."""
    assert repository.load_all(project) == []


def test_list_ids_returns_sorted_ids(
    project: Project,
    repository: ContentRepositorySample,
    tmp_path: Path,
) -> None:
    """Return sorted content IDs from JSON filenames."""
    content_directory = tmp_path / project.qualified_id / "sample"
    content_directory.mkdir(parents=True)

    for content_id in ["zinc", "copper", "iron"]:
        (content_directory / f"{content_id}.json").write_text("{}", encoding="utf-8")

    assert repository.list_ids(project) == ["copper", "iron", "zinc"]


def test_list_ids_returns_empty_list_when_directory_does_not_exist(
    project: Project,
    repository: ContentRepositorySample,
) -> None:
    """Return an empty list when the content directory is missing."""
    assert repository.list_ids(project) == []


def test_save_creates_content_directory(
    project: Project,
    repository: ContentRepositorySample,
    tmp_path: Path,
) -> None:
    """Create the content directory when saving content."""
    repository.save(project, ContentFactory.create())

    content_directory = tmp_path / project.qualified_id / "sample"

    assert content_directory.is_dir()


def test_save_writes_json_file(
    project: Project,
    repository: ContentRepositorySample,
    tmp_path: Path,
) -> None:
    """Write serialized content to a JSON file."""
    material = MaterialFactory.create()

    repository.save(project, material)

    file_path = tmp_path / project.qualified_id / "sample" / f"{material.id}.json"

    assert file_path.is_file()

    with file_path.open("r", encoding="utf-8") as file:
        data = json.load(file)

    assert data == {
        "id": f"{project.qualified_id}.contents.{material.id}",
    }


def test_save_marks_content_as_saved(project: Project, repository: ContentRepositorySample) -> None:
    """Mark content as saved after persisting it."""
    content = ContentFactory.create()

    repository.save(project, content)

    assert content.state == ContentState.SAVED


def test_load_reads_content_from_file(
    project: Project,
    repository: ContentRepositorySample,
    tmp_path: Path,
) -> None:
    """Load content from its JSON file."""
    content_directory = tmp_path / project.qualified_id / "sample"
    content_directory.mkdir(parents=True)

    (content_directory / "iron.json").write_text(
        json.dumps({"id": f"{project.qualified_id}.iron"}),
        encoding="utf-8",
    )

    content = repository.load(project, "iron")

    assert content.id == "iron"


def test_delete_removes_content_file(
    project: Project,
    repository: ContentRepositorySample,
    tmp_path: Path,
) -> None:
    """Delete the JSON file associated with content."""
    content = ContentFactory.create()

    repository.save(project, content)
    repository.delete(project, content.id)

    file_path = tmp_path / project.qualified_id / "sample" / f"{content.id}.json"

    assert not file_path.exists()


def test_delete_raises_when_file_does_not_exist(
    project: Project,
    repository: ContentRepositorySample,
) -> None:
    """Raise FileNotFoundError when deleting a missing file."""
    with pytest.raises(FileNotFoundError):
        repository.delete(project, "missing")
