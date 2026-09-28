from orebiters_modding_tool.app.editors.content.content_localization_editor_widget import (
    ContentLocalizationEditorWidget,
)
from orebiters_modding_tool.app.editors.editor_field import EditorField, EditorVariantField
from orebiters_modding_tool.domain.item import ItemLocalization


class ItemLocalizationEditorWidget(ContentLocalizationEditorWidget[ItemLocalization]):
    """Editor for item localization."""

    FIELDS: tuple[EditorField | EditorVariantField, ...] = (
        *ContentLocalizationEditorWidget.FIELDS,
        EditorField(name="hint", label="Hint"),
        EditorField(name="description", label="Description"),
    )
