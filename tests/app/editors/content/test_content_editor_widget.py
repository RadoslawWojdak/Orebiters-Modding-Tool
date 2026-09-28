from unittest.mock import Mock

import pytest
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication, QLabel

from orebiters_modding_tool.app.editors.content.content_editor_widget import ContentEditorWidget
from orebiters_modding_tool.app.editors.editor_field import EditorField
from orebiters_modding_tool.domain.content import Content, ContentType


class SampleContent(Content):
    """Content used for testing."""


class QualifiedIdEditorWidget(ContentEditorWidget):
    """Editor used for testing qualified ID."""

    FIELDS = (
        EditorField(
            name="qualified_id",
            label="Qualified ID:",
            read_only=True,
            value_provider=ContentEditorWidget._get_qualified_id,
        ),
    )


class UnregisteredEditorWidget(ContentEditorWidget):
    """Editor used for testing unregistered editor."""


@pytest.fixture
def isolated_registry(monkeypatch: pytest.MonkeyPatch) -> dict:
    """Provide an isolated editor registry."""
    registry: dict = {}
    monkeypatch.setattr(ContentEditorWidget, "_registry", registry)
    return registry


# =========================================================================
# Tests
# =========================================================================


def create_editor_class(content_type: ContentType) -> type[ContentEditorWidget]:
    """Create an editor class registered for the given content type."""

    class RegisteredEditorWidget(ContentEditorWidget[SampleContent]):
        """Editor used for registry tests."""

        CONTENT_TYPE = content_type

    return RegisteredEditorWidget


def test_displays_qualified_id(qapp: QApplication) -> None:
    """Display the qualified ID provided by the content."""
    content = Mock()
    content.get_qualified_id.return_value = "example.mod.example_type.example_id"

    editor = QualifiedIdEditorWidget(content, context={"mod_id": "example.mod"})

    qualified_id_widget = editor._get_field_widget("qualified_id")

    assert isinstance(qualified_id_widget, QLabel)
    assert qualified_id_widget.text() == "example.mod.example_type.example_id"


def test_get_qualified_id_raises_when_mod_id_is_not_string(qapp: QApplication) -> None:
    """Raise an error when the mod ID is not a string."""
    content = Mock()

    with pytest.raises(TypeError, match="Context value 'mod_id' must be a string."):
        QualifiedIdEditorWidget(content, context={"mod_id": 123})


def test_read_only_keeps_qualified_id_selectable(qapp: QApplication) -> None:
    """Allow selecting the qualified ID in read-only mode."""
    content = Mock()
    content.get_qualified_id.return_value = "example.mod.example_type.example_id"

    editor = QualifiedIdEditorWidget(content, context={"mod_id": "example.mod"}, read_only=True)

    field = editor._get_field_widget("qualified_id")

    assert isinstance(field, QLabel)
    assert field.textInteractionFlags() == Qt.TextInteractionFlag.TextSelectableByMouse


def test_registers_editor_subclass_by_content_type(
    qapp: QApplication,
    isolated_registry: dict,
) -> None:
    """Register a concrete editor subclass for its content type."""
    content_type = next(iter(ContentType))

    class RegisteredEditorWidget(ContentEditorWidget[SampleContent]):
        CONTENT_TYPE = content_type

    assert isolated_registry[content_type] is RegisteredEditorWidget


def test_get_class_returns_registered_editor(qapp: QApplication, isolated_registry: dict) -> None:
    """Return the editor registered for a content type."""
    content_type = next(iter(ContentType))

    class RegisteredEditorWidget(ContentEditorWidget[SampleContent]):
        CONTENT_TYPE = content_type

    assert ContentEditorWidget.get_class(content_type) is RegisteredEditorWidget


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
    assert UnregisteredEditorWidget not in isolated_registry.values()


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
