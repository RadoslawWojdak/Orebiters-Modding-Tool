import json
from pathlib import Path

from orebiters_modding_tool.domain.project import Project
from orebiters_modding_tool.infrastructure.project_repository import ProjectRepository


def test_create_and_load_project(tmp_path: Path) -> None:
    """Verify that a project can be created and loaded."""
    repository = ProjectRepository(tmp_path)

    project = Project(namespace="test", mod_id="test_mod", name="Test Mod")
    repository.create(project)

    loaded_project = repository.load(project.qualified_id)

    assert loaded_project == project


def test_save_overwrites_existing_project(tmp_path: Path) -> None:
    """Overwrite an existing project when saving it again."""
    repository = ProjectRepository(tmp_path)

    project = Project(namespace="test", mod_id="test_mod", name="Test Mod")
    repository.create(project)

    updated_project = Project(namespace="test", mod_id="test_mod", name="Updated Mod")
    repository.save(updated_project)

    assert repository.load(project.qualified_id) == updated_project


def test_load_all_returns_empty_list_when_mods_directory_does_not_exist(tmp_path: Path) -> None:
    """Return an empty list when the mods directory does not exist."""
    repository = ProjectRepository(tmp_path / "mods")

    assert repository.load_all() == []


def test_load_all_loads_projects_sorted_by_name(tmp_path: Path) -> None:
    """Load all projects sorted by name case-insensitively."""
    repository = ProjectRepository(tmp_path)

    first_project = Project(namespace="test", mod_id="hm_mod", name="Hardcore Mode")
    second_project = Project(namespace="test", mod_id="ma_mod", name="More Animals")
    third_project = Project(namespace="test", mod_id="ip_mod", name="Ice Planet")

    repository.create(first_project)
    repository.create(second_project)
    repository.create(third_project)

    assert repository.load_all() == [first_project, third_project, second_project]


def test_load_all_ignores_files_and_directories_without_project_file(tmp_path: Path) -> None:
    """Ignore files and directories that do not contain a project file."""
    repository = ProjectRepository(tmp_path)

    valid_project = Project(namespace="test", mod_id="valid_mod", name="Valid Mod")
    repository.create(valid_project)

    (tmp_path / "not_a_project.txt").write_text("not a project", encoding="utf-8")
    (tmp_path / "empty_directory").mkdir()

    assert repository.load_all() == [valid_project]


def test_list_project_qualified_ids_returns_empty_list_when_mods_directory_does_not_exist(
    tmp_path: Path,
) -> None:
    """Return an empty list when the mods directory does not exist."""
    repository = ProjectRepository(tmp_path / "mods")

    assert repository.list_project_qualified_ids() == []


def test_list_project_qualified_ids_returns_sorted_ids(tmp_path: Path) -> None:
    """Return project qualified IDs in sorted order."""
    repository = ProjectRepository(tmp_path)

    projects = [
        Project(namespace="test", mod_id="hm_mod", name="Hardcore Mode"),
        Project(namespace="test", mod_id="ma_mod", name="More Animals"),
        Project(namespace="test", mod_id="ip_mod", name="Ice Planet"),
    ]

    for project in projects:
        repository.create(project)

    assert repository.list_project_qualified_ids() == ["test.hm_mod", "test.ip_mod", "test.ma_mod"]


def test_list_project_qualified_ids_ignores_files_and_directories_without_project_file(
    tmp_path: Path,
) -> None:
    """Ignore files and directories that do not contain a project file."""
    repository = ProjectRepository(tmp_path)

    valid_project = Project(namespace="test", mod_id="valid_mod", name="Valid Mod")
    repository.create(valid_project)

    (tmp_path / "not_a_project.txt").write_text("not a project", encoding="utf-8")
    (tmp_path / "empty_directory").mkdir()

    assert repository.list_project_qualified_ids() == [valid_project.qualified_id]


def test_save_writes_expected_json(tmp_path: Path) -> None:
    """Write the expected project data to JSON."""
    repository = ProjectRepository(tmp_path)

    project = Project(namespace="test", mod_id="test_mod", name="Test Mod")
    repository.create(project)

    project_file = tmp_path / project.qualified_id / "mod.json"

    assert json.loads(project_file.read_text(encoding="utf-8")) == {
        "namespace": "test",
        "id": "test_mod",
        "name": "Test Mod",
    }
