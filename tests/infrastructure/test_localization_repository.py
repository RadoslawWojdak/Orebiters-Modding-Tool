import json
from pathlib import Path

import pytest

from orebiters_modding_tool.domain.project import Project
from orebiters_modding_tool.infrastructure.localization_repository import LocalizationRepository


def test_save_and_load_localization(tmp_path: Path) -> None:
    """Verify that localization entries can be saved and loaded."""
    repository = LocalizationRepository(tmp_path)
    project = Project(namespace="test", mod_id="test_mod", name="Test Mod")

    localizations = {
        "config.clay.one": "Clay",
        "config.clay.few": "Clays",
        "config.clay.many": "Clay",
        "config.clay.hint": "A piece of clay.",
        "config.clay.description": "A useful crafting material.",
    }

    repository.save(project, "en", localizations)

    loaded_localizations = repository.load(project, "en")

    assert loaded_localizations == localizations


def test_load_all_loads_all_localizations(tmp_path: Path) -> None:
    """Verify that all project localizations can be loaded."""
    repository = LocalizationRepository(tmp_path)
    project = Project(namespace="test", mod_id="test_mod", name="Test Mod")

    english = {
        "config.clay.one": "Clay",
        "config.clay.few": "Clays",
        "config.clay.many": "Clay",
    }
    polish = {
        "config.clay.one": "Glina",
        "config.clay.few": "Gliny",
        "config.clay.many": "Glin",
    }

    repository.save(project, "en", english)
    repository.save(project, "pl", polish)

    loaded_localizations = repository.load_all(project)

    assert loaded_localizations == {
        "en": english,
        "pl": polish,
    }


def test_load_all_returns_empty_dict_when_localization_directory_does_not_exist(
    tmp_path: Path,
) -> None:
    """Return an empty dictionary when the localization directory does not exist."""
    repository = LocalizationRepository(tmp_path)
    project = Project(namespace="test", mod_id="test_mod", name="Test Mod")

    assert repository.load_all(project) == {}


def test_list_languages_returns_sorted_languages(tmp_path: Path) -> None:
    """Return localization languages in sorted order."""
    repository = LocalizationRepository(tmp_path)
    project = Project(namespace="test", mod_id="test_mod", name="Test Mod")

    repository.save(project, "es", {})
    repository.save(project, "pl", {})
    repository.save(project, "en", {})

    assert repository.list_languages(project) == ["en", "es", "pl"]


def test_list_languages_returns_empty_list_when_localization_directory_does_not_exist(
    tmp_path: Path,
) -> None:
    """Return an empty list when the localization directory does not exist."""
    repository = LocalizationRepository(tmp_path)
    project = Project(namespace="test", mod_id="test_mod", name="Test Mod")

    assert repository.list_languages(project) == []


def test_save_all_saves_localizations_for_all_languages(tmp_path: Path) -> None:
    """Save localization entries for all provided languages."""
    repository = LocalizationRepository(tmp_path)
    project = Project(namespace="test", mod_id="test_mod", name="Test Mod")

    localization_data = {
        "en": {
            "config.clay.one": "Clay",
            "config.clay.description": "A useful crafting material.",
        },
        "pl": {
            "config.clay.one": "Glina",
            "config.clay.description": "Przydatny materiał rzemieślniczy.",
        },
    }

    repository.save_all(project, localization_data)

    assert repository.load_all(project) == localization_data


def test_delete_removes_localization(tmp_path: Path) -> None:
    """Remove localization entries for a language."""
    repository = LocalizationRepository(tmp_path)
    project = Project(namespace="test", mod_id="test_mod", name="Test Mod")

    repository.save(project, "en", {"config.clay.one": "Clay"})

    repository.delete(project, "en")

    assert repository.list_languages(project) == []


def test_save_overwrites_existing_localization(tmp_path: Path) -> None:
    """Overwrite existing localization entries when saving again."""
    repository = LocalizationRepository(tmp_path)
    project = Project(namespace="test", mod_id="test_mod", name="Test Mod")

    repository.save(
        project,
        "en",
        {
            "config.clay.one": "Clay",
        },
    )

    updated_localizations = {
        "config.clay.one": "Updated Clay",
        "config.clay.description": "Updated description.",
    }

    repository.save(project, "en", updated_localizations)

    assert repository.load(project, "en") == updated_localizations


def test_load_raises_for_json_value_that_is_not_an_object(tmp_path: Path) -> None:
    """Raise an error when a localization file does not contain an object."""
    repository = LocalizationRepository(tmp_path)
    project = Project(namespace="test", mod_id="test_mod", name="Test Mod")

    localization_file = tmp_path / project.qualified_id / "localization" / "en.json"
    localization_file.parent.mkdir(parents=True)
    localization_file.write_text(json.dumps(["Clay", "Stone"]), encoding="utf-8")

    with pytest.raises(ValueError, match="Localization file must contain a JSON object:"):
        repository.load(project, "en")


def test_load_raises_for_non_string_localization_keys_or_values(tmp_path: Path) -> None:
    """Raise an error when localization keys or values are not strings."""
    repository = LocalizationRepository(tmp_path)
    project = Project(namespace="test", mod_id="test_mod", name="Test Mod")

    localization_file = tmp_path / project.qualified_id / "localization" / "en.json"
    localization_file.parent.mkdir(parents=True)
    localization_file.write_text(
        json.dumps(
            {
                "config.clay.one": "Clay",
                "config.clay.amount": 123,
            },
        ),
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="Localization file must contain string keys and values:"):
        repository.load(project, "en")
