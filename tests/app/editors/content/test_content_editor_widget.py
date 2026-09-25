import pytest
from PySide6.QtWidgets import QApplication

from orebiters_modding_tool.app.editors.content.content_editor_widget import ContentEditorWidget
from orebiters_modding_tool.domain.content import Content, ContentType


class SampleContent(Content):
    """Content used for testing."""


@pytest.fixture
def isolated_registry(monkeypatch: pytest.MonkeyPatch) -> dict:
    """Provide an isolated editor registry."""
    registry: dict = {}
    monkeypatch.setattr(ContentEditorWidget, "_registry", registry)
    return registry


def test_registers_editor_subclass_by_content_type(
    qapp: QApplication,
    isolated_registry: dict,
) -> None:
    """Register a concrete editor subclass for its content type."""
    content_type = next(iter(ContentType))

    class SampleEditor(ContentEditorWidget[SampleContent]):
        CONTENT_TYPE = content_type

    assert isolated_registry[content_type] is SampleEditor


def test_get_class_returns_registered_editor(qapp: QApplication, isolated_registry: dict) -> None:
    """Return the editor registered for a content type."""
    content_type = next(iter(ContentType))

    class SampleEditor(ContentEditorWidget[SampleContent]):
        CONTENT_TYPE = content_type

    assert ContentEditorWidget.get_class(content_type) is SampleEditor


def test_get_class_raises_for_unregistered_content_type(
    qapp: QApplication,
    isolated_registry: dict,
) -> None:
    """Raise KeyError when no editor is registered for a content type."""
    content_type = next(iter(ContentType))

    with pytest.raises(KeyError):
        ContentEditorWidget.get_class(content_type)


def test_editor_without_content_type_is_not_registered(
    qapp: QApplication,
    isolated_registry: dict,
) -> None:
    """Do not register an editor that does not define a content type."""

    class SampleEditor(ContentEditorWidget[SampleContent]):
        """Editor without a content type."""

    assert SampleEditor not in isolated_registry.values()


def test_subclass_without_own_content_type_does_not_reuse_parent_registration(
    qapp: QApplication,
    isolated_registry: dict,
) -> None:
    """Only a class defining its own content type is registered."""
    content_type = next(iter(ContentType))

    class ParentEditor(ContentEditorWidget[SampleContent]):
        """Parent editor used for testing."""

        CONTENT_TYPE = content_type

    class ChildEditor(ParentEditor):
        """Child editor without its own content type."""

    assert isolated_registry[content_type] is ParentEditor
    assert ChildEditor not in isolated_registry.values()


def test_rejects_duplicate_editor_for_content_type(
    qapp: QApplication,
    isolated_registry: dict,
) -> None:
    """Reject multiple editors registered for the same content type."""
    content_type = next(iter(ContentType))

    class FirstEditor(ContentEditorWidget[SampleContent]):
        """First editor for the content type."""

        CONTENT_TYPE = content_type

    with pytest.raises(
        ValueError,
        match=f"Editor for content type '{content_type}' is already registered",
    ):

        class SecondEditor(ContentEditorWidget[SampleContent]):
            """Second editor for the same content type."""

            CONTENT_TYPE = content_type

    assert isolated_registry[content_type] is FirstEditor
